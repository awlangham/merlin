import json
from json.decoder import JSONDecodeError
from contextlib import contextmanager
from importlib.resources import files

import merlin


filename = str(files(merlin) / 'config.json')


@contextmanager
def config_file():
    """
    Context manager to update a Merlin
    configuration file.

    Example usage:
    with config_file() as cf:
        # modify cf as Python dictionary
    # file automatically saved and released
    # upon exiting the context manager
    """

    try:
        with open(filename) as f:
            config_json = json.load(f)
            yield config_json
    except FileNotFoundError:
        config_json = {}
        yield config_json
    finally:
        with open(filename, 'w') as f:
            json.dump(config_json, f, indent=4)
