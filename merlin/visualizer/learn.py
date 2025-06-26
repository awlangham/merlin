from fastapi import APIRouter, Request

from merlin.api import Installation
from merlin.models import Exemplar

router = APIRouter()


@router.put('/learn')
async def label(start_ts: int, end_ts: int, exemplar_name: str, request: Request) -> None:
    load_name, transition = exemplar_name.split('::')
    state1, state2 = transition.split('->')

    new_exemplar = Exemplar()
    new_exemplar.start_ts = start_ts
    new_exemplar.end_ts = end_ts
    new_exemplar.transitions = [[load_name, state1, state2]]

    current_installation = Installation(request.app.node)
    current_installation.add_exemplar(new_exemplar)
