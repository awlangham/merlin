from fastapi import APIRouter

from merlin.api import Installation

router = APIRouter()


@router.get('/config')
def config() -> dict:
    config_json = Installation(None).read_config()
    return config_json
