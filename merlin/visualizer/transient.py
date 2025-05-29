from fastapi import APIRouter
from fastapi import Request, Response

from merlin.utilities import read_interval

router = APIRouter()


@router.get('/transient')
async def transients(request: Request, response: Response, stream_name: str, start_ts: int, end_ts: int) -> dict:
    sarray = await read_interval(request.app.node, stream_name, start_ts, end_ts)

    timestamps, data = sarray[:, 0], sarray[:, 1:]
    timestamps -= timestamps[0]
    timestamps = timestamps / 1e6
    P = data[:, 0] + data[:, 8] + data[:, 16]
    Q = data[:, 1] + data[:, 9] + data[:, 17]

    response.headers['cache-control'] = 'max-age=3600'
    return {
        'timestamps': timestamps.tolist(),
        'P': P.tolist(),
        'Q': Q.tolist()
    }
