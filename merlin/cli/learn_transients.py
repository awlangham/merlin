import asyncio
import click
from joule.api import get_node
from joule.utilities import human_to_timestamp as h2ts, timestamp_to_human as ts2h
import numpy as np
from scipy.optimize import minimize_scalar
import matplotlib.pyplot as plt
from tqdm import tqdm

from merlin.cli.decorators import pass_node_name

plt.rc('text', usetex=True)
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
plt.rcParams['font.size'] = 16
plt.rcParams['lines.linewidth'] = 3


@click.command(name='learn-transients')
@click.argument('prep_stream')
@click.option('--smallest_load', '-l', help='Smallest step change of interest', default=5000)
@click.option('--start', '-s', help='Timestamp or descriptive string', required=True)
@click.option('--end', '-e', help='Timestamp or descriptive string', required=True)
@pass_node_name
def learn_transients(node, prep_stream, start, end, smallest_load):
    min_window_length = 10
    ss_window_length = 5

    data = asyncio.run(_get_data(node, prep_stream, h2ts(start), h2ts(end)))

    click.echo(f'Optimizing over [ {ts2h(data[0, 0])}-> {ts2h(data[-1, 0])}]')

    timestamps = data[:, 0] / 1e6 / 60
    timestamps -= timestamps[0]
    P_total = data[:, 1] + data[:, 9] + data[:, 17]

    entire_ss_change = np.mean(P_total[-ss_window_length:]) - np.mean(P_total[:ss_window_length])

    def evaluate_threshold(threshold, plot=False):
        mask = np.ones(P_total.shape)  # 0 is flat, 1 is not-flat

        sum_of_flat_ranges = 0

        def split(start, end):
            nonlocal sum_of_flat_ranges

            if end - start < min_window_length:
                return

            x = P_total[start:end]

            if np.max(x) - np.min(x) < threshold:
                # if compute_range(prep[start:end]) < threshold:
                mask[start:end] = 0
                sum_of_flat_ranges += np.max(x) - np.min(x)
                return

            x_summed = np.cumsum(x - np.min(x))
            split_index = np.searchsorted(x_summed, x_summed[-1] / 2) + start
            # split_index = len(x) // 2 + start

            if (split_index - start) > min_window_length // 2 and (end - split_index) > min_window_length // 2:
                window_around_split = P_total[split_index - min_window_length // 2: split_index + min_window_length // 2]
                if np.max(window_around_split) - np.min(window_around_split) > threshold:
                    # This split is in the middle of something interesting
                    split_index -= min_window_length // 2

            # Make sure we don't split degeneratively
            if split_index == start:
                split_index += 1

            if split_index == end:
                split_index -= 1

            split(start, split_index)
            split(split_index, end)

        split(0, len(P_total))

        flat_changes = np.diff(np.pad(mask, 1))  # 1 means we went from flat to not-flat, -1 means we went from not-flat to flat
        intervals = list(zip(np.where(flat_changes == 1)[0], np.where(flat_changes == -1)[0]))

        if plot:
            plt.figure(tight_layout=True)
            plt.plot(timestamps, P_total / 1e3)

        total_ss_change = 0
        for (start, end) in intervals:
            # If too close to the start/end of all the data, just discard
            if start < ss_window_length or end > len(P_total) - ss_window_length:
                continue

            if plot:
                plt.axvspan(timestamps[start], timestamps[min(end, len(timestamps) - 1)], color='green', alpha=0.4)

            # Add [ss_window_length] points to start and end
            new_start, new_end = start - ss_window_length, end + ss_window_length

            ss_change = np.mean(P_total[end:new_end]) - np.mean(P_total[new_start:start])
            total_ss_change += ss_change

        if plot:
            f0 = 1 / ((timestamps[1] - timestamps[0]) * 60)
            T = 1e3 * min_window_length / f0

            plt.title(f'k = {round(threshold)} W, T = {round(T)} ms')
            plt.xlabel('Time (min)')
            plt.ylabel('Total Real Power (kW)')
            plt.xlim(timestamps[0], timestamps[-1])
            plt.show()

        return np.abs(total_ss_change - entire_ss_change) + sum_of_flat_ranges

    result = minimize_scalar(evaluate_threshold, bounds=(0, smallest_load))
    click.echo(result)

    evaluate_threshold(result.x, plot=True)


async def _get_data(node, prep_stream, start_ts, end_ts):
    node = get_node(node)
    pipe = await node.data_read(prep_stream,
                                start=start_ts,
                                end=end_ts
                                )
    estimated_num_rows = round(60 * (end_ts - start_ts) / 1e6)

    data = []
    with tqdm(total=estimated_num_rows, desc='Loading data', unit='rows') as pbar:
        while not await pipe.is_empty():
            batch = await pipe.read(flatten=True)
            data.append(batch)
            pipe.consume(len(batch))
            pbar.update(len(batch))

    await node.close()
    return np.row_stack(data)
