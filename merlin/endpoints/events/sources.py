from fastapi import APIRouter
from merlin.utilities import search_for_stream

router = APIRouter()


@router.get('/events/sources')
def get_event_sources():
    return {
        'stream_names': search_for_stream('events')
    }
