import click


from merlin.cli.learn.loads import learn_loads
from merlin.cli.learn.transients import learn_transients


@click.group()
def learn() -> None:  # pragma: no cover
    """
    Learn loads and transients.
    """
    pass


learn.add_command(learn_loads)
learn.add_command(learn_transients)
