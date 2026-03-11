from merlin.models import Exemplar


def add_exemplar(self, exemplar: Exemplar) -> None:
    with self.modify_config() as cf:
        cf['exemplars'].append(exemplar.to_json())


def remove_exemplar(self, index: int) -> None:
    # index starts at 1
    with self.modify_config() as cf:
        if index > len(cf['exemplars']) or index <= 0:
            raise IndexError(f'Invalid exemplar index {index}')

        del cf['exemplars'][index - 1]


def remove_exemplar_by_load(self, load_name: str) -> None:
    with self.modify_config() as cf:
        exemplars = cf['exemplars'].copy()

        for exemplar in exemplars:
            if exemplar['transitions'][0][0] == load_name:
                cf['exemplars'].remove(exemplar)


async def get_exemplar(self, load_name: str, state1: str, state2: str):
    """
    Find the exemplar corresponding to
    the transition load_name::state1->state2
    """

    cf = self.read_config()
    exemplars = cf['exemplars']

    for exemplar in exemplars:
        if exemplar['transitions'] == [[load_name, state1, state2]]:
            return await self.get_transient(exemplar['start_ts'], exemplar['end_ts'])
