from .aio.client import Client as NATS

async def connect(servers=..., **options) -> NATS: ...
