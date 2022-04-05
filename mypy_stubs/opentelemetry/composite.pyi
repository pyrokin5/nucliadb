import typing
from opentelemetry.context.context import Context as Context
from opentelemetry.propagators import textmap
from typing import Any

logger: Any

class CompositePropagator(textmap.TextMapPropagator):
    def __init__(self, propagators: typing.Sequence[textmap.TextMapPropagator]) -> None: ...
    def extract(self, carrier: textmap.CarrierT, context: typing.Optional[Context] = ..., getter: textmap.Getter = ...) -> Context: ...
    def inject(self, carrier: textmap.CarrierT, context: typing.Optional[Context] = ..., setter: textmap.Setter = ...) -> None: ...
    @property
    def fields(self) -> typing.Set[str]: ...

class CompositeHTTPPropagator(CompositePropagator): ...
