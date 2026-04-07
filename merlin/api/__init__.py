import json
from importlib.resources import files
from pathlib import Path

from .installation import OfflineInstallation, RealTimeInstallation
import merlin

default_path = Path('/opt/configs')
config_filename = str(default_path / 'merlin.json') if default_path.exists() else str(files(merlin) / 'merlin.json')


def new_installation(stream_name, num_phases, node):
    with open(config_filename, 'w') as config_file:
        config = {}
        config['node'] = node
        config['stream_name'] = stream_name
        config['num_phases'] = num_phases
        config['method'] = 'unsupervised'
        json.dump(config, config_file, indent=4)


def get_installation():
    return OfflineInstallation(config_filename)

def run_installation(node):
    return RealTimeInstallation(config_filename, node)
