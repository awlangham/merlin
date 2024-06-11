import click
import webbrowser
# from os.path import isfile
from importlib.resources import files

import merlin


@click.command('docs')
def docs() -> None:
    """
    Open Merlin documentation in the default browser.
    """

    installed_path = str(files(merlin)) + '/docs/index.html'
    # dev_path = str(files(merlin).parent / 'docs/_build/html/index.html')

    
    # if isfile(installed_path):
    webbrowser.open('file://' + installed_path)
    # elif isfile(dev_path):
        # Fall back to dev directory structure
        # webbrowser.open('file://' + dev_path)
