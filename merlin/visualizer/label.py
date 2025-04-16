import asyncio
from fastapi import APIRouter, Request
from merlin.lib.events import label_events


router = APIRouter()


@router.put('/label')
def label(stream_name: str, request: Request) -> None:
    request_json = asyncio.run(request.json())
    intervals = request_json['intervals']
    label_name = request_json['label']

    label_events(request.app.node, stream_name, intervals, label_name)
