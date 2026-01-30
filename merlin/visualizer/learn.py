from fastapi import APIRouter, Request

from merlin.api import get_installation
from merlin.models import Exemplar

router = APIRouter()


@router.put('/learn')
async def label(start_ts: int, end_ts: int, exemplar_name: str, request: Request) -> None:
    load_name, transition = exemplar_name.split('::')
    state1, state2 = transition.split('->')

    new_exemplar = Exemplar(start_ts, end_ts, [[load_name, state1, state2]])

    current_installation = get_installation()
    current_installation.add_exemplar(new_exemplar)
