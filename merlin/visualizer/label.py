from fastapi import APIRouter, Request

from merlin.utilities import label_data


router = APIRouter()


@router.put('/label')
async def label(stream_name: str, request: Request) -> None:
    request_json = await request.json()
    intervals = request_json['intervals']
    label_name = request_json['label']

    await label_data(request.app.node, stream_name, intervals, label_name)
