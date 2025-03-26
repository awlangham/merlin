from fastapi import APIRouter, Request, Response
import orjson
from joule.utilities import timestamp_to_human as ts2h
from merlin.utilities import get_joule_node, read_interval

router = APIRouter()


@router.get('/features')
async def features(request: Request, stream_name: str, start_ts: int = None, end_ts: int = None):
    # Invalidate LRU cache of transients
    read_interval.cache_clear()

    async with get_joule_node(request.app.node) as node:
        events = await node.event_stream_read(stream_name + '/events', limit=1000, start=start_ts, end=end_ts)

    result = {
        'events': [{
            'id': idx,
            'timestamp': ts2h(event.start_time),
            'start_ts': event.start_time,
            'end_ts': event.end_time,
            'Steady-State P': event.content['P_ss'],
            'Steady-State Q': event.content['Q_ss'],
            'Peak P': event.content['P_pk'],
            'Peak Q': event.content['Q_pk'],
            'type': event.content['type'] if 'type' in event.content else None,
            'load_family': event.content['load_family'] if 'load_family' in event.content else None,
            'label': event.content['label'] if 'label' in event.content else None
        } for idx, event in enumerate(events)]
    }

    return Response(content=orjson.dumps(result))
