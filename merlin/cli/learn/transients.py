import asyncio
import click
from joule.api import get_node
from joule.utilities import human_to_timestamp as h2ts, timestamp_to_human as ts2h
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from tqdm import tqdm
from scipy.signal import medfilt
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter
from segment_tree import SegmentTree

from merlin.cli.decorators import pass_node_name

# plt.rc('text', usetex=True)
# plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
# plt.rcParams['font.size'] = 16
# plt.rcParams['lines.linewidth'] = 3


def under_threshold(start, end, prep_trees, threshold):
    for tree in prep_trees:
        minimum = tree.query(start, end, 'min')
        maximum = tree.query(start, end, 'max')
        if (maximum - minimum) >= threshold:
            return False

    return True


def rolling_median(data, window):
    filtered = medfilt(data, [window, 1])
    bound = int(window / 2)
    return filtered[bound:-bound]


class LearnTransientsProblem(ElementwiseProblem):
    def __init__(self, data, min_load):
        super().__init__(
            n_var=3, # threshold, median filter length, flat window length
            n_obj=2, # residual sum of delta ss, total duration of transients
            xl=[0, 0, 5],
            xu=[min_load, 10, 60]
        )

        self.timestamps = data[:, 0]
        self.prep = data[:, 1:]
        self.prep_len = {1: len(self.prep)}
        self.prep_trees = {1: [SegmentTree(self.prep[:, i]) for i in [0, 1, 8, 9, 16, 17]]}
        self.ss_window_length = 5
        self.entire_ss_change = np.mean(self.prep[-self.ss_window_length:], axis=0) - np.mean(self.prep[:self.ss_window_length], axis=0)

    def get_prep_trees(self, median_window_length):
        try:
            return self.prep_trees[median_window_length]
        except KeyError:
            prep_filtered = rolling_median(self.prep, median_window_length)
            self.prep_len[median_window_length] = len(prep_filtered)
            self.prep_trees[median_window_length] = [SegmentTree(prep_filtered[:, i]) for i in [0, 1, 8, 9, 16, 17]]
            return self.prep_trees[median_window_length]

    def _evaluate(self, x, out, *args, **kwargs):
        plot = kwargs.get('plot', False)
        relative_timestamps = self.timestamps - self.timestamps[0]
        relative_timestamps_h = relative_timestamps / (1e6 * 60 * 60)

        threshold = x[0]
        median_window = 2 * round(x[1]) + 1
        min_window_length = round(x[2])

        print(threshold, median_window, min_window_length)

        prep_trees = self.get_prep_trees(median_window)
        prep_len = self.prep_len[median_window]

        mask = np.ones(prep_len)  # 0 is flat, 1 is not-flat

        def split(start, end):
            if end - start < min_window_length:
                return

            if under_threshold(start, end, prep_trees, threshold):
                mask[start:end] = 0
                return

            split_index = (end - start) // 2 + start

            if (split_index - start) > min_window_length // 2 and (end - split_index) > min_window_length // 2:
                if under_threshold(split_index - min_window_length // 2, split_index + min_window_length // 2, prep_trees, threshold):
                    # This split is in the middle of something interesting
                    split_index -= min_window_length // 2

            # Make sure we don't split degeneratively
            if split_index == start:
                split_index += 1

            if split_index == end:
                split_index -= 1

            split(start, split_index)
            split(split_index, end)

        split(0, prep_len - 1)

        flat_changes = np.diff(np.pad(mask, 1))  # 1 means we went from flat to not-flat, -1 means we went from not-flat to flat
        intervals = list(zip(np.where(flat_changes == 1)[0], np.where(flat_changes == -1)[0]))

        if plot:
            plt.figure(tight_layout=True)
            plt.plot(relative_timestamps_h, self.prep[:,  0] / 1e3, label='A')
            plt.plot(relative_timestamps_h, self.prep[:,  8] / 1e3, label='B')
            plt.plot(relative_timestamps_h, self.prep[:, 16] / 1e3, label='C')

        total_ss_change = 0
        transient_length = 0
        num_intervals = 0
        for (start, end) in intervals:
            # If too close to the start/end of all the data, just discard
            if start < self.ss_window_length or end > prep_len - self.ss_window_length:
                continue

            transient_length += (end - start)
            num_intervals += 1

            if plot:
                plt.axvspan(relative_timestamps_h[start], relative_timestamps_h[min(end, len(relative_timestamps_h) - 1)], color='green', alpha=0.4)

            # Add [ss_window_length] points to start and end
            new_start, new_end = start - self.ss_window_length, end + self.ss_window_length

            ss_change = np.mean(self.prep[end:new_end], axis=0) - np.mean(self.prep[new_start:start], axis=0)
            total_ss_change += ss_change

        if plot:
            plt.title(f'R = {round(threshold)} W, M = {median_window}, N = {min_window_length}')
            plt.xlabel('Time (min)')
            plt.ylabel('Real Power (kW)')
            plt.xlim(relative_timestamps_h[0], relative_timestamps_h[-1])
            plt.legend()
            plt.show()

        loss_ss = np.linalg.norm(total_ss_change - self.entire_ss_change)

        output = np.array([loss_ss, transient_length])
        if num_intervals in [0, 1]:
            out['F'] = np.array([np.inf, np.inf])
        else:
            out['F'] = output


@click.command(name='transients')
@click.argument('prep_stream')
@click.option('--smallest_load', '-l', help='Smallest step change of interest', type=float, required=True)
@click.option('--start', '-s', help='Timestamp or descriptive string', required=True)
@click.option('--end', '-e', help='Timestamp or descriptive string', required=True)
@pass_node_name
def learn_transients(node, prep_stream, start, end, smallest_load):
    try:
        start_ts, end_ts = h2ts(start), h2ts(end)
        if start_ts >= end_ts:
            raise ValueError
    except ValueError:
        click.echo('Invalid start/end time.')
        return

    data = asyncio.run(_get_data(node, prep_stream, h2ts(start), h2ts(end)))

    click.echo(f'Optimizing over [ {ts2h(data[0, 0])}-> {ts2h(data[-1, 0])}]')

    timestamps = data[:, 0] / 1e6 / 60
    timestamps -= timestamps[0]

    # if data.shape[1] == 25:
    #     P_total = data[:, 1] + data[:, 9] + data[:, 17]
    # elif data.shape[1] == 9:
    #     P_total = data[:, 1]
    # else:
    #     raise ValueError(f'Invalid number of columns: {data.shape[1]}')

    algorithm = NSGA2(pop_size=20)

    learn_transient_problem = LearnTransientsProblem(data, smallest_load)

    res = minimize(
        learn_transient_problem,
        algorithm,
        termination=('n_gen', 10),
        seed=1,
        verbose=True
    )

    Scatter().add(res.F).show()

    for x in res.X:
        learn_transient_problem._evaluate(x, {}, plot=True)


async def _get_data(node, prep_stream, start_ts, end_ts):
    node = get_node(node)
    pipe = await node.data_read(prep_stream,
                                start=start_ts,
                                end=end_ts
                                )
    estimated_num_rows = round(60 * (end_ts - start_ts) / 1e6)

    data = []
    with tqdm(total=estimated_num_rows, desc='Loading data', unit=' rows') as pbar:
        while not await pipe.is_empty():
            batch = await pipe.read(flatten=True)
            data.append(batch)
            pipe.consume(len(batch))
            pbar.update(len(batch))

    await node.close()
    return np.row_stack(data)
