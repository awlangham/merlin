from fastapi import APIRouter
from fastapi import Request

from merlin.lib.transients import read_single_transient

router = APIRouter()


@router.get('/transient')
def transients(request: Request, stream_name: str, start_ts: int, end_ts: int) -> dict:
    sarray = read_single_transient(request.app.node, stream_name, start_ts, end_ts)

    timestamps, data = sarray[:, 0], sarray[:, 1:]
    timestamps -= timestamps[0]
    timestamps = timestamps / 1e6
    P = data[:, 0]
    Q = data[:, 1]

    return {
        'timestamps': timestamps.tolist(),
        'P': P.tolist(),
        'Q': Q.tolist()
    }
