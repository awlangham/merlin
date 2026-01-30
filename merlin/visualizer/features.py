from fastapi import APIRouter, Request, Response
import orjson
from joule.utilities import timestamp_to_human as ts2h

from merlin.utilities import get_joule_node

router = APIRouter()


@router.get('/features')
async def features(request: Request, stream_name: str, start_ts: int = None, end_ts: int = None) -> Response:
    async with get_joule_node(request.app.node) as node:
        events = await node.event_stream_read_list(stream_name + '/events', limit=1500, start=start_ts, end=end_ts)
        stream = await node.data_stream_get(stream_name + '/transients')
    
    num_phases = 3 if len(stream.elements) == 24 else 1
    if num_phases == 3:
        result = {
            'num_phases': num_phases,
            'events': [{
                'id': idx,
                'timestamp': ts2h(event.start_time),
                'start_ts': event.start_time,
                'end_ts': event.end_time,
                'Total Steady-State P': event.content['P_ss'],
                'Total Steady-State Q': event.content['Q_ss'],
                'A Steady-State P': event.content['PA_ss'],
                'A Steady-State Q': event.content['QA_ss'],
                'B Steady-State P': event.content['PB_ss'],
                'B Steady-State Q': event.content['QB_ss'],
                'C Steady-State P': event.content['PC_ss'],
                'C Steady-State Q': event.content['QC_ss'],
                'Total Peak P': event.content['P_pk'],
                'Total Peak Q': event.content['Q_pk'],
                'ZS in-phase': event.content['I0_i'],
                'ZS quadrature': event.content['I0_q'],
                'type': event.content['type'] if 'type' in event.content else None,
                'load_family': event.content['load_family'] if 'load_family' in event.content else None,
                'label': event.content['label'] if 'label' in event.content else None
            } for idx, event in enumerate(events)]
        }
    else:
        result = {
            'num_phases': num_phases,
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
