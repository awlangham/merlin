import click
import asyncio
from joule.utilities import human_to_timestamp as h2ts

from merlin.api import get_installation


@click.command('infer')
@click.option('--start', '-s', help='Timestamp or descriptive string', required=True)
@click.option('--end', '-e', help='Timestamp or descriptive string', required=True)
def infer(start: str, end: str) -> None:
    """
    Infer load identity and state change over [start, end].
    """

    try:
        start_ts, end_ts = h2ts(start), h2ts(end)
    except ValueError:
        click.echo('Invalid start/end time.')
        return

    matching_exemplar, match_score = asyncio.run(_infer(start_ts, end_ts))
    click.echo(f'Matching exemplar: {matching_exemplar}')
    click.echo(f'Match score: {match_score}')


async def _infer(start_ts, end_ts):
    installation = get_installation()
    data = await installation.get_transient(start_ts, end_ts)
    prep_data = data[:, 1:]
    # installation.close()

    return await installation.find_matching_exemplar(prep_data)
