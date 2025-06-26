import json

from merlin.installation import config_filename, CurrentInstallation


def new_installation(node, stream_name):
    with open(config_filename, 'w') as config_file:
        config = {}
        config['stream_name'] = stream_name
        json.dump(config, config_file, indent=4)

    return CurrentInstallation(node)
