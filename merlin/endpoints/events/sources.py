from fastapi import APIRouter
from merlin import list_event_sources

router = APIRouter()


@router.get('/events/sources')
def get_event_sources():
    return {
        'stream_names': list_event_sources()
    }
