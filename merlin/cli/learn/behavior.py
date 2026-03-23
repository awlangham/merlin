import click
import asyncio
from joule.utilities import human_to_timestamp as h2ts

from merlin.api import get_installation


@click.command('behavior')
@click.option('--start', '-s', help='Timestamp or descriptive string', required=True)
@click.option('--end', '-e', help='Timestamp or descriptive string', required=True)
@click.argument('load_name')
def learn_behavior(start, end, load_name) -> None:
    try:
        start_ts, end_ts = h2ts(start), h2ts(end)
        if start_ts >= end_ts:
            raise ValueError
    except ValueError:
        click.echo('Invalid start/end time.')
        return

    installation = get_installation()
    asyncio.run(installation.learn_behavior(start_ts, end_ts, load_name))
    installation.close()
