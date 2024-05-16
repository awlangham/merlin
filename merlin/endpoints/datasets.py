from fastapi import APIRouter, Request
from merlin.utilities import search_for_stream, connection_info

router = APIRouter()


@router.get('/datasets')
def get_datasets(request: Request):
    return {
        'joule_node': connection_info(request.app.node),
        'dataset_names': search_for_stream(request.app.node, 'events')
    }
