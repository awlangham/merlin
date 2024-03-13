from fastapi import APIRouter
from merlin.utilities import search_for_stream

router = APIRouter()


@router.get('/datasets')
def get_datasets():
    return {
        'dataset_names': search_for_stream('events')
    }
