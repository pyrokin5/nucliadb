// Copyright (C) 2021 Bosutech XXI S.L.
//
// nucliadb is offered under the AGPL v3.0 and as commercial software.
// For commercial licensing, contact us at info@nuclia.com.
//
// AGPL:
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program. If not, see <http://www.gnu.org/licenses/>.
//

use std::sync::Arc;

use nucliadb_core::protos::node_writer_server::NodeWriter;
use nucliadb_core::protos::{
    op_status, DeleteGraphNodes, EmptyQuery, EmptyResponse, NewShardRequest, NewVectorSetRequest,
    NodeMetadata, OpStatus, Resource, ResourceId, SetGraph, ShardCleaned, ShardCreated, ShardId,
    ShardIds, VectorSetId, VectorSetList,
};
use nucliadb_core::tracing::{self, *};
use nucliadb_core::NodeResult;
use nucliadb_telemetry::payload::TelemetryEvent;
use nucliadb_telemetry::sync::send_telemetry_event;
use tokio::sync::mpsc::UnboundedSender;
use tonic::{Request, Response, Status};

use crate::settings::Settings;
use crate::shards::errors::ShardNotFoundError;
use crate::shards::metadata::ShardMetadata;
use crate::shards::providers::unbounded_cache::AsyncUnboundedShardWriterCache;
use crate::shards::providers::AsyncShardWriterProvider;
use crate::shards::writer::ShardWriter;

pub struct NodeWriterGRPCDriver {
    shards: AsyncUnboundedShardWriterCache,
    sender: Option<UnboundedSender<NodeWriterEvent>>,
    settings: Arc<Settings>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum NodeWriterEvent {
    ShardCreation,
    ShardDeletion,
}

impl NodeWriterGRPCDriver {
    pub fn new(settings: Arc<Settings>) -> Self {
        Self {
            shards: AsyncUnboundedShardWriterCache::new(settings.shards_path()),
            sender: None,
            settings,
        }
    }

    /// This function must be called before using this service
    pub async fn initialize(&self) -> NodeResult<()> {
        if !self.settings.lazy_loading() {
            // If lazy loading is disabled, load
            self.shards.load_all().await?
        }
        Ok(())
    }

    pub fn with_sender(self, sender: UnboundedSender<NodeWriterEvent>) -> Self {
        Self {
            sender: Some(sender),
            ..self
        }
    }

    async fn obtain_shard(&self, id: impl Into<String>) -> Result<Arc<ShardWriter>, tonic::Status> {
        let id = id.into();

        // NOTE: Taking into account we use an unbounded shard cache, we only request
        // loading a shard into memory when lazy loading is enabled. Otherwise,
        // we rely on all shards (stored on disk) been brought to memory before
        // the driver is online on `initialize`.
        if self.settings.lazy_loading() {
            self.shards.load(id.clone()).await.map_err(|error| {
                if error.is::<ShardNotFoundError>() {
                    tonic::Status::not_found(error.to_string())
                } else {
                    tonic::Status::internal(format!("Error lazy loading shard {id}: {error:?}"))
                }
            })?;
        }

        match self.shards.get(id.clone()).await {
            Some(shard) => Ok(shard),
            None => Err(tonic::Status::not_found(format!(
                "Error loading shard {id}: shard not found"
            ))),
        }
    }

    #[tracing::instrument(skip_all)]
    fn emit_event(&self, event: NodeWriterEvent) {
        if let Some(sender) = &self.sender {
            let _ = sender.send(event);
        }
    }
}

#[tonic::async_trait]
impl NodeWriter for NodeWriterGRPCDriver {
    async fn new_shard(
        &self,
        request: Request<NewShardRequest>,
    ) -> Result<Response<ShardCreated>, Status> {
        send_telemetry_event(TelemetryEvent::Create).await;
        let request = request.into_inner();
        let metadata = ShardMetadata::from(request);
        let new_shard = self.shards.create(metadata).await;
        match new_shard {
            Ok(new_shard) => {
                self.emit_event(NodeWriterEvent::ShardCreation);
                Ok(tonic::Response::new(ShardCreated {
                    id: new_shard.id.clone(),
                    document_service: new_shard.document_version() as i32,
                    paragraph_service: new_shard.paragraph_version() as i32,
                    vector_service: new_shard.vector_version() as i32,
                    relation_service: new_shard.relation_version() as i32,
                }))
            }
            Err(error) => Err(tonic::Status::internal(error.to_string())),
        }
    }

    async fn delete_shard(&self, request: Request<ShardId>) -> Result<Response<ShardId>, Status> {
        send_telemetry_event(TelemetryEvent::Delete).await;
        // Deletion does not require for the shard to be loaded.
        let shard_id = request.into_inner();
        let deleted = self.shards.delete(shard_id.id.clone()).await;
        match deleted {
            Ok(_) => {
                self.emit_event(NodeWriterEvent::ShardDeletion);
                Ok(tonic::Response::new(shard_id))
            }
            Err(e) => {
                let error_msg = format!("Error deleting shard {:?}: {}", shard_id, e);
                error!("{}", error_msg);
                Err(tonic::Status::internal(error_msg))
            }
        }
    }

    async fn clean_and_upgrade_shard(
        &self,
        request: Request<ShardId>,
    ) -> Result<Response<ShardCleaned>, Status> {
        let shard_id = request.into_inner().id;
        // No need to load shard to upgrade it
        match self.shards.upgrade(shard_id).await {
            Ok(upgrade_details) => Ok(tonic::Response::new(upgrade_details)),
            Err(error) => Err(tonic::Status::internal(error.to_string())),
        }
    }

    async fn list_shards(
        &self,
        _request: Request<EmptyQuery>,
    ) -> Result<Response<ShardIds>, Status> {
        let shard_ids = self
            .shards
            .list_loaded_ids()
            .await
            .into_iter()
            .map(|shard_id| ShardId { id: shard_id })
            .collect();
        Ok(tonic::Response::new(ShardIds { ids: shard_ids }))
    }

    // Incremental call that can be call multiple times for the same resource
    async fn set_resource(&self, request: Request<Resource>) -> Result<Response<OpStatus>, Status> {
        let resource = request.into_inner();
        let shard_id = resource.shard_id.clone();
        let shard = self.obtain_shard(&shard_id).await?;
        let status = tokio::task::spawn_blocking(move || {
            shard
                .set_resource(&resource)
                .and_then(|()| shard.get_opstatus())
        })
        .await
        .map_err(|error| tonic::Status::internal(format!("Blocking task panicked: {error:?}")))?;
        match status {
            Ok(mut status) => {
                status.status = 0;
                status.detail = "Success!".to_string();
                Ok(tonic::Response::new(status))
            }
            Err(error) => {
                let status = OpStatus {
                    status: op_status::Status::Error as i32,
                    detail: error.to_string(),
                    field_count: 0_u64,
                    shard_id,
                    ..Default::default()
                };
                Ok(tonic::Response::new(status))
            }
        }
    }

    async fn remove_resource(
        &self,
        request: Request<ResourceId>,
    ) -> Result<Response<OpStatus>, Status> {
        let resource = request.into_inner();
        let shard_id = resource.shard_id.clone();
        let shard = self.obtain_shard(&shard_id).await?;
        let status = tokio::task::spawn_blocking(move || {
            shard
                .remove_resource(&resource)
                .and_then(|()| shard.get_opstatus())
        })
        .await
        .map_err(|error| tonic::Status::internal(format!("Blocking task panicked: {error:?}")))?;
        match status {
            Ok(mut status) => {
                status.status = 0;
                status.detail = "Success!".to_string();
                Ok(tonic::Response::new(status))
            }
            Err(error) => {
                let status = OpStatus {
                    status: op_status::Status::Error as i32,
                    detail: error.to_string(),
                    field_count: 0_u64,
                    shard_id,
                    ..Default::default()
                };
                Ok(tonic::Response::new(status))
            }
        }
    }

    async fn join_graph(&self, request: Request<SetGraph>) -> Result<Response<OpStatus>, Status> {
        let request = request.into_inner();
        let shard_id = match request.shard_id {
            Some(ref shard_id) => &shard_id.id,
            None => return Err(tonic::Status::invalid_argument("Shard ID must be provided")),
        };
        let graph = match request.graph {
            Some(graph) => graph,
            None => return Err(tonic::Status::invalid_argument("Shard ID must be provided")),
        };
        let shard = self.obtain_shard(shard_id).await?;
        let status = tokio::task::spawn_blocking(move || {
            shard
                .join_relations_graph(&graph)
                .and_then(|()| shard.get_opstatus())
        })
        .await
        .map_err(|error| tonic::Status::internal(format!("Blocking task panicked: {error:?}")))?;
        match status {
            Ok(mut status) => {
                status.status = 0;
                status.detail = "Success!".to_string();
                Ok(tonic::Response::new(status))
            }
            Err(error) => Err(tonic::Status::internal(error.to_string())),
        }
    }

    async fn delete_relation_nodes(
        &self,
        request: Request<DeleteGraphNodes>,
    ) -> Result<Response<OpStatus>, Status> {
        let request = request.into_inner();
        let shard_id = match request.shard_id {
            Some(ref shard_id) => &shard_id.id,
            None => return Err(tonic::Status::invalid_argument("Shard ID must be provided")),
        };
        let shard = self.obtain_shard(shard_id).await?;
        let status = tokio::task::spawn_blocking(move || {
            shard
                .delete_relation_nodes(&request)
                .and_then(|()| shard.get_opstatus())
        })
        .await
        .map_err(|error| tonic::Status::internal(format!("Blocking task panicked: {error:?}")))?;
        match status {
            Ok(mut status) => {
                status.status = 0;
                status.detail = "Success!".to_string();
                Ok(tonic::Response::new(status))
            }
            Err(error) => Err(tonic::Status::internal(error.to_string())),
        }
    }

    async fn add_vector_set(
        &self,
        request: Request<NewVectorSetRequest>,
    ) -> Result<Response<OpStatus>, Status> {
        let request = request.into_inner();
        let vectorset_id = match request.id {
            Some(ref vectorset_id) => vectorset_id.clone(),
            None => {
                return Err(tonic::Status::invalid_argument(
                    "Vectorset ID must be provided",
                ))
            }
        };
        let shard_id = match vectorset_id.shard {
            Some(ref shard_id) => &shard_id.id,
            None => return Err(tonic::Status::invalid_argument("Shard ID must be provided")),
        };

        let shard = self.obtain_shard(shard_id).await?;
        let status = tokio::task::spawn_blocking(move || {
            shard
                .add_vectorset(&vectorset_id, request.similarity())
                .and_then(|()| shard.get_opstatus())
        })
        .await
        .map_err(|error| tonic::Status::internal(format!("Blocking task panicked: {error:?}")))?;
        match status {
            Ok(mut status) => {
                status.status = 0;
                status.detail = "Success!".to_string();
                Ok(tonic::Response::new(status))
            }
            Err(error) => Err(tonic::Status::internal(error.to_string())),
        }
    }

    async fn remove_vector_set(
        &self,
        request: Request<VectorSetId>,
    ) -> Result<Response<OpStatus>, Status> {
        let request = request.into_inner();
        let shard_id = match request.shard {
            Some(ref shard_id) => &shard_id.id,
            None => return Err(tonic::Status::invalid_argument("Shard ID must be provided")),
        };
        let shard = self.obtain_shard(shard_id).await?;
        let status = tokio::task::spawn_blocking(move || {
            shard
                .remove_vectorset(&request)
                .and_then(|()| shard.get_opstatus())
        })
        .await
        .map_err(|error| tonic::Status::internal(format!("Blocking task panicked: {error:?}")))?;
        match status {
            Ok(mut status) => {
                status.status = 0;
                status.detail = "Success!".to_string();
                Ok(tonic::Response::new(status))
            }
            Err(error) => Err(tonic::Status::internal(error.to_string())),
        }
    }

    async fn list_vector_sets(
        &self,
        request: Request<ShardId>,
    ) -> Result<Response<VectorSetList>, Status> {
        let shard_id = request.into_inner();
        let shard = self.obtain_shard(shard_id.id.clone()).await?;
        let vector_sets = tokio::task::spawn_blocking(move || shard.list_vectorsets())
            .await
            .map_err(|error| {
                tonic::Status::internal(format!("Blocking task panicked: {error:?}"))
            })?;
        match vector_sets {
            Ok(vector_sets) => {
                let list = VectorSetList {
                    shard: Some(shard_id),
                    vectorset: vector_sets,
                };
                Ok(tonic::Response::new(list))
            }
            Err(error) => Err(tonic::Status::internal(error.to_string())),
        }
    }

    async fn get_metadata(
        &self,
        _request: Request<EmptyQuery>,
    ) -> Result<Response<NodeMetadata>, Status> {
        let metadata_path = self.settings.metadata_path();
        let metadata = tokio::task::spawn_blocking(move || {
            crate::node_metadata::NodeMetadata::load(&metadata_path)
        })
        .await
        .map_err(|error| tonic::Status::internal(format!("Blocking task panicked: {error:?}")))?;
        match metadata {
            Ok(metadata) => Ok(tonic::Response::new(metadata.into())),
            Err(error) => Err(tonic::Status::internal(error.to_string())),
        }
    }

    async fn gc(&self, request: Request<ShardId>) -> Result<Response<EmptyResponse>, Status> {
        send_telemetry_event(TelemetryEvent::GarbageCollect).await;
        let shard_id = request.into_inner();
        let shard = self.obtain_shard(&shard_id.id).await?;
        let result = tokio::task::spawn_blocking(move || shard.gc())
            .await
            .map_err(|error| {
                tonic::Status::internal(format!("Blocking task panicked: {error:?}"))
            })?;
        match result {
            Ok(()) => Ok(tonic::Response::new(EmptyResponse {})),
            Err(error) => Err(tonic::Status::internal(error.to_string())),
        }
    }
}
