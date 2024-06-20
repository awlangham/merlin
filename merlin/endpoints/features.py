from fastapi import APIRouter, Request, Response
import orjson
from joule.utilities import timestamp_to_human as ts2h
from merlin.utilities import get_joule_node

router = APIRouter()


@router.get('/features')
async def features(request: Request, stream_name: str):
    async with get_joule_node(request.app.node) as node:
        # TODO: Fix limit parameter
        events = await node.event_stream_read(stream_name + '/events')

    if len(events) == 0:
        return {'range_start': None, 'range_end': None, 'events': []}

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
            'type': event.content['type'],
            'label': event.content['label'] if 'label' in event.content else None
        } for idx, event in enumerate(events)]
    }

    return Response(content=orjson.dumps(result))
