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
import logging

import aiohttp

from nucliadb.common.cluster.discovery.abc import (
    AbstractClusterDiscovery,
    update_members,
)
from nucliadb.common.cluster.discovery.types import IndexNodeMetadata

logger = logging.getLogger(__name__)


class StandaloneDiscovery(AbstractClusterDiscovery):
    """
    Manual provide all cluster members addresses to load information from standalone server.
    """

    session: aiohttp.ClientSession

    async def discover(self) -> None:
        members = []
        for address in self.settings.cluster_discovery_manual_addresses:
            url = f"http://{address}/api/v1/cluster/self/info"
            async with self.session.get(
                url, headers={"X-NUCLIADB-ROLES": "MANAGER"}
            ) as resp:
                if resp.status != 200:
                    logger.warning(f"Cannot get cluster info from {address}")
                    continue
                metadata = await resp.json()
                members.append(
                    IndexNodeMetadata(
                        node_id=metadata["id"],
                        name=metadata["id"],
                        address=metadata["address"],
                        shard_count=metadata["shard_count"],
                    )
                )
        update_members(members)

    async def watch(self) -> None:
        first = True
        while True:
            wait_time = 15
            if first:
                wait_time = 1
            first = False
            try:
                await asyncio.sleep(wait_time)
                await self.discover()
            except asyncio.CancelledError:
                return
            except Exception:
                logger.exception(
                    "Error while watching cluster members. Will retry at started interval"
                )

    async def initialize(self) -> None:
        self.session = aiohttp.ClientSession()
        self.task = asyncio.create_task(self.watch())

    async def finalize(self) -> None:
        self.task.cancel()
        await self.session.close()
