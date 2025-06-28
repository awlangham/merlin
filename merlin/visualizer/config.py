from fastapi import APIRouter

from merlin.api import Installation

router = APIRouter()


@router.get('/config')
def config() -> dict:
    with Installation(None).config() as cf:
        config_json = cf

    return config_json
