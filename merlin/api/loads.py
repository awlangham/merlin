from merlin.models import GenericLoad

def add_load(self, new_load: GenericLoad) -> None:
    with self.modify_config() as cf:
        cf['loads'][new_load.name] = new_load.to_json()

def remove_load(self, load_name: str) -> None:
    with self.modify_config() as cf:
        del cf['loads'][load_name]