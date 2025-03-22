from fastapi import APIRouter, Request

from merlin.unsupervised.clustering import Clustering

router = APIRouter()


@router.get('/clusters')
def get_clusters(stream_name: str, request: Request, start_ts: int = None, end_ts: int = None) -> dict:
    cluster_assignments = Clustering(request.app.node, stream_name, start_ts, end_ts).cluster_assignments

    return {
        'cluster_assignments': cluster_assignments.tolist()
    }
