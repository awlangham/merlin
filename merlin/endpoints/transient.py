from fastapi import APIRouter
from fastapi import Request

from merlin.utilities import get_joule_node

router = APIRouter()


@router.get('/transient')
async def transients(request: Request, stream_name: str, start_ts: int, end_ts: int):
    async with get_joule_node(request.app.node) as node:
        sarray = await node.data_read_array(stream_name + '/prep', start=start_ts, end=end_ts)

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
