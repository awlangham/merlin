from fastapi import APIRouter, Request
from merlin.unsupervised import cluster_data

router = APIRouter()


@router.get('/clusters')
async def get_clusters(stream_name: str, request: Request):
    labels, _ = await cluster_data(request.app.node, stream_name)

    return {
        'labels': labels.tolist()
    }
