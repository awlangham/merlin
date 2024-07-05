from merlin.config import config_file
from merlin.utilities import read_interval


async def load_exemplar(load_name, state1, state2):
    with config_file() as cf:
        exemplars = cf['exemplars']
        stream_name = cf['stream_name']

    for exemplar in exemplars:
        if exemplar['transitions'] == [[load_name, state1, state2]]:
            return await read_interval('', stream_name, exemplar['start_ts'], exemplar['end_ts'])


class CurrentInstallation:
    def get_load_names(self) -> list:
        with config_file() as cf:
            return list(cf['loads'].keys())
