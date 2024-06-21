import click
import webbrowser
# from os.path import isfile
from importlib.resources import files


@click.command('docs')
def docs() -> None:
    """
    Open Merlin documentation in the default browser.
    """

    import merlin

    installed_path = str(files(merlin)) + '/docs/index.html'
    # dev_path = str(files(merlin).parent / 'docs/_build/html/index.html')

    # if isfile(installed_path):
    webbrowser.open('file://' + installed_path)
    # elif isfile(dev_path):
    # Fall back to dev directory structure
    # webbrowser.open('file://' + dev_path)
