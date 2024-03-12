from fastapi import APIRouter, Request

from nilmevents import get_connection

router = APIRouter()

# @router.get('/{event_set_name}/labels')
# async def labels(event_set_name: str, request: Request):
#     eventDB = request.app.eventDB
#     label_list = eventDB.get_labels(event_set_name)
#     return {
#         'label_list': label_list
#     }

@router.put('/{event_set_name}/label/{label_name}')
async def label(event_set_name: str, label_name: str, request: Request):
    eventDB = get_connection(event_set_name)
    ids = (await request.json())['ids']
    eventDB.label(ids, label_name)