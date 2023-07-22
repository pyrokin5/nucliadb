import logging
import os
import uuid

from nucliadb.common.cluster.settings import settings as cluster_settings

logger = logging.getLogger(__name__)


def get_standalone_node_id() -> str:
    if not os.path.exists(cluster_settings.data_path):
        os.makedirs(cluster_settings.data_path, exist_ok=True)
    host_key_path = f"{cluster_settings.data_path}/node.key"
    if not os.path.exists(host_key_path):
        logger.info("Generating new node key")
        with open(host_key_path, "wb") as f:
            f.write(uuid.uuid4().bytes)

    with open(host_key_path, "rb") as f:
        return str(uuid.UUID(bytes=f.read()))
