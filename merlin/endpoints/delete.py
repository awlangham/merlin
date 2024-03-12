from fastapi import APIRouter

from nilmevents import get_connection

router = APIRouter(prefix='/delete')


@router.get('/{event_set_name}/{event_id}')
async def delete(event_set_name: str, event_id: int):
    get_connection(event_set_name).delete(event_id)
