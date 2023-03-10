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
from datetime import datetime
from os.path import getsize
from typing import Optional
from uuid import uuid4

import pytest
from nucliadb_protos.resources_pb2 import (
    Basic,
    Classification,
    CloudFile,
    Entity,
    ExtractedText,
    ExtractedTextWrapper,
    ExtractedVectorsWrapper,
    FieldComputedMetadata,
    FieldComputedMetadataWrapper,
    FieldID,
    FieldType,
    FileExtractedData,
    LargeComputedMetadata,
    LargeComputedMetadataWrapper,
)
from nucliadb_protos.resources_pb2 import Metadata as PBMetadata
from nucliadb_protos.resources_pb2 import Origin as PBOrigin
from nucliadb_protos.resources_pb2 import Paragraph, Position, RowsPreview, Sentence
from nucliadb_protos.resources_pb2 import TokenSplit as PBTokenSplit
from nucliadb_protos.resources_pb2 import UserFieldMetadata as PBUserFieldMetadata
from nucliadb_protos.train_pb2 import EnabledMetadata
from nucliadb_protos.utils_pb2 import Relation as PBRelation
from nucliadb_protos.utils_pb2 import RelationNode, Vector, VectorObject, Vectors
from nucliadb_protos.writer_pb2 import BrokerMessage

from nucliadb.ingest.fields.file import File
from nucliadb.ingest.fields.text import Text
from nucliadb.ingest.orm.knowledgebox import KnowledgeBox
from nucliadb.ingest.tests.assets import ASSETS_PATH
from nucliadb.ingest.tests.fixtures import broker_resource
from nucliadb_utils.storages.storage import Storage


@pytest.mark.asyncio
async def test_knowledgebox_purge_handles_unexisting_shard_payload(
    gcs_storage, redis_driver
):
    await KnowledgeBox.purge(redis_driver, "idonotexist")


@pytest.fixture(scope="function")
def tikv_driver_configured(tikv_driver):
    from nucliadb.ingest.settings import settings
    from nucliadb_utils.store import MAIN

    prev_driver = settings.driver
    settings.driver = "tikv"
    settings.driver_tikv_url = tikv_driver.url
    MAIN["driver"] = tikv_driver_configured

    yield

    settings.driver = prev_driver
    MAIN.pop("driver", None)


@pytest.fixture(scope="function")
async def tikv_txn(tikv_driver):
    txn = await tikv_driver.begin()
    yield txn
    await txn.abort()


@pytest.mark.asyncio
async def test_knowledgebox_delete_all_kb_keys(
    gcs_storage,
    cache,
    fake_node,
    tikv_driver_configured,
    tikv_driver,
    knowledgebox_ingest: str,
):
    txn = await tikv_driver.begin()
    kbid = knowledgebox_ingest
    kb_obj = KnowledgeBox(txn, gcs_storage, cache, kbid=kbid)

    # Create some resources in the KB
    n_resources = 100
    uuids = set()
    for _ in range(n_resources):
        bm = broker_resource(kbid)
        r = await kb_obj.add_resource(uuid=bm.uuid, slug=bm.uuid, basic=bm.basic)
        assert r is not None
        await r.set_slug()
        uuids.add(bm.uuid)
    await txn.commit(resource=False)

    # Check that all of them are there
    txn = await tikv_driver.begin()
    kb_obj = KnowledgeBox(txn, gcs_storage, cache, kbid=kbid)
    for uuid in uuids:
        assert await kb_obj.get_resource_uuid_by_slug(uuid) == uuid
    await txn.abort()

    # Now delete all kb keys
    await KnowledgeBox.delete_all_kb_keys(tikv_driver, kbid, chunk_size=10)

    # Check that all of them were deleted
    txn = await tikv_driver.begin()
    kb_obj = KnowledgeBox(txn, gcs_storage, cache, kbid=kbid)
    for uuid in uuids:
        assert await kb_obj.get_resource_uuid_by_slug(uuid) is None
    await txn.abort()


@pytest.mark.asyncio
async def test_create_resource_orm_file_extracted(
    local_files, gcs_storage: Storage, txn, cache, fake_node, knowledgebox_ingest: str
):
    uuid = str(uuid4())
    kb_obj = KnowledgeBox(txn, gcs_storage, cache, kbid=knowledgebox_ingest)
    r = await kb_obj.add_resource(uuid=uuid, slug="slug")
    assert r is not None

    filename = f"{ASSETS_PATH}/orm/file.png"
    cf1 = CloudFile(
        uri="file.png",
        source=CloudFile.Source.LOCAL,
        bucket_name="/assets/orm",
        size=getsize(filename),
        content_type="image/png",
        filename="file.png",
    )

    ex1 = FileExtractedData()
    ex1.md5 = "ASD"
    ex1.language = "ca"
    ex1.metadata["asd"] = "asd"
    ex1.nested["asd"] = "asd"
    ex1.file_generated["asd"].CopyFrom(cf1)
    ex1.file_rows_previews["asd"].sheets["Tab1"].rows.append(
        RowsPreview.Sheet.Row(cell="hola")
    )
    ex1.file_preview.CopyFrom(cf1)
    ex1.file_thumbnail.CopyFrom(cf1)
    ex1.file_pages_previews.pages.append(cf1)
    ex1.field = "file1"

    field_obj: File = await r.get_field(ex1.field, FieldType.FILE, load=False)
    await field_obj.set_file_extracted_data(ex1)

    ex2: Optional[FileExtractedData] = await field_obj.get_file_extracted_data()
    assert ex2 is not None
    assert ex2.md5 == ex1.md5
    assert ex2.file_generated["asd"].source == CloudFile.Source.GCS
    assert ex2.file_preview.source == CloudFile.Source.GCS
    assert ex2.file_thumbnail.source == CloudFile.Source.GCS
    assert ex1.file_pages_previews.pages[0].source == CloudFile.Source.GCS
    data = await gcs_storage.downloadbytescf(ex1.file_pages_previews.pages[0])
    with open(filename, "rb") as testfile:
        data2 = testfile.read()
    assert data.read() == data2


class TestExtracted:
    @pytest.mark.asyncio
    async def test_create_resource_orm_extracted(
        gcs_storage: Storage, txn, cache, fake_node, knowledgebox_ingest: str
    ):
        uuid = str(uuid4())
        kb_obj = KnowledgeBox(txn, gcs_storage, cache, kbid=knowledgebox_ingest)
        r = await kb_obj.add_resource(uuid=uuid, slug="slug")
        assert r is not None

        ex1 = ExtractedTextWrapper()
        ex1.field.CopyFrom(FieldID(field_type=FieldType.TEXT, field="text1"))
        ex1.body.text = "My Text"

        field_obj: Optional[Text] = await r.get_field(
            ex1.field.field, ex1.field.field_type, load=False
        )
        assert field_obj is not None
        await field_obj.set_extracted_text(ex1)

        ex2: Optional[ExtractedText] = await field_obj.get_extracted_text()
        assert ex2 is not None
        assert ex2.text == ex1.body.text

    @pytest.mark.asyncio
    async def test_create_resource_orm_extracted_file(
        local_files,
        gcs_storage: Storage,
        txn,
        cache,
        fake_node,
        knowledgebox_ingest: str,
    ):
        uuid = str(uuid4())
        kb_obj = KnowledgeBox(txn, gcs_storage, cache, kbid=knowledgebox_ingest)
        r = await kb_obj.add_resource(uuid=uuid, slug="slug")
        assert r is not None

        ex1 = ExtractedTextWrapper()
        ex1.field.CopyFrom(FieldID(field_type=FieldType.TEXT, field="text1"))

        filename = f"{ASSETS_PATH}/orm/text.pb"
        cf1 = CloudFile(
            uri="text.pb",
            source=CloudFile.Source.LOCAL,
            bucket_name="/assets/orm",
            size=getsize(filename),
            content_type="application/octet-stream",
            filename="text.pb",
        )
        ex1.file.CopyFrom(cf1)

        field_obj: Optional[Text] = await r.get_field(
            ex1.field.field, ex1.field.field_type, load=False
        )
        assert field_obj is not None
        await field_obj.set_extracted_text(ex1)

        ex2: Optional[ExtractedText] = await field_obj.get_extracted_text()
        assert ex2 is not None
        ex3 = ExtractedText()
        with open(filename, "rb") as testfile:
            data2 = testfile.read()
        ex3.ParseFromString(data2)
        assert ex3.text == ex2.text

    @pytest.mark.asyncio
    async def test_create_resource_orm_extracted_delta(
        gcs_storage: Storage, txn, cache, fake_node, knowledgebox_ingest: str
    ):
        uuid = str(uuid4())
        kb_obj = KnowledgeBox(txn, gcs_storage, cache, kbid=knowledgebox_ingest)
        r = await kb_obj.add_resource(uuid=uuid, slug="slug")
        assert r is not None
        ex1 = ExtractedTextWrapper()
        ex1.field.CopyFrom(FieldID(field_type=FieldType.LAYOUT, field="text1"))
        ex1.body.split_text["ident1"] = "My text"
        ex1.body.text = "all text"

        field_obj: Text = await r.get_field(
            ex1.field.field, ex1.field.field_type, load=False
        )
        await field_obj.set_extracted_text(ex1)

        ex2: Optional[ExtractedText] = await field_obj.get_extracted_text()
        assert ex2 is not None
        assert ex2.text == ex1.body.text

        ex1 = ExtractedTextWrapper()
        ex1.field.CopyFrom(FieldID(field_type=FieldType.LAYOUT, field="text1"))
        ex1.body.split_text["ident2"] = "My text"
        ex1.body.text = "all text 2"

        field_obj = await r.get_field(ex1.field.field, ex1.field.field_type, load=False)
        await field_obj.set_extracted_text(ex1)

        ex2 = await field_obj.get_extracted_text()
        assert ex2 is not None
        assert ex2.text == ex1.body.text
        assert len(ex2.split_text) == 2


class TestLargeMetadata:
    @pytest.mark.asyncio
    async def test_create_resource_orm_large_metadata(
        gcs_storage: Storage, txn, cache, fake_node, knowledgebox_ingest: str
    ):
        uuid = str(uuid4())
        kb_obj = KnowledgeBox(txn, gcs_storage, cache, kbid=knowledgebox_ingest)
        r = await kb_obj.add_resource(uuid=uuid, slug="slug")
        assert r is not None

        ex1 = LargeComputedMetadataWrapper()
        ex1.field.CopyFrom(FieldID(field_type=FieldType.TEXT, field="text1"))
        en1 = Entity(token="tok1", root="tok", type="NAME")
        en2 = Entity(token="tok2", root="tok2", type="NAME")
        ex1.real.metadata.entities.append(en1)
        ex1.real.metadata.entities.append(en2)
        ex1.real.metadata.tokens["tok"] = 3

        field_obj: Text = await r.get_field(
            ex1.field.field, ex1.field.field_type, load=False
        )
        await field_obj.set_large_field_metadata(ex1)

        ex2: Optional[
            LargeComputedMetadata
        ] = await field_obj.get_large_field_metadata()
        assert ex2 is not None
        assert ex2.metadata.tokens["tok"] == ex1.real.metadata.tokens["tok"]

    @pytest.mark.asyncio
    async def test_create_resource_orm_large_metadata_file(
        local_files,
        gcs_storage: Storage,
        txn,
        cache,
        fake_node,
        knowledgebox_ingest: str,
    ):
        uuid = str(uuid4())
        kb_obj = KnowledgeBox(txn, gcs_storage, cache, kbid=knowledgebox_ingest)
        r = await kb_obj.add_resource(uuid=uuid, slug="slug")
        assert r is not None

        ex1 = LargeComputedMetadataWrapper()
        ex1.field.CopyFrom(FieldID(field_type=FieldType.TEXT, field="text1"))

        en1 = Entity(token="tok1", root="tok", type="NAME")
        en2 = Entity(token="tok2", root="tok2", type="NAME")
        real = LargeComputedMetadata()
        real.metadata.entities.append(en1)
        real.metadata.entities.append(en2)
        real.metadata.tokens["tok"] = 3
        real.metadata.tokens["adeu"] = 5

        filename = f"{ASSETS_PATH}/orm/largemetadata.pb"
        with open(filename, "wb") as testfile:
            testfile.write(real.SerializeToString())
        cf1 = CloudFile(
            uri="largemetadata.pb",
            source=CloudFile.Source.LOCAL,
            bucket_name="/assets/orm",
            size=getsize(filename),
            content_type="application/octet-stream",
            filename="largemetadata.pb",
        )
        ex1.file.CopyFrom(cf1)

        field_obj: Text = await r.get_field(
            ex1.field.field, ex1.field.field_type, load=False
        )
        await field_obj.set_large_field_metadata(ex1)

        ex2: Optional[
            LargeComputedMetadata
        ] = await field_obj.get_large_field_metadata()
        assert ex2 is not None
        ex3 = LargeComputedMetadata()
        with open(filename, "rb") as testfile:
            data2 = testfile.read()
        ex3.ParseFromString(data2)
        assert ex3.metadata.tokens["tok"] == ex2.metadata.tokens["tok"]


class TestMetadata:
    @pytest.mark.asyncio
    async def test_create_resource_orm_metadata(
        gcs_storage: Storage, txn, cache, fake_node, knowledgebox_ingest: str
    ):
        uuid = str(uuid4())
        kb_obj = KnowledgeBox(txn, gcs_storage, cache, kbid=knowledgebox_ingest)
        r = await kb_obj.add_resource(uuid=uuid, slug="slug")
        assert r is not None

        ex1 = FieldComputedMetadataWrapper()
        ex1.field.CopyFrom(FieldID(field_type=FieldType.TEXT, field="text1"))
        ex1.metadata.metadata.links.append("https://nuclia.com")

        p1 = Paragraph(start=0, end=20)
        p1.sentences.append(Sentence(start=0, end=10, key="test"))
        p1.sentences.append(Sentence(start=11, end=20, key="test"))
        cl1 = Classification(labelset="labelset1", label="label1")
        p1.classifications.append(cl1)
        ex1.metadata.metadata.paragraphs.append(p1)
        ex1.metadata.metadata.classifications.append(cl1)
        ex1.metadata.metadata.ner["Ramon"] = "PEOPLE"
        ex1.metadata.metadata.last_index.FromDatetime(datetime.now())
        ex1.metadata.metadata.last_understanding.FromDatetime(datetime.now())
        ex1.metadata.metadata.last_extract.FromDatetime(datetime.now())
        ex1.metadata.metadata.positions["document"].entity = "Ramon"
        ex1.metadata.metadata.positions["document"].position.extend(
            [Position(start=0, end=5), Position(start=23, end=28)]
        )

        field_obj: Text = await r.get_field(
            ex1.field.field, ex1.field.field_type, load=False
        )
        await field_obj.set_field_metadata(ex1)

        ex2: Optional[FieldComputedMetadata] = await field_obj.get_field_metadata()
        assert ex2 is not None
        assert ex2.metadata.links[0] == ex1.metadata.metadata.links[0]

    @pytest.mark.asyncio
    async def test_create_resource_orm_metadata_split(
        gcs_storage: Storage, txn, cache, fake_node, knowledgebox_ingest: str
    ):
        uuid = str(uuid4())
        kb_obj = KnowledgeBox(txn, gcs_storage, cache, kbid=knowledgebox_ingest)
        r = await kb_obj.add_resource(uuid=uuid, slug="slug")
        assert r is not None

        ex1 = FieldComputedMetadataWrapper()
        ex1.field.CopyFrom(FieldID(field_type=FieldType.LAYOUT, field="text1"))
        ex1.metadata.split_metadata["ff1"].links.append("https://nuclia.com")
        s2 = Sentence(start=0, end=10, key="test")
        s1 = Sentence(start=11, end=20, key="test")

        p1 = Paragraph(start=0, end=20)
        p1.sentences.append(s1)
        p1.sentences.append(s2)
        cl1 = Classification(labelset="labelset1", label="label1")
        p1.classifications.append(cl1)
        ex1.metadata.split_metadata["ff1"].paragraphs.append(p1)
        ex1.metadata.split_metadata["ff1"].classifications.append(cl1)
        ex1.metadata.split_metadata["ff1"].ner["Ramon"] = "PEOPLE"
        ex1.metadata.split_metadata["ff1"].last_index.FromDatetime(datetime.now())
        ex1.metadata.split_metadata["ff1"].last_understanding.FromDatetime(
            datetime.now()
        )
        ex1.metadata.split_metadata["ff1"].last_extract.FromDatetime(datetime.now())
        field_obj: Text = await r.get_field(
            ex1.field.field, ex1.field.field_type, load=False
        )
        await field_obj.set_field_metadata(ex1)

        ex2 = FieldComputedMetadataWrapper()
        ex2.field.CopyFrom(FieldID(field_type=FieldType.LAYOUT, field="text1"))
        ex2.metadata.split_metadata["ff2"].links.append("https://nuclia.com")
        s1 = Sentence(start=0, end=10, key="test")
        s2 = Sentence(start=11, end=20, key="test")

        p1 = Paragraph(start=0, end=20)
        p1.sentences.append(s1)
        p1.sentences.append(s2)
        cl1 = Classification(labelset="labelset1", label="label1")
        p1.classifications.append(cl1)
        ex2.metadata.split_metadata["ff2"].paragraphs.append(p1)
        ex2.metadata.split_metadata["ff2"].classifications.append(cl1)
        ex2.metadata.split_metadata["ff2"].ner["Ramon"] = "PEOPLE"
        ex2.metadata.split_metadata["ff2"].last_index.FromDatetime(datetime.now())
        ex2.metadata.split_metadata["ff2"].last_understanding.FromDatetime(
            datetime.now()
        )
        ex2.metadata.split_metadata["ff2"].last_extract.FromDatetime(datetime.now())
        field_obj = await r.get_field(ex1.field.field, ex1.field.field_type, load=False)
        await field_obj.set_field_metadata(ex2)

        ex3: Optional[FieldComputedMetadata] = await field_obj.get_field_metadata()
        assert ex3 is not None
        assert (
            ex1.metadata.split_metadata["ff1"].links[0]
            == ex3.split_metadata["ff1"].links[0]
        )
        assert len(ex3.split_metadata) == 2


class TestResource:
    @pytest.mark.asyncio
    async def test_create_resource_orm_with_basic(
        gcs_storage, txn, cache, fake_node, knowledgebox_ingest: str
    ):
        basic = Basic(
            icon="text/plain",
            title="My title",
            summary="My summary",
            thumbnail="/file",
            layout="basic",
        )
        basic.metadata.metadata["key"] = "value"
        basic.metadata.language = "ca"
        basic.metadata.useful = True
        basic.metadata.status = PBMetadata.Status.PROCESSED

        cl1 = Classification(labelset="labelset1", label="label")
        basic.usermetadata.classifications.append(cl1)

        r1 = PBRelation(
            relation=PBRelation.CHILD,
            source=RelationNode(value="000000", ntype=RelationNode.NodeType.RESOURCE),
            to=RelationNode(value="000001", ntype=RelationNode.NodeType.RESOURCE),
        )

        basic.usermetadata.relations.append(r1)

        ufm1 = PBUserFieldMetadata(
            token=[PBTokenSplit(token="My home", klass="Location")],
            field=FieldID(field_type=FieldType.TEXT, field="title"),
        )

        basic.fieldmetadata.append(ufm1)
        uuid = str(uuid4())
        kb_obj = KnowledgeBox(txn, gcs_storage, cache, kbid=knowledgebox_ingest)
        r = await kb_obj.add_resource(uuid=uuid, slug="slug", basic=basic)
        assert r is not None

        b2: Optional[Basic] = await r.get_basic()
        assert b2 is not None
        assert b2.icon == "text/plain"

        o2: Optional[PBOrigin] = await r.get_origin()
        assert o2 is None

        o2 = PBOrigin()
        assert o2 is not None
        o2.source = PBOrigin.Source.API
        o2.source_id = "My Surce"
        o2.created.FromDatetime(datetime.now())

        await r.set_origin(o2)
        o2 = await r.get_origin()
        assert o2 is not None
        assert o2.source_id == "My Surce"

    @pytest.mark.asyncio
    async def test_iterate_paragraphs(
        gcs_storage, txn, cache, fake_node, knowledgebox_ingest: str
    ):
        # Create a resource
        basic = Basic(
            icon="text/plain",
            title="My title",
            summary="My summary",
            thumbnail="/file",
            layout="basic",
        )
        basic.metadata.metadata["key"] = "value"
        basic.metadata.language = "ca"
        basic.metadata.useful = True
        basic.metadata.status = PBMetadata.Status.PROCESSED

        uuid = str(uuid4())
        kb_obj = KnowledgeBox(txn, gcs_storage, cache, kbid=knowledgebox_ingest)
        r = await kb_obj.add_resource(uuid=uuid, slug="slug", basic=basic)
        assert r is not None

        # Add some labelled paragraphs to it
        bm = BrokerMessage()
        field1_if = FieldID()
        field1_if.field = "field1"
        field1_if.field_type = FieldType.TEXT
        fcmw = FieldComputedMetadataWrapper()
        fcmw.field.CopyFrom(field1_if)
        p1 = Paragraph()
        p1.start = 0
        p1.end = 82
        p1.classifications.append(Classification(labelset="ls1", label="label1"))
        p2 = Paragraph()
        p2.start = 84
        p2.end = 103
        p2.classifications.append(Classification(labelset="ls1", label="label2"))
        fcmw.metadata.metadata.paragraphs.append(p1)
        fcmw.metadata.metadata.paragraphs.append(p2)
        bm.field_metadata.append(fcmw)
        await r.apply_extracted(bm)

        # Check iterate paragraphs
        async for paragraph in r.iterate_paragraphs(EnabledMetadata(labels=True)):
            assert len(paragraph.metadata.labels.paragraph) == 1
            assert paragraph.metadata.labels.paragraph[0].label in ("label1", "label2")


class TestVectors:
    @pytest.mark.asyncio
    async def test_create_resource_orm_vector(
        gcs_storage: Storage, txn, cache, fake_node, knowledgebox_ingest: str
    ):
        uuid = str(uuid4())
        kb_obj = KnowledgeBox(txn, gcs_storage, cache, kbid=knowledgebox_ingest)
        r = await kb_obj.add_resource(uuid=uuid, slug="slug")
        assert r is not None

        ex1 = ExtractedVectorsWrapper()
        ex1.field.CopyFrom(FieldID(field_type=FieldType.TEXT, field="text1"))
        v1 = Vector(start=1, end=2, vector=b"ansjkdn")
        ex1.vectors.vectors.vectors.append(v1)

        field_obj: Text = await r.get_field(
            ex1.field.field, ex1.field.field_type, load=False
        )
        await field_obj.set_vectors(ex1)

        ex2: Optional[VectorObject] = await field_obj.get_vectors()
        assert ex2 is not None
        assert ex2.vectors.vectors[0].vector == ex1.vectors.vectors.vectors[0].vector

    @pytest.mark.asyncio
    async def test_create_resource_orm_vector_file(
        local_files,
        gcs_storage: Storage,
        txn,
        cache,
        fake_node,
        knowledgebox_ingest: str,
    ):
        uuid = str(uuid4())
        kb_obj = KnowledgeBox(txn, gcs_storage, cache, kbid=knowledgebox_ingest)
        r = await kb_obj.add_resource(uuid=uuid, slug="slug")
        assert r is not None

        ex1 = ExtractedVectorsWrapper()
        ex1.field.CopyFrom(FieldID(field_type=FieldType.TEXT, field="text1"))

        filename = f"{ASSETS_PATH}/orm/vectors.pb"
        cf1 = CloudFile(
            uri="vectors.pb",
            source=CloudFile.Source.LOCAL,
            size=getsize(filename),
            bucket_name="/assets/orm",
            content_type="application/octet-stream",
            filename="vectors.pb",
        )
        ex1.file.CopyFrom(cf1)

        field_obj: Text = await r.get_field(
            ex1.field.field, ex1.field.field_type, load=False
        )
        await field_obj.set_vectors(ex1)

        ex2: Optional[VectorObject] = await field_obj.get_vectors()
        ex3 = VectorObject()
        with open(filename, "rb") as testfile:
            data2 = testfile.read()
        ex3.ParseFromString(data2)
        assert ex2 is not None

        assert ex3.vectors.vectors[0].vector == ex2.vectors.vectors[0].vector

    @pytest.mark.asyncio
    async def test_create_resource_orm_vector_split(
        gcs_storage: Storage, txn, cache, fake_node, knowledgebox_ingest: str
    ):
        uuid = str(uuid4())
        kb_obj = KnowledgeBox(txn, gcs_storage, cache, kbid=knowledgebox_ingest)
        r = await kb_obj.add_resource(uuid=uuid, slug="slug")
        assert r is not None

        ex1 = ExtractedVectorsWrapper()
        ex1.field.CopyFrom(FieldID(field_type=FieldType.LAYOUT, field="text1"))
        v1 = Vector(start=1, vector=b"ansjkdn")
        vs1 = Vectors()
        vs1.vectors.append(v1)
        ex1.vectors.split_vectors["es1"].vectors.append(v1)
        ex1.vectors.split_vectors["es2"].vectors.append(v1)

        field_obj: Text = await r.get_field(
            ex1.field.field, ex1.field.field_type, load=False
        )
        await field_obj.set_vectors(ex1)

        ex1 = ExtractedVectorsWrapper()
        ex1.field.CopyFrom(FieldID(field_type=FieldType.LAYOUT, field="text1"))
        v1 = Vector(start=1, vector=b"ansjkdn")
        vs1 = Vectors()
        vs1.vectors.append(v1)
        ex1.vectors.split_vectors["es3"].vectors.append(v1)
        ex1.vectors.split_vectors["es2"].vectors.append(v1)

        field_obj2: Text = await r.get_field(
            ex1.field.field, ex1.field.field_type, load=False
        )
        await field_obj2.set_vectors(ex1)

        ex2: Optional[VectorObject] = await field_obj2.get_vectors()
        assert ex2 is not None
        assert len(ex2.split_vectors) == 3
