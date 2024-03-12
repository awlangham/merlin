from fastapi import APIRouter, Request, Response
import numpy as np
from io import BytesIO

from nilmevents import get_connection

router = APIRouter(prefix='/download')


@router.post('/{event_set_name}')
async def download(event_set_name: str, request: Request):
    ids = (await request.json())['ids']
    ids.sort()

    eventDB = get_connection(event_set_name)    
    transients = eventDB.get_multiple_transients(ids)

    buffer = BytesIO()
    transient_kwargs = {
        str(transient_id): transient for transient_id, transient in zip(ids, transients)}
    np.savez(buffer, **transient_kwargs)
    buffer.seek(0)

    headers = {'Content-Disposition': 'attachment;'}
    return Response(buffer.getvalue(), headers=headers, media_type='application/octet-stream')
