from hatchling.builders.hooks.plugin.interface import BuildHookInterface
import subprocess


class BuildFrontend(BuildHookInterface):
    def initialize(self, version, build_data):
        if version != 'editable':
            build_data['force_include'] = {
                "frontend/build": "merlin/static"
                # "docs/_build/html": "merlin/docs"
                }

        subprocess.run(args=['npm', 'install'], cwd='frontend', check=True)
        subprocess.run(args=['npm', 'run', 'build'], cwd='frontend', check=True)
