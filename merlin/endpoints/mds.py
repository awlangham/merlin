from fastapi import APIRouter, Request
from merlin.unsupervised import mds_data

router = APIRouter()


@router.post('/mds')
async def mds(stream_name: str, request: Request):
    intervals = (await request.json())['intervals']
    transformed_data = await mds_data(stream_name, intervals)

    return {
        'data0': transformed_data[:, 0].tolist(),
        'data1': transformed_data[:, 1].tolist()
    }
