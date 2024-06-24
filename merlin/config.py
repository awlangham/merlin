import json
from json.decoder import JSONDecodeError
from contextlib import contextmanager
from importlib.resources import files

import merlin


filename = str(files(merlin) / 'config.json')


@contextmanager
def config_file():
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
