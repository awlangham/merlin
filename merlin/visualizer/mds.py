from fastapi import APIRouter, Request
from merlin.unsupervised.mds import mds_data

router = APIRouter()


@router.post('/mds')
async def mds(stream_name: str, request: Request) -> dict:
    intervals = (await request.json())['intervals']
    transformed_data = await mds_data(request.app.node, stream_name, intervals)

    return {
        'data0': transformed_data[:, 0].tolist(),
        'data1': transformed_data[:, 1].tolist()
    }
