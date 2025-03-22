from fastapi import APIRouter, Request, Response
import numpy as np
from io import BytesIO

from merlin.utilities import get_transients

router = APIRouter()


@router.post('/download')
async def download(stream_name: str, request: Request) -> Response:
    intervals = (await request.json())['intervals']
    transients = await get_transients(request.app.node, stream_name, intervals)
    ids = range(len(transients))

    buffer = BytesIO()
    transient_kwargs = {
        str(transient_id): transient for transient_id, transient in zip(ids, transients)}
    np.savez(buffer, **transient_kwargs)
    buffer.seek(0)

    headers = {'Content-Disposition': 'attachment;'}
    return Response(buffer.getvalue(), headers=headers, media_type='application/octet-stream')
