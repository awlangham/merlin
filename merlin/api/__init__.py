import json

from .installation import OfflineInstallation, RealTimeInstallation
import merlin
from importlib.resources import files


config_filename = str(files(merlin) / 'config.json')


def new_installation(stream_name, num_phases, node):
    with open(config_filename, 'w') as config_file:
        config = {}
        config['node'] = node
        config['stream_name'] = stream_name
        config['num_phases'] = num_phases
        config['mode'] = 'unsupervised'
        json.dump(config, config_file, indent=4)


def get_installation():
    return OfflineInstallation(config_filename)

def run_installation(node):
    return RealTimeInstallation(config_filename, node)
