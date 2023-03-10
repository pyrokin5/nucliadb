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

import asyncio
import base64
import json
from datetime import datetime
from unittest import mock
from uuid import uuid4

import pytest
from httpx import AsyncClient
from nucliadb_protos.resources_pb2 import (
    CloudFile,
    Entity,
    ExtractedTextWrapper,
    ExtractedVectorsWrapper,
    FieldType,
    FileExtractedData,
    Keyword,
    LargeComputedMetadataWrapper,
    LinkExtractedData,
    UserVector,
    UserVectorsWrapper,
)
from nucliadb_protos.utils_pb2 import Vector, VectorObject
from nucliadb_protos.writer_pb2 import (
    BinaryData,
    BrokerMessage,
    CreateShadowShardRequest,
    DeleteShadowShardRequest,
    ExportRequest,
    FileRequest,
    IndexResource,
    ListMembersRequest,
    Member,
    OpStatusWriter,
    SetVectorsRequest,
)
from nucliadb_protos.writer_pb2 import Shards as PBShards
from nucliadb_protos.writer_pb2 import UploadBinaryData

from nucliadb.ingest import SERVICE_NAME
from nucliadb.ingest.fields.base import FIELD_VECTORS
from nucliadb.ingest.orm import NODES
from nucliadb.ingest.orm.node import Node
from nucliadb.ingest.tests.fixtures import IngestFixture
from nucliadb.ingest.utils import get_driver
from nucliadb_protos import knowledgebox_pb2, utils_pb2, writer_pb2, writer_pb2_grpc
from nucliadb_telemetry.settings import telemetry_settings
from nucliadb_telemetry.utils import get_telemetry, init_telemetry
from nucliadb_utils.cache import KB_COUNTER_CACHE
from nucliadb_utils.keys import KB_SHARDS
from nucliadb_utils.utilities import get_cache, get_storage


@pytest.mark.asyncio
async def test_clean_and_upgrade_kb_index(grpc_servicer: IngestFixture):
    stub = writer_pb2_grpc.WriterStub(grpc_servicer.channel)

    kb_id = str(uuid4())
    pb = knowledgebox_pb2.KnowledgeBoxNew(slug="test", forceuuid=kb_id)
    pb.config.title = "My Title"
    result = await stub.NewKnowledgeBox(pb)  # type: ignore
    assert result.status == knowledgebox_pb2.KnowledgeBoxResponseStatus.OK

    req = knowledgebox_pb2.KnowledgeBoxID(uuid=kb_id)
    result = await stub.CleanAndUpgradeKnowledgeBoxIndex(req)  # type: ignore


@pytest.mark.asyncio
async def test_create_entities_group(grpc_servicer: IngestFixture):
    stub = writer_pb2_grpc.WriterStub(grpc_servicer.channel)

    kb_id = str(uuid4())
    pb = knowledgebox_pb2.KnowledgeBoxNew(slug="test", forceuuid=kb_id)
    pb.config.title = "My Title"
    result = await stub.NewKnowledgeBox(pb)  # type: ignore
    assert result.status == knowledgebox_pb2.KnowledgeBoxResponseStatus.OK

    pb_ser = writer_pb2.SetEntitiesRequest(
        kb=knowledgebox_pb2.KnowledgeBoxID(uuid=kb_id, slug="test"),
        group="0",
        entities=knowledgebox_pb2.EntitiesGroup(
            title="zero",
            color="#fff",
            custom=True,
            entities={
                "ent1": knowledgebox_pb2.Entity(value="1", merged=True, represents=[])
            },
        ),
    )
    result = await stub.SetEntities(pb_ser)  # type: ignore
    assert result.status == knowledgebox_pb2.KnowledgeBoxResponseStatus.OK

    pb_ger = writer_pb2.GetEntitiesRequest(
        kb=knowledgebox_pb2.KnowledgeBoxID(uuid=kb_id, slug="test"),
    )
    result = await stub.GetEntities(pb_ger)  # type: ignore


@pytest.mark.asyncio
async def test_list_members(grpc_servicer: IngestFixture):
    stub = writer_pb2_grpc.WriterStub(grpc_servicer.channel)

    response = await stub.ListMembers(ListMembersRequest())  # type: ignore

    for member in response.members:
        assert member.type == Member.Type.IO
        assert isinstance(member.load_score, float)
        assert isinstance(member.shard_count, int)


@pytest.mark.asyncio
async def test_process_message_clears_counters_cache(grpc_servicer: IngestFixture):
    stub = writer_pb2_grpc.WriterStub(grpc_servicer.channel)

    # Create a new KB
    pb = knowledgebox_pb2.KnowledgeBoxNew(slug="test")
    pb.config.title = "My Title"
    result: knowledgebox_pb2.NewKnowledgeBoxResponse = await stub.NewKnowledgeBox(pb)  # type: ignore
    assert result.status == knowledgebox_pb2.KnowledgeBoxResponseStatus.OK
    kbid = result.uuid

    # Set some values in the KB counters cache
    cache = await get_cache()
    assert cache is not None
    kb_counters_key = KB_COUNTER_CACHE.format(kbid=kbid)
    await cache.set(
        kb_counters_key,
        json.dumps(
            {
                "resources": 100,
                "paragraphs": 100,
                "fields": 100,
                "sentences": 100,
                "shards": [],
            }
        ),
    )
    assert await cache.get(kb_counters_key)

    # Create a BM to process
    bm = BrokerMessage()
    bm.uuid = "test1"
    bm.slug = bm.basic.slug = "slugtest"
    bm.kbid = kbid
    bm.texts["text1"].body = "My text1"

    # Check that the cache is currently empty
    resp = await stub.ProcessMessage([bm])  # type: ignore
    assert resp.status == OpStatusWriter.Status.OK

    # Check that KB counters cache is empty
    assert await cache.get(kb_counters_key) is None


@pytest.mark.asyncio
async def test_reindex_resource(grpc_servicer, fake_node):
    stub = writer_pb2_grpc.WriterStub(grpc_servicer.channel)

    # Create a kb
    kb_id = str(uuid4())
    pb = knowledgebox_pb2.KnowledgeBoxNew(slug="test", forceuuid=kb_id)
    pb.config.title = "My Title"
    result = await stub.NewKnowledgeBox(pb)
    assert result.status == knowledgebox_pb2.KnowledgeBoxResponseStatus.OK

    # Create a resource with a field and some vectors
    bm = BrokerMessage()
    rid = "test1"
    field_id = "text1"
    field_type = FieldType.TEXT
    bm.uuid = rid
    bm.kbid = result.uuid
    bm.texts[field_id].body = "My text1"

    evw = ExtractedVectorsWrapper()
    vec = Vector()
    vec.vector.extend([1.0, 1.0])
    evw.vectors.vectors.vectors.append(vec)
    evw.field.field = field_id
    evw.field.field_type = field_type
    bm.field_vectors.append(evw)

    await stub.ProcessMessage([bm])  # type: ignore

    # Reindex it along with its vectors
    req = IndexResource(kbid=kb_id, rid=rid, reindex_vectors=True)
    result = await stub.ReIndex(req)


@pytest.mark.asyncio
async def test_set_vectors(grpc_servicer, gcs_storage):
    stub = writer_pb2_grpc.WriterStub(grpc_servicer.channel)

    # Create a kb
    kb_id = str(uuid4())
    pb = knowledgebox_pb2.KnowledgeBoxNew(slug="test", forceuuid=kb_id)
    pb.config.title = "My Title"
    result = await stub.NewKnowledgeBox(pb)
    assert result.status == knowledgebox_pb2.KnowledgeBoxResponseStatus.OK

    # Create a resource with a field
    bm = BrokerMessage()
    rid = "test1"
    field_id = "text1"
    field_type = FieldType.TEXT
    bm.uuid = rid
    bm.kbid = result.uuid
    bm.texts[field_id].body = "My text1"

    evw = ExtractedVectorsWrapper()
    vec = Vector()
    vec.vector.extend([1.0, 1.0])
    evw.vectors.vectors.vectors.append(vec)
    evw.field.field = field_id
    evw.field.field_type = field_type
    bm.field_vectors.append(evw)

    await stub.ProcessMessage([bm])  # type: ignore

    # Try to set vectors of a field
    req = SetVectorsRequest(kbid=kb_id, rid=rid)
    req.field.field_type = field_type
    req.field.field = field_id
    vector = Vector()
    vector.start = 10
    vector.end = 20
    vector.start_paragraph = 0
    vector.end_paragraph = 20
    vector.vector.extend([9.0, 9.0])
    req.vectors.vectors.vectors.append(vector)

    result = await stub.SetVectors(req)
    assert result.found is True

    # Check that vectors were updated at gcs storage
    sf = gcs_storage.file_extracted(kb_id, rid, "t", field_id, FIELD_VECTORS)
    vo = await gcs_storage.download_pb(sf, VectorObject)
    assert vo == req.vectors


class TestExport:
    @pytest.mark.asyncio
    async def test_export_resources(grpc_servicer: IngestFixture):
        stub = writer_pb2_grpc.WriterStub(grpc_servicer.channel)

        pb = knowledgebox_pb2.KnowledgeBoxNew(slug="test")
        pb.config.title = "My Title"
        result: knowledgebox_pb2.NewKnowledgeBoxResponse = await stub.NewKnowledgeBox(pb)  # type: ignore
        assert result.status == knowledgebox_pb2.KnowledgeBoxResponseStatus.OK

        bm = BrokerMessage()
        bm.uuid = "test1"
        bm.slug = bm.basic.slug = "slugtest"
        bm.kbid = result.uuid
        bm.texts["text1"].body = "My text1"
        bm.files["file1"].file.uri = "http://nofile"
        bm.files["file1"].file.size = 0
        bm.files["file1"].file.source = CloudFile.Source.LOCAL
        bm.links["link1"].uri = "http://nolink"
        bm.datetimes["date1"].value.FromDatetime(datetime.now())
        bm.keywordsets["key1"].keywords.append(Keyword(value="key1"))
        evw = ExtractedVectorsWrapper()
        vec = Vector()
        vec.vector.extend([1.0, 1.0])
        evw.vectors.vectors.vectors.append(vec)
        evw.field.field = "text1"
        evw.field.field_type = FieldType.TEXT
        bm.field_vectors.append(evw)

        etw = ExtractedTextWrapper()
        etw.body.text = "My text"
        etw.field.field = "text1"
        etw.field.field_type = FieldType.TEXT
        bm.extracted_text.append(etw)
        bm.basic.title = "My Title"

        lcmw = LargeComputedMetadataWrapper()
        lcmw.field.field = "text1"
        lcmw.field.field_type = FieldType.TEXT
        entity = Entity(token="token", root="root", type="type")
        lcmw.real.metadata.entities.append(entity)
        bm.field_large_metadata.append(lcmw)

        uvw = UserVectorsWrapper()
        uvw.field.field = "file1"
        uvw.field.field_type = FieldType.FILE
        uv = UserVector(vector=[1.0, 0.0], labels=["some", "labels"], start=1, end=2)
        uvw.vectors.vectors["vectorset1"].vectors["vect1"].CopyFrom(uv)
        bm.user_vectors.append(uvw)

        led = LinkExtractedData()
        led.metadata["foo"] = "bar"
        led.field = "link1"
        led.description = "My link is from wikipedia"
        led.title = "My Link"
        bm.link_extracted_data.append(led)

        fed = FileExtractedData()
        fed.language = "es"
        fed.metadata["foo"] = "bar"
        fed.icon = "image/png"
        fed.field = "file1"
        bm.file_extracted_data.append(fed)

        await stub.ProcessMessage([bm])  # type: ignore

        req = ExportRequest()
        req.kbid = result.uuid
        export: BrokerMessage
        found = False
        async for export in stub.Export(req):  # type: ignore
            assert found is False
            found = True
            assert export.basic.title == "My Title"
            assert export.slug == export.basic.slug == "slugtest"
            assert export.extracted_text[0].body.text == "My text"
            assert export.field_vectors == bm.field_vectors
            assert export.user_vectors == bm.user_vectors
            assert export.field_large_metadata == bm.field_large_metadata
            assert export.extracted_text == bm.extracted_text
            assert export.field_metadata == bm.field_metadata
            assert export.link_extracted_data == bm.link_extracted_data
            assert export.file_extracted_data == bm.file_extracted_data
        assert found

        index_req = IndexResource()
        index_req.kbid = result.uuid
        index_req.rid = "test1"
        assert await stub.ReIndex(index_req)  # type: ignore

    @pytest.mark.asyncio
    async def test_upload_download(grpc_servicer: IngestFixture):
        stub = writer_pb2_grpc.WriterStub(grpc_servicer.channel)

        # Create a KB
        pb = knowledgebox_pb2.KnowledgeBoxNew(slug="test")
        pb.config.title = "My Title"
        result: knowledgebox_pb2.NewKnowledgeBoxResponse = await stub.NewKnowledgeBox(pb)  # type: ignore
        assert result.status == knowledgebox_pb2.KnowledgeBoxResponseStatus.OK
        kbid = result.uuid

        # Upload a file to it
        metadata = UploadBinaryData(count=0)
        metadata.metadata.size = 1
        metadata.metadata.kbid = kbid
        metadata.metadata.key = f"{kbid}/some/key"

        binary = base64.b64encode(b"Hola")
        data = UploadBinaryData(count=1)
        data.payload = binary

        async def upload_iterator():
            yield metadata
            yield data

        await stub.UploadFile(upload_iterator())  # type: ignore

        # Now download the file
        file_req = FileRequest()
        storage = await get_storage(service_name=SERVICE_NAME)
        file_req.bucket = storage.get_bucket_name(kbid)
        file_req.key = metadata.metadata.key

        downloaded = b""
        bindata: BinaryData
        async for bindata in stub.DownloadFile(file_req):  # type: ignore
            downloaded += bindata.data
        assert downloaded == binary

    @pytest.mark.asyncio
    async def test_export_file(grpc_servicer: IngestFixture):
        stub = writer_pb2_grpc.WriterStub(grpc_servicer.channel)

        pb = knowledgebox_pb2.KnowledgeBoxNew(slug="test")
        pb.config.title = "My Title"
        result: knowledgebox_pb2.NewKnowledgeBoxResponse = await stub.NewKnowledgeBox(pb)  # type: ignore
        assert result.status == knowledgebox_pb2.KnowledgeBoxResponseStatus.OK
        kbid = result.uuid

        # Create an exported bm with a file
        bm = BrokerMessage()
        bm.uuid = "test1"
        bm.slug = bm.basic.slug = "slugtest"
        bm.kbid = kbid
        bm.texts["text1"].body = "My text1"
        bm.files["file1"].file.size = 0
        bm.files["file1"].file.source = CloudFile.Source.EXPORT
        bm.files["file1"].file.bucket_name = "bucket_from_exported_kb"
        bm.files["file1"].file.uri = "/kbs/exported_kb/r/test1/f/f/file1"

        await stub.ProcessMessage([bm])  # type: ignore

        # Check that file bucket and uri were replaced
        req = ExportRequest()
        req.kbid = result.uuid
        export: BrokerMessage
        found = False
        async for export in stub.Export(req):  # type: ignore
            assert found is False
            found = True
            assert export.files["file1"].file.uri.startswith(f"kbs/{kbid}")
            assert kbid in export.files["file1"].file.bucket_name
        assert found


async def get_kb_similarity(txn, kbid) -> utils_pb2.VectorSimilarity.ValueType:
    kb_shards_key = KB_SHARDS.format(kbid=kbid)
    kb_shards_binary = await txn.get(kb_shards_key)
    assert kb_shards_binary, "Shards object not found!"
    kb_shards = PBShards()
    kb_shards.ParseFromString(kb_shards_binary)
    return kb_shards.similarity


class TestKnowledgeBox:
    @pytest.mark.asyncio
    async def test_create_knowledgebox(
        set_telemetry_settings, grpc_servicer: IngestFixture
    ):
        tracer_provider = get_telemetry("GCS_SERVICE")
        assert tracer_provider is not None
        await init_telemetry(tracer_provider)

        stub = writer_pb2_grpc.WriterStub(grpc_servicer.channel)
        pb_prefix = knowledgebox_pb2.KnowledgeBoxPrefix(prefix="")

        count = 0
        async for _ in stub.ListKnowledgeBox(pb_prefix):  # type: ignore
            count += 1
        assert count == 0

        pb = knowledgebox_pb2.KnowledgeBoxNew(slug="test")
        pb.config.title = "My Title"
        result = await stub.NewKnowledgeBox(pb)  # type: ignore
        assert result.status == knowledgebox_pb2.KnowledgeBoxResponseStatus.OK

        pb = knowledgebox_pb2.KnowledgeBoxNew(
            slug="test",
        )
        pb.config.title = "My Title 2"
        result = await stub.NewKnowledgeBox(pb)  # type: ignore
        assert result.status == knowledgebox_pb2.KnowledgeBoxResponseStatus.CONFLICT

        pb = knowledgebox_pb2.KnowledgeBoxNew(slug="test2")
        result = await stub.NewKnowledgeBox(pb)  # type: ignore
        assert result.status == knowledgebox_pb2.KnowledgeBoxResponseStatus.OK

        pb_prefix = knowledgebox_pb2.KnowledgeBoxPrefix(prefix="test")
        slugs = []
        async for kpb in stub.ListKnowledgeBox(pb_prefix):  # type: ignore
            slugs.append(kpb.slug)

        assert "test" in slugs
        assert "test2" in slugs

        pbid = knowledgebox_pb2.KnowledgeBoxID(slug="test")
        result = await stub.DeleteKnowledgeBox(pbid)  # type: ignore

        await tracer_provider.async_force_flush()

        expected_spans = 6

        client = AsyncClient()
        for _ in range(10):
            resp = await client.get(
                f"http://localhost:{telemetry_settings.jaeger_query_port}/api/traces?service=GCS_SERVICE",
                headers={"Accept": "application/json"},
            )
            if resp.status_code != 200 or len(resp.json()["data"]) < expected_spans:
                await asyncio.sleep(2)
            else:
                break
        assert len(resp.json()["data"]) == expected_spans

    @pytest.mark.asyncio
    async def test_create_knowledgebox_with_similarity(
        grpc_servicer: IngestFixture, txn
    ):
        stub = writer_pb2_grpc.WriterStub(grpc_servicer.channel)

        pb = knowledgebox_pb2.KnowledgeBoxNew(slug="test-dot")
        pb.config.title = "My Title"
        pb.similarity = utils_pb2.VectorSimilarity.DOT
        result = await stub.NewKnowledgeBox(pb)  # type: ignore
        assert result.status == knowledgebox_pb2.KnowledgeBoxResponseStatus.OK

        assert (
            await get_kb_similarity(txn, result.uuid) == utils_pb2.VectorSimilarity.DOT
        )

    @pytest.mark.asyncio
    async def test_create_knowledgebox_defaults_to_cosine_similarity(
        grpc_servicer: IngestFixture,
        txn,
    ):
        stub = writer_pb2_grpc.WriterStub(grpc_servicer.channel)
        pb = knowledgebox_pb2.KnowledgeBoxNew(slug="test-default")
        pb.config.title = "My Title"
        result = await stub.NewKnowledgeBox(pb)  # type: ignore
        assert result.status == knowledgebox_pb2.KnowledgeBoxResponseStatus.OK

        assert (
            await get_kb_similarity(txn, result.uuid)
            == utils_pb2.VectorSimilarity.COSINE
        )

    @pytest.mark.asyncio
    async def test_get_resource_id(grpc_servicer: IngestFixture) -> None:
        stub = writer_pb2_grpc.WriterStub(grpc_servicer.channel)

        pb = knowledgebox_pb2.KnowledgeBoxNew(slug="test")
        pb.config.title = "My Title"
        result: knowledgebox_pb2.NewKnowledgeBoxResponse = await stub.NewKnowledgeBox(pb)  # type: ignore

        pbid = writer_pb2.ResourceIdRequest(kbid="foo", slug="bar")
        result = await stub.GetResourceId(pbid)  # type: ignore
        assert result.uuid == ""

    @pytest.mark.asyncio
    async def test_delete_knowledgebox_handles_unexisting_kb(
        grpc_servicer: IngestFixture,
    ) -> None:
        stub = writer_pb2_grpc.WriterStub(grpc_servicer.channel)

        pbid = knowledgebox_pb2.KnowledgeBoxID(slug="idonotexist")
        result = await stub.DeleteKnowledgeBox(pbid)  # type: ignore
        assert result.status == knowledgebox_pb2.KnowledgeBoxResponseStatus.OK

        pbid = knowledgebox_pb2.KnowledgeBoxID(uuid="idonotexist")
        result = await stub.DeleteKnowledgeBox(pbid)  # type: ignore
        assert result.status == knowledgebox_pb2.KnowledgeBoxResponseStatus.OK

        pbid = knowledgebox_pb2.KnowledgeBoxID(uuid="idonotexist", slug="meneither")
        result = await stub.DeleteKnowledgeBox(pbid)  # type: ignore
        assert result.status == knowledgebox_pb2.KnowledgeBoxResponseStatus.OK


class TestShardManagement:
    @pytest.mark.asyncio
    async def test_create_and_delete_shadow_shard(grpc_servicer, fake_node):
        stub = writer_pb2_grpc.WriterStub(grpc_servicer.channel)

        # Create a KB
        kbid = str(uuid4())
        pb = knowledgebox_pb2.KnowledgeBoxNew(slug="test", forceuuid=kbid)
        pb.config.title = "My Title"
        result = await stub.NewKnowledgeBox(pb)
        assert result.status == knowledgebox_pb2.KnowledgeBoxResponseStatus.OK

        # Get current shards object
        driver = await get_driver()
        txn = await driver.begin()
        shards_object = await Node.get_all_shards(txn, kbid)
        await txn.abort()
        assert shards_object

        replica1 = shards_object.shards[0].replicas[0]
        replica2 = shards_object.shards[0].replicas[1]
        # There should not be shadow replicas by default
        assert not replica1.HasField("shadow_replica")
        assert not replica2.HasField("shadow_replica")
        rep1_id, rep1_node = replica1.shard.id, replica1.node
        _, rep2_node = replica2.shard.id, replica2.node

        # Create a shadow shard of rep1 onto the other node
        req = CreateShadowShardRequest()
        req.kbid = kbid
        req.replica.id = replica1.shard.id
        req.node = rep2_node

        resp = await stub.CreateShadowShard(req)
        assert resp.success

        # Check that the shadow replica has been updated at the shard object
        txn = await driver.begin()
        shards_object = await Node.get_all_shards(txn, kbid)
        await txn.abort()

        found = False
        for shard in shards_object.shards:
            for replica in shard.replicas:
                if replica.shard.id == rep1_id and replica.node == rep1_node:
                    found = True
                    assert replica.HasField("shadow_replica")
                    assert replica.shadow_replica.shard.id
                    assert replica.shadow_replica.node == rep2_node
                else:
                    assert not replica.HasField("shadow_replica")
        assert found

        # Now delete it
        req = DeleteShadowShardRequest()
        req.kbid = kbid
        req.replica.id = replica1.shard.id
        resp = await stub.DeleteShadowShard(req)
        assert resp.success

        # Check that the shadow replica has been cleaned from the shard object
        txn = await driver.begin()
        shards_object = await Node.get_all_shards(txn, kbid)
        await txn.abort()

        found = False
        for shard in shards_object.shards:
            for replica in shard.replicas:
                if replica.shard.id == rep1_id and replica.node == rep1_node:
                    found = True
                    assert not replica.HasField("shadow_replica")
        assert found

    @pytest.mark.asyncio
    async def test_create_cleansup_on_error(grpc_servicer, fake_node):
        stub = writer_pb2_grpc.WriterStub(grpc_servicer.channel)
        # Create a KB
        kbid = str(uuid4())
        pb = knowledgebox_pb2.KnowledgeBoxNew(slug="test", forceuuid=kbid)
        pb.config.title = "My Title"
        result = await stub.NewKnowledgeBox(pb)
        assert result.status == knowledgebox_pb2.KnowledgeBoxResponseStatus.OK

        # Get current shards object
        driver = await get_driver()
        txn = await driver.begin()
        shards_object = await Node.get_all_shards(txn, kbid)
        await txn.abort()
        assert shards_object

        replica1 = shards_object.shards[0].replicas[0]

        # Clear sidecar mock
        node = NODES[replica1.node]
        node.sidecar.calls.clear()

        # Attempt to create a shadow shard of rep1 onto the same node
        req = CreateShadowShardRequest()
        req.kbid = kbid
        req.replica.id = replica1.shard.id
        req.node = replica1.node

        # Mock an error updating the shards object
        with mock.patch(
            "nucliadb.ingest.orm.node.update_shards_with_shadow_replica",
            side_effect=AttributeError,
        ):
            resp = await stub.CreateShadowShard(req)
            assert not resp.success

        # Check that the shadow shard was cleaned up after the error
        node = NODES[replica1.node]
        assert len(node.sidecar.calls["CreateShadowShard"]) == 1
        assert len(node.sidecar.calls["DeleteShadowShard"]) == 1
