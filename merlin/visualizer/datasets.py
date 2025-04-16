from fastapi import APIRouter, Request
from merlin.lib.utilities import search_for_stream, get_joule_node

router = APIRouter()


@router.get('/datasets')
def get_datasets(request: Request) -> dict:
    def find_default_node_name():
        with get_joule_node(request.app.node) as node:
            return node.name

    if request.app.node == '':
        joule_node_name = find_default_node_name()
    else:
        joule_node_name = request.app.node

    return {
        'joule_node': joule_node_name,
        'dataset_names': search_for_stream(request.app.node, 'events')
    }
