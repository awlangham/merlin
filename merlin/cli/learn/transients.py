import asyncio
import click
from joule.api import get_node
from joule.utilities import human_to_timestamp as h2ts, timestamp_to_human as ts2h
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from scipy.signal import medfilt
from pymoo.core.problem import ElementwiseProblem
from pymoo.core.variable import Real, Integer
from pymoo.algorithms.moo.nsga2 import RankAndCrowdingSurvival
from pymoo.core.mixed import MixedVariableGA
from pymoo.optimize import minimize
from pymoo.core.termination import NoTermination
from segment_tree import SegmentTree
import os
from datetime import datetime
import matplotlib

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
    def __init__(self, data, min_load, output_directory, **kwargs):
        vars = {
            'threshold': Real(bounds=(0, min_load)),
            'median_half_length': Integer(bounds=(0, 10)),  # median_length = 2 * median_half_length + 1, so that it's an odd integer
            'flat_length': Integer(bounds=(5, 60))
        }
        super().__init__(vars=vars, n_obj=2, **kwargs)
        self.count = 1
        self.generation = 1
        self.directory_name = output_directory

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
            prep_fundamental = self.prep[:, (0, 1, 8, 9, 16, 17)]
            prep_filtered = rolling_median(prep_fundamental, median_window_length)
            self.prep_len[median_window_length] = len(prep_filtered)
            self.prep_trees[median_window_length] = [SegmentTree(prep_filtered[:, i]) for i in range(prep_filtered.shape[1])]
            return self.prep_trees[median_window_length]

    def _evaluate(self, X, out, *args, **kwargs):
        self.count += 1
        plot = kwargs.get('plot', False)
        relative_timestamps = self.timestamps - self.timestamps[0]
        relative_timestamps_h = relative_timestamps / (1e6 * 60 * 60)

        threshold = X['threshold']
        median_window = 2 * X['median_half_length'] + 1
        min_window_length = X['flat_length']

        # print(threshold, median_window, min_window_length)

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
            plt.xlabel('Time (hr.)')
            plt.ylabel('Real Power (kW)')
            plt.xlim(relative_timestamps_h[0], relative_timestamps_h[-1])
            plt.legend(loc='upper right')
            plt.savefig(f'{self.directory_name}/generation_{self.generation}/solution_{self.count}.pdf')
            plt.close()

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

    matplotlib.use('Agg')

    data = asyncio.run(_get_data(node, prep_stream, h2ts(start), h2ts(end)))

    timestamps = data[:, 0] / 1e6 / 60
    timestamps -= timestamps[0]

    pop_size = 10

    # initial_thresholds = np.linspace(0, smallest_load, pop_size + 1)[1:]
    # initial_median_lengths = np.zeros(pop_size)
    # initial_flat_lengths = np.linspace(5, 60, pop_size)
    # initial_population = np.column_stack((initial_thresholds, initial_median_lengths, initial_flat_lengths))

    algorithm = MixedVariableGA(pop_size=pop_size, survival=RankAndCrowdingSurvival())

    directory_name = f'optimization_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    os.mkdir(directory_name)

    learn_transient_problem = LearnTransientsProblem(data, smallest_load, directory_name)
    algorithm.setup(learn_transient_problem, termination=NoTermination(), seed=1)

    click.echo(f'Optimizing over [ {ts2h(data[0, 0])}-> {ts2h(data[-1, 0])}]')
    click.echo(f'Saving to {directory_name}')
    try:
        while algorithm.has_next():
            gen_number = algorithm.n_gen if algorithm.n_gen else 1
            print(f'Gen {gen_number}')
            learn_transient_problem.generation = gen_number
            algorithm.next()

            os.mkdir(f'{directory_name}/generation_{gen_number}')

            learn_transient_problem.count = 0
            best_X = algorithm.opt.get('X')
            for x in best_X:
                learn_transient_problem._evaluate(x, {}, plot=True)
    except KeyboardInterrupt:
        os._exit(130)
        # best_F = algorithm.opt.get('F')
        # best_X = algorithm.opt.get('X')

    # print('Results:')
    # for x in best_X:
    #     print(x)

    # plt.figure(tight_layout=True)
    # plt.scatter(best_F[:, 0], best_F[:, 1] / (h2ts(end) - h2ts(start)))
    # plt.xlabel('Total Delta P error')
    # plt.ylabel('Transient fraction of data')

    # for x in best_X:
    #     learn_transient_problem._evaluate(x, {}, plot=True)


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
