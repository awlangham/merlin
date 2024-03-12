from fastapi import APIRouter

from merlin import get_node

router = APIRouter()


@router.get('/transient')
async def transients(stream_name: str, start_ts: int, end_ts: int):
    async with get_node() as node:
        pipe = await node.data_read(stream_name + '/prep', start=start_ts, end=end_ts)
        sarray = await pipe.read_all()

    timestamps, data = sarray['timestamp'], sarray['data']
    timestamps -= timestamps[0]
    timestamps = timestamps / 1e6
    P = data[:, 0] + data[:, 8] + data[:, 16]
    Q = data[:, 1] + data[:, 9] + data[:, 17]

    return {
        'timestamps': timestamps.tolist(),
        'P': P.tolist(),
        'Q': Q.tolist()
    }
