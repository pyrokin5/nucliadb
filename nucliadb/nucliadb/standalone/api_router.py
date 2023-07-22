# Copyright (C) 2021 Bosutech XXI S.L.
#
# nucliadb is offered under the AGPL v3.0 and as commercial software.
# For commercial licensing, contact us at info@nuclia.com.
#
# AGPL:
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import functools
import inspect
import logging
from socket import gethostname

import pydantic
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from fastapi_versioning import version

from nucliadb.common.cluster import manager
from nucliadb.common.cluster.standalone import grpc_node_binding
from nucliadb.common.cluster.standalone.index_node import StandaloneIndexNode
from nucliadb.common.cluster.utils import get_shard_manager as get_shard_manager
from nucliadb.common.http_clients.processing import ProcessingHTTPClient
from nucliadb.standalone.utils import get_standalone_node_id
from nucliadb_models.resource import NucliaDBRoles
from nucliadb_utils.authentication import requires
from nucliadb_utils.settings import nuclia_settings

from .settings import Settings

logger = logging.getLogger(__name__)

standalone_api_router = APIRouter()


@standalone_api_router.get("/config-check")
@version(1)
@requires(NucliaDBRoles.READER)
async def api_config_check(request: Request):
    valid_nua_key = False
    nua_key_check_error = None
    if nuclia_settings.nuclia_service_account is not None:
        async with ProcessingHTTPClient() as processing_client:
            try:
                await processing_client.status()
                valid_nua_key = True
            except Exception as exc:
                logger.warning(f"Error validating nua key", exc_info=exc)
                nua_key_check_error = f"Error checking NUA key: {str(exc)}"
    return JSONResponse(
        {
            "nua_api_key": {
                "has_key": nuclia_settings.nuclia_service_account is not None,
                "valid": valid_nua_key,
                "error": nua_key_check_error,
            },
            "user": {
                "username": request.user.display_name,
                "roles": request.auth.scopes,
            },
        },
    )


class ClusterNode(pydantic.BaseModel):
    id: str
    address: str
    shard_count: int


class ClusterInfo(pydantic.BaseModel):
    nodes: list[ClusterNode]


_SELF_INDEX_NODE = None


def get_self(settings: Settings) -> StandaloneIndexNode:
    global _SELF_INDEX_NODE
    if _SELF_INDEX_NODE is None:
        _SELF_INDEX_NODE = StandaloneIndexNode(
            id=get_standalone_node_id(),
            address=f"{gethostname()}:{settings.http_port}",
            shard_count=0,
        )
    return _SELF_INDEX_NODE


@standalone_api_router.get("/cluster/nodes")
@version(1)
@requires(NucliaDBRoles.MANAGER)
async def cluster_info(request: Request) -> ClusterInfo:
    node_info = []
    for node in manager.get_index_nodes():
        node_info.append(
            ClusterNode(id=node.id, address=node.address, shard_count=node.shard_count)
        )

    return ClusterInfo(nodes=node_info)


@standalone_api_router.get("/cluster/self/info")
@version(1)
@requires(NucliaDBRoles.MANAGER)
async def current_node_info(request: Request):
    index_node = get_self(request.app.settings)
    return {
        "id": index_node.id,
        "address": index_node.address,
        "shard_count": index_node.shard_count,
    }


@standalone_api_router.post("/cluster/self/rpc/{service}/{action}")
@version(1)
@requires(NucliaDBRoles.MANAGER)
async def node_action(request: Request, service: str, action: str) -> bytes:
    index_node = get_self(request.app.settings)
    payload = await request.body()
    if service == "reader":
        method = getattr(index_node.reader, action)
    elif service == "writer":
        method = getattr(index_node.writer, action)
    else:
        method = getattr(index_node.sidecar, action)

    sig = inspect.signature(method.__func__)
    request_type = getattr(grpc_node_binding, sig.parameters["request"].annotation)

    request = request_type()
    request.ParseFromString(payload)
    response = await method(request)
    return Response(
        content=response.SerializeToString(), media_type="application/octet-stream"
    )
