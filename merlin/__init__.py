import joule
from contextlib import asynccontextmanager


@asynccontextmanager
async def get_node():
    node = joule.api.get_node()
    try:
        yield node
    finally:
        await node.close()
