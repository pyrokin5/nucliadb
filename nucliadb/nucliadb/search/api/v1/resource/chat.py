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
from typing import Optional, Union

from fastapi import Body, Header, Request, Response
from fastapi_versioning import version
from starlette.responses import StreamingResponse

from nucliadb.ingest.serialize import get_resource_uuid_by_slug
from nucliadb.models.responses import HTTPClientError
from nucliadb.search.api.v1.find import find
from nucliadb.search.api.v1.router import KB_PREFIX, api
from nucliadb.search.search.chat.query import chat, rephrase_query_from_context
from nucliadb_models.resource import NucliaDBRoles
from nucliadb_models.search import (
    ChatRequest,
    FindRequest,
    NucliaDBClientType,
    SearchOptions,
)
from nucliadb_utils.authentication import requires
from nucliadb_utils.exceptions import LimitsExceededError

END_OF_STREAM = "_END_"

CHAT_RESOURCE_EXAMPLES = {
    "search_and_chat": {
        "summary": "Ask who won the league final",
        "description": "You can ask a question to your document",  # noqa
        "value": {
            "query": "Who won the league final?",
        },
    },
}


class ResourceNotFoundError(Exception):
    pass


class IncompleteFindResourceResults(Exception):
    pass


@api.post(
    f"/{KB_PREFIX}/{{kbid}}/resource/{{rid}}/chat",
    status_code=200,
    name="Chat with a Resource (by id)",
    summary="Chat with a resource",
    description="Chat with a resource",
    tags=["Search"],
)
@requires(NucliaDBRoles.READER)
@version(1)
async def chat_post_resource_by_id(
    request: Request,
    response: Response,
    kbid: str,
    rid: str,
    item: ChatRequest = Body(examples=CHAT_RESOURCE_EXAMPLES),
    x_ndb_client: NucliaDBClientType = Header(NucliaDBClientType.API),
    x_nucliadb_user: str = Header(""),
    x_forwarded_for: str = Header(""),
) -> Union[StreamingResponse, HTTPClientError]:
    try:
        return await chat_on_resource(
            response,
            kbid,
            rid,
            None,
            item,
            x_ndb_client,
            x_nucliadb_user,
            x_forwarded_for,
        )
    except LimitsExceededError as exc:
        return HTTPClientError(status_code=exc.status_code, detail=exc.detail)
    except ResourceNotFoundError:
        return HTTPClientError(status_code=404, detail="Resource not found")
    except IncompleteFindResourceResults:
        return HTTPClientError(
            status_code=529,
            detail="Temporary error on information retrieval. Please try again.",
        )


@api.post(
    f"/{KB_PREFIX}/{{kbid}}/resource/{{rslug}}/chat",
    status_code=200,
    name="Chat with a Resource (by slug)",
    summary="Chat with a resource",
    description="Chat with a resource",
    tags=["Search"],
)
@requires(NucliaDBRoles.READER)
@version(1)
async def chat_post_resource_by_slug(
    request: Request,
    response: Response,
    kbid: str,
    rslug: str,
    item: ChatRequest = Body(examples=CHAT_RESOURCE_EXAMPLES),
    x_ndb_client: NucliaDBClientType = Header(NucliaDBClientType.API),
    x_nucliadb_user: str = Header(""),
    x_forwarded_for: str = Header(""),
) -> Union[StreamingResponse, HTTPClientError]:
    try:
        return await chat_on_resource(
            response,
            kbid,
            None,
            rslug,
            item,
            x_ndb_client,
            x_nucliadb_user,
            x_forwarded_for,
        )
    except LimitsExceededError as exc:
        return HTTPClientError(status_code=exc.status_code, detail=exc.detail)
    except ResourceNotFoundError:
        return HTTPClientError(status_code=404, detail="Resource not found")
    except IncompleteFindResourceResults:
        return HTTPClientError(
            status_code=529,
            detail="Temporary error on information retrieval. Please try again.",
        )


async def chat_on_resource(
    response: Response,
    kbid: str,
    rid: Optional[str],
    rslug: Optional[str],
    item: ChatRequest,
    x_ndb_client: NucliaDBClientType,
    x_nucliadb_user: str,
    x_forwarded_for: str,
):
    if all([rid, rslug]) or not any([rid, rslug]):
        raise ValueError("You must provide either rid or rslug")

    if rid is None:
        rid = await get_resource_uuid_by_slug(kbid, rslug)  # type: ignore
        if rid is None:
            raise ResourceNotFoundError()

    if item.context is not None and len(item.context) > 0:
        new_query = await rephrase_query_from_context(
            kbid, item.context, item.query, x_nucliadb_user
        )
    else:
        new_query = item.query

    find_request = FindRequest()
    find_request.resource_filters = [rid]
    find_request.features = [
        SearchOptions.PARAGRAPH,
        SearchOptions.VECTOR,
    ]
    find_request.query = new_query
    find_request.fields = item.fields
    find_request.filters = item.filters
    find_request.field_type_filter = item.field_type_filter
    find_request.min_score = item.min_score
    find_request.range_creation_start = item.range_creation_start
    find_request.range_creation_end = item.range_creation_end
    find_request.range_modification_start = item.range_modification_start
    find_request.range_modification_end = item.range_modification_end
    find_request.show = item.show
    find_request.extracted = item.extracted
    find_request.shards = item.shards
    find_request.autofilter = item.autofilter
    find_request.highlight = item.highlight

    find_results, incomplete = await find(
        response, kbid, find_request, x_ndb_client, x_nucliadb_user, x_forwarded_for
    )
    if incomplete:
        raise IncompleteFindResourceResults()
    return await chat(kbid, find_results, item, x_nucliadb_user)
