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
import inspect
import typing
from typing import Any, Callable, List, Optional, Tuple, Type, Union

import httpx
from pydantic import BaseModel


class Example(BaseModel):
    description: str
    code: str


class Docstring(BaseModel):
    doc: str
    examples: List[Example] = []


SEARCH = Docstring(
    doc="""Search in your knowledge box""",
    examples=[
        Example(
            description="Advanced search on the full text index",
            code=""">>> from nucliadb_sdk import *
>>> sdk = NucliaDBSDK(api_key="api-key")
>>> resp = sdk.search(kbid="mykbid", advanced_query="text:SRE OR text:DevOps", features=["document"])
>>> rid = resp.fulltext.results[0].rid
>>> resp.resources[rid].title
The Site Reliability Workbook.pdf
""",
        )
    ],
)

FIND = Docstring(
    doc="""Find documents in your knowledge box""",
    examples=[
        Example(
            description="Find documents matching a query",
            code=""">>> from nucliadb_sdk import *
>>> sdk = NucliaDBSDK(api_key="api-key")
>>> resp = sdk.find(kbid="mykbid", query="Very experienced candidates with Rust experience")
>>> resp.resources.popitem().title
Graydon_Hoare.cv.pdf
""",
        ),
        Example(
            description="Filter down by country and increase accuracy of results",
            code=""">>> content = FindRequest(query="Very experienced candidates with Rust experience", filters=["/l/country/Spain"], min_score=2.5)
>>> resp = sdk.find(kbid="mykbid", content=content)
>>> resp.resources.popitem().title
http://github.com/hermeGarcia
""",  # noqa
        ),
    ],
)

CHAT = Docstring(
    doc="""Chat with your knowledge box""",
    examples=[
        Example(
            description="Get an answer for a question that is part of the data in the Knowledge Box",
            code=""">>> from nucliadb_sdk import *
>>> sdk = NucliaDBSDK(api_key="api-key")
>>> sdk.chat(kbid="mykbid", query="Will France be in recession in 2023?").answer
Yes, according to the provided context, France is expected to be in recession in 2023.""",
        ),
        Example(
            description="You can use the `content` parameter to pass a `ChatRequest` object",
            code=""">>> content = ChatRequest(query="Who won the 2018 football World Cup?")
>>> sdk.chat(kbid="mykbid", content=content).answer
France won the 2018 football World Cup.
""",
        ),
    ],
)

SUGGEST = Docstring(
    doc="""Get query suggestions based on your knowledge box data""",
    examples=[
        Example(
            description="Typo-tolerant suggestions are supported",
            code=""">>> from nucliadb_sdk import *
>>> sdk = NucliaDBSDK(api_key="api-key")
>>> sdk.suggest(kbid="mykbid", query="Ablert Eisntien").paragraphs.results[0].text
Albert Einstein, best known for developing the theory of relativity.
""",
        ),
    ],
)


def inject_documentation(
    func,
    name: str,
    method: str,
    path_template: str,
    path_params: Tuple[str, ...],
    request_type: Optional[Union[Type[BaseModel], List[Any]]],
    response_type: Optional[
        Union[Type[BaseModel], Callable[[httpx.Response], BaseModel]]
    ],
    docstring: Optional[Docstring] = None,
):
    func.__name__ = name
    _inject_signature(func, path_params, request_type, response_type)
    _inject_docstring(func, method, path_template, path_params, request_type, docstring)


def _inject_signature(
    func,
    path_params: Tuple[str, ...],
    request_type: Optional[Union[Type[BaseModel], List[Any]]],
    response_type: Optional[
        Union[Type[BaseModel], Callable[[httpx.Response], BaseModel]]
    ],
):
    parameters = []
    # The first parameter is always self
    parameters.append(
        inspect.Parameter("self", kind=inspect.Parameter.POSITIONAL_OR_KEYWORD)
    )

    # Path params
    for path_param in path_params:
        parameters.append(
            inspect.Parameter(
                path_param, kind=inspect.Parameter.KEYWORD_ONLY, annotation=str
            )
        )

    # Body params
    if request_type is not None:
        if isinstance(request_type, type) and issubclass(request_type, BaseModel):
            for field in request_type.__fields__.values():
                parameters.append(
                    inspect.Parameter(
                        field.name,
                        kind=inspect.Parameter.KEYWORD_ONLY,
                        annotation=field.annotation,
                        default=field.default,
                    )
                )
        parameters.append(
            inspect.Parameter(
                "content",
                kind=inspect.Parameter.KEYWORD_ONLY,
                annotation=typing.Optional[request_type],
                default=None,
            )
        )
    # Response type
    if inspect.isroutine(response_type):
        return_annotation = typing.get_type_hints(response_type).get("return")
    else:
        return_annotation = response_type

    func.__signature__ = inspect.Signature(
        parameters=parameters, return_annotation=return_annotation
    )


def _inject_docstring(
    func,
    method: str,
    path_template: str,
    path_params: Tuple[str, ...],
    request_type: Optional[Union[Type[BaseModel], List[Any]]],
    docstring: Optional[Docstring] = None,
):
    # Initial description section
    func_doc = f"Wrapper of the API endpoint: `{method.upper()} {path_template}`\n\n"
    if docstring:
        func_doc += docstring.doc + "\n\n"

    # Add params section
    params = []
    for path_param in path_params:
        description = ""
        if path_param == "kbid":
            description = "The id of the knowledge box"
        params.append(f":param {path_param}: {description}")
    if request_type is not None:
        if isinstance(request_type, type) and issubclass(request_type, BaseModel):
            for field in request_type.__fields__.values():
                params.append(
                    f":param {field.name}: {field.field_info.description or ''}"
                )
    func_doc += "\n".join(params)
    func_doc += "\n"

    # Add examples
    if docstring:
        for example in docstring.examples or []:
            description = example.description or ""
            code = example.code or ""
            func_doc += f"\n{description}\n\n{code}\n"
    func.__doc__ = func_doc
