from fastapi import APIRouter, Request
from merlin.utilities import search_for_stream

router = APIRouter()


@router.get('/datasets')
def get_datasets(request: Request):
    return {
        'dataset_names': search_for_stream(request.app.node, 'events')
    }
