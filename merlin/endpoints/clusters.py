from fastapi import APIRouter, Request

# from merlin.unsupervised.clustering import cluster_data
from merlin.unsupervised.clustering import Clustering

router = APIRouter()


@router.get('/clusters')
def get_clusters(stream_name: str, request: Request):
    labels = Clustering(request.app.node, stream_name).labels

    return {
        'labels': labels.tolist()
    }
