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
from typing import Optional

from httpx import AsyncClient
from nucliadb_protos.knowledgebox_pb2 import SemanticModelMetadata
from nucliadb_protos.utils_pb2 import VectorSimilarity
from nucliadb_protos.writer_pb2 import Shards
from pydantic import BaseModel

from nucliadb.common.maindb.utils import setup_driver
from nucliadb.ingest.orm.knowledgebox import KnowledgeBox
from nucliadb_utils.keys import KB_SHARDS
from nucliadb_utils.utilities import get_storage

from .tool import MigrationContext


async def migrate(context: MigrationContext) -> None:
    """
    Non-kb type of migration.
    """


async def migrate_kb(context: MigrationContext, kbid: str) -> None:
    """
    Migrate kb.

    Must have both types of migrations.
    """
    # Call learning config service to get the model metadata
    http_client = AsyncClient()
    learning_config = await get_learning_config(http_client, kbid)
    shards_object = await get_shards_object(kbid)

    min_score = get_default_min_score(learning_config, shards_object)
    vector_dimension = get_vector_dimension(learning_config, shards_object)

    await set_model_metadata(kbid, min_score, vector_dimension)


class KBLearningConfig(BaseModel):
    semantic_model: Optional[str]
    semantic_vector_similarity: Optional[str]
    semantic_vector_size: Optional[int]


async def set_model_metadata(
    kbid: str, similarity: VectorSimilarity, min_score: float, vector_dimension: int
) -> None:
    driver = await setup_driver()
    storage = await get_storage()
    async with driver.transaction() as txn:
        kb = KnowledgeBox(txn, storage, kbid)
        shards = await kb.get_shards_object()

        shards.similarity = similarity
        model = shards.model if shards.model else SemanticModelMetadata()
        model.similarity_function = similarity
        model.default_min_score = min_score
        model.vector_dimension = vector_dimension
        shards.model.CopyFrom(model)

        kb_shards_key = KB_SHARDS.format(kbid)
        await txn.set(kb_shards_key, shards.SerializeToString())
        await txn.commit()


async def get_shards_object(kbid: str) -> Optional[Shards]:
    driver = await setup_driver()
    storage = await get_storage()
    async with driver.transaction() as txn:
        kb = KnowledgeBox(txn, storage, kbid)
        shards = await kb.get_shards_object()
        if shards is None:
            # TODO
            raise Exception()
        return shards


async def get_learning_config(
    client: AsyncClient, kbid: str
) -> Optional[KBLearningConfig]:
    resp = await client.get()
    # handle error response status code
    config = KBLearningConfig()
    return config


def get_default_min_score(similarity_function: VectorSimilarity) -> float:
    if similarity_function == VectorSimilarity.DOT:
        return 1.5
    elif similarity_function == VectorSimilarity.COSINE:
        return 0.7
    else:
        raise ValueError(f"Unknown similarity function: {similarity_function}")


def get_vector_dimension(model_name: str) -> int:
    if model_name.startswith("en"):
        return 384
    elif model_name.startswith("multilingual"):
        return 768
    else:
        raise ValueError(f"Unknown model name: {model_name}")
