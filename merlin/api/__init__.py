import merlin
from importlib.resources import files


config_filename = str(files(merlin) / 'config.json')

from .installation import Installation
from .new_installation import new_installation
