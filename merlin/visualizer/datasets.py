import asyncio
from fastapi import APIRouter, Request
from merlin.utilities import search_for_stream, get_joule_node

router = APIRouter()


@router.get('/datasets')
def get_datasets(request: Request) -> dict:
    async def find_default_node_name():
        async with get_joule_node(request.app.node) as node:
            return node.name

    if request.app.node == '':
        joule_node_name = asyncio.run(find_default_node_name())
    else:
        joule_node_name = request.app.node

    return {
        'joule_node': joule_node_name,
        'dataset_names': search_for_stream(request.app.node, 'events')
    }
