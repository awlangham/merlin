import merlin
from importlib.resources import files


config_filename = str(files(merlin) / 'config.json')

from .current_installation import CurrentInstallation
from .new_installation import new_installation
