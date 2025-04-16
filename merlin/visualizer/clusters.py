from fastapi import APIRouter, Request

from merlin.lib.inference.clustering import cluster_events

router = APIRouter()


@router.get('/clusters')
def get_clusters(stream_name: str, request: Request, start_ts: int = None, end_ts: int = None) -> dict:
    cluster_assignments = cluster_events(request.app.node, stream_name, start_ts, end_ts)[0]

    return {
        'cluster_assignments': cluster_assignments.tolist()
    }
