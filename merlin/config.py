import json
from json.decoder import JSONDecodeError
from contextlib import contextmanager


def config_filename(dataset_name):
    return dataset_name[1:].replace('/', '_').replace(' ', '_') + '.merlin'


@contextmanager
def config_file(filename):
    """
    Context manager to manage a load file.
    """

    try:
        with open(filename) as f:
            loads_json = json.load(f)
            yield loads_json
    except (FileNotFoundError, JSONDecodeError):
        loads_json = {}
        yield loads_json
    finally:
        with open(filename, 'w') as f:
            json.dump(loads_json, f, indent=4)
