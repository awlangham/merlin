from fastapi import APIRouter

from merlin.api import get_installation

router = APIRouter()


@router.get('/config')
def config() -> dict:
    config_json = get_installation().read_config()
    return config_json
