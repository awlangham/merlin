from fastapi import APIRouter
from merlin.unsupervised import cluster_data

router = APIRouter()


@router.get('/clusters')
async def get_clusters(stream_name: str):
    labels, _ = await cluster_data(stream_name)

    return {
        'labels': labels.tolist()
    }
