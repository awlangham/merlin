import asyncio
from fastapi import APIRouter, Request
from merlin.utilities import search_for_stream, get_joule_node

router = APIRouter()


@router.get('/datasets')
async def get_datasets(request: Request) -> dict:
    if request.app.node == '':
        async with get_joule_node(request.app.node) as node:
            joule_node_name = node.name
    else:
        joule_node_name = request.app.node

    return {
        'joule_node': joule_node_name,
        'dataset_names': await search_for_stream(request.app.node, 'events')
    }
