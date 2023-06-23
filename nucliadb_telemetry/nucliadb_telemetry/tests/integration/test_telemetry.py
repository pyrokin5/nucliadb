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

import asyncio
import json

import pytest
from httpx import AsyncClient

from nucliadb_telemetry import grpc_metrics
from nucliadb_telemetry.jetstream import msg_time_histo
from nucliadb_telemetry.settings import telemetry_settings
from nucliadb_telemetry.tests.telemetry import Greeter


def fmt_span(span):
    tags_by_key = {tag["key"]: tag["value"] for tag in span["tags"]}
    return {
        "time": span["startTime"],
        "id": span["spanID"],
        "parent": span["references"][0]["spanID"],
        "process": span["processID"],
        "scope": tags_by_key["otel.scope.name"],
        "operation": span["operationName"],
    }


def debug_spans(spans):
    print(
        json.dumps(
            sorted([fmt_span(span) for span in spans], key=lambda x: x["time"]),
            indent=4,
        )
    )


@pytest.mark.asyncio
async def test_telemetry_dict(http_service: AsyncClient, greeter: Greeter):
    trace_id = "f13dc5318bf3bef64a0a5ea607db93a1"

    resp = await http_service.get(
        "http://test/",
        headers={
            "x-b3-traceid": trace_id,
            "x-b3-spanid": "bfc2225c60b39d97",
            "x-b3-sampled": "1",
        },
    )
    assert resp.status_code == 200

    # Check that trace ids are returned in response headers
    assert resp.headers["X-NUCLIA-TRACE-ID"]
    assert resp.headers["X-NUCLIA-TRACE-ID"] == trace_id
    assert "X-NUCLIA-TRACE-ID" in resp.headers["Access-Control-Expose-Headers"]

    for i in range(10):
        if len(greeter.messages) == 0:
            await asyncio.sleep(1)
    assert (
        greeter.messages[0].headers["x-b3-traceid"]
        == trace_id
    )
    assert len(greeter.messages) == 4

    expected_spans = 17

    await asyncio.sleep(2)
    client = AsyncClient()
    for _ in range(10):
        resp = await client.get(
            f"http://localhost:{telemetry_settings.jaeger_query_port}/api/traces/{trace_id}",
            headers={"Accept": "application/json"},
        )
        if (
            resp.status_code != 200
            or len(resp.json()["data"][0]["spans"]) < expected_spans
        ):
            await asyncio.sleep(2)
        else:
            break

    assert resp.json()["data"][0]["traceID"] == trace_id

    # Enable this block for debugging purposes, to see sunmmarized and sorted details of all spans
    # debug_spans(resp.json()["data"][0]["spans"])

    assert len(resp.json()["data"][0]["spans"]) == expected_spans
    assert len(resp.json()["data"][0]["processes"]) == 3

    assert grpc_metrics.grpc_client_observer.histogram.collect()[0].samples  # type: ignore
    assert grpc_metrics.grpc_server_observer.histogram.collect()[0].samples  # type: ignore

    assert msg_time_histo.histo.collect()[0].samples  # type: ignore

    sample = [
        sam.labels
        for sam in msg_time_histo.histo.collect()[0].samples  # type: ignore
        if sam.labels.get("le") == "0.005"
    ][0]
    sample.pop("consumer")
    assert sample == {"stream": "testing", "acked": "no", "le": "0.005"}
