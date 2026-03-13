import asyncio
import click
from joule.api import get_node
from joule.utilities import human_to_timestamp as h2ts, timestamp_to_human as ts2h
from joule.api import Event, EventStream
from joule.errors import ApiError
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from scipy.signal import medfilt
from pymoo.core.problem import ElementwiseProblem
from pymoo.core.variable import Real, Integer
from pymoo.algorithms.moo.nsga2 import RankAndCrowdingSurvival
from pymoo.core.mixed import MixedVariableGA
from pymoo.core.termination import NoTermination

from merlin.cli.decorators import pass_node_name


def under_threshold(start, end, prep_to_use, threshold):
    data = prep_to_use[start:end]
    ranges = np.max(data, axis=0) - np.min(data, axis=0)
    return np.all(ranges < threshold)


def rolling_median(data, window):
    filtered = medfilt(data, [window, 1])
    bound = int(window / 2)
    return filtered[bound:-bound]


class LearnTransientsProblem(ElementwiseProblem):
    def __init__(self, data, min_load, output_stream, node_name, **kwargs):
        vars = {
            'threshold': Real(bounds=(0, min_load)),
            'median_half_length': Integer(bounds=(0, 10)),  # median_length = 2 * median_half_length + 1, so that it's an odd integer
            'flat_length': Integer(bounds=(5, 60))
        }
        super().__init__(vars=vars, n_obj=2, **kwargs)
        self.count = 1
        self.generation = 1
        self.output_stream = output_stream
        self.node_name = node_name

        self.timestamps = data[:, 0]
        self.prep = data[:, 1:]
        self.prep_len = {1: len(self.prep)}
        self.preps = {1: self.prep[:, (0, 1, 8, 9, 16, 17)]}
        self.ss_window_length = 5
        self.entire_ss_change = np.mean(self.prep[-self.ss_window_length:], axis=0) - np.mean(self.prep[:self.ss_window_length], axis=0)

    def get_prep(self, median_window_length):
        try:
            return self.preps[median_window_length]
        except KeyError:
            prep_fundamental = self.prep[:, (0, 1, 8, 9, 16, 17)]
            prep_filtered = rolling_median(prep_fundamental, median_window_length)
            self.prep_len[median_window_length] = len(prep_filtered)
            self.preps[median_window_length] = prep_filtered
            return self.preps[median_window_length]

    def _evaluate(self, X, out, *args, **kwargs):
        self.count += 1
        plot = kwargs.get('plot', False)
        relative_timestamps = self.timestamps - self.timestamps[0]
        relative_timestamps_h = relative_timestamps / (1e6 * 60 * 60)

        threshold = X['threshold']
        median_window = 2 * X['median_half_length'] + 1
        min_window_length = X['flat_length']

        prep_to_use = self.get_prep(median_window)
        prep_len = self.prep_len[median_window]

        mask = np.ones(prep_len)  # 0 is flat, 1 is not-flat

        def split(start, end):
            if end - start < min_window_length:
                return

            if under_threshold(start, end, prep_to_use, threshold):
                mask[start:end] = 0
                return

            split_index = (end - start) // 2 + start

            if (split_index - start) > min_window_length // 2 and (end - split_index) > min_window_length // 2:
                if under_threshold(split_index - min_window_length // 2, split_index + min_window_length // 2, prep_to_use, threshold):
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

        total_ss_change = 0
        transient_length = 0
        num_intervals = 0
        new_events = []
        for (start, end) in intervals:
            # If too close to the start/end of all the data, just discard
            if start < self.ss_window_length or end > prep_len - self.ss_window_length:
                continue

            transient_length += (end - start)
            num_intervals += 1

            if plot:
                event_content = {
                    'threshold': float(threshold),
                    'median_length': int(median_window),
                    'flat_length': int(min_window_length)
                }
                new_event = Event(start_time=self.timestamps[start + median_window // 2],
                                  end_time=self.timestamps[end + median_window // 2],
                                  content=event_content
                                  )
                new_events.append(new_event)
                plt.axvspan(relative_timestamps_h[start], relative_timestamps_h[min(end, len(relative_timestamps_h) - 1)], color='green', alpha=0.4)

            # Add [ss_window_length] points to start and end
            new_start, new_end = start - self.ss_window_length, end + self.ss_window_length

            ss_change = np.mean(self.prep[end:new_end], axis=0) - np.mean(self.prep[new_start:start], axis=0)
            total_ss_change += ss_change

        if plot:
            asyncio.run(self.write_events(new_events))

        loss_ss = np.linalg.norm(total_ss_change - self.entire_ss_change)

        output = np.array([loss_ss, transient_length])
        if num_intervals in [0, 1]:
            out['F'] = np.array([np.inf, np.inf])
        else:
            out['F'] = output

    async def write_events(self, events):
        try:
            node_handle = get_node(self.node_name)
            event_stream_name = f'g{self.generation}s{self.count}'
            event_stream_path = self.output_stream + '/learned/' + event_stream_name
            try:
                event_stream = await node_handle.event_stream_get(event_stream_path)
            except ApiError:
                new_stream = EventStream(name=event_stream_name)
                event_stream = await node_handle.event_stream_create(new_stream, self.output_stream + '/learned')
            await node_handle.event_stream_write(event_stream, events)
            await node_handle.close()
        except KeyboardInterrupt:
            await node_handle.close()


@click.command(name='transients')
@click.argument('stream_name')
@click.option('--smallest_load', '-l', help='Smallest step change of interest', type=float, required=True)
@click.option('--start', '-s', help='Timestamp or descriptive string', required=True)
@click.option('--end', '-e', help='Timestamp or descriptive string', required=True)
@pass_node_name
def learn_transients(node_name, stream_name, start, end, smallest_load):
    try:
        start_ts, end_ts = h2ts(start), h2ts(end)
        if start_ts >= end_ts:
            raise ValueError
    except ValueError:
        click.echo('Invalid start/end time.')
        return

    data = asyncio.run(_get_data(node_name, stream_name, h2ts(start), h2ts(end)))

    timestamps = data[:, 0] / 1e6 / 60
    timestamps -= timestamps[0]

    pop_size = 10

    algorithm = MixedVariableGA(pop_size=pop_size, survival=RankAndCrowdingSurvival())

    asyncio.run(_clear_learned_folder(node_name, stream_name))

    learn_transient_problem = LearnTransientsProblem(data, smallest_load, stream_name, node_name)
    algorithm.setup(learn_transient_problem, termination=NoTermination(), seed=1)

    click.echo(f'Optimizing over [ {ts2h(data[0, 0])}-> {ts2h(data[-1, 0])}]')
    click.echo(f'Saving to {stream_name}/learned')
    try:
        while algorithm.has_next():
            gen_number = algorithm.n_gen if algorithm.n_gen else 1
            click.echo(f'Generation {gen_number}')
            learn_transient_problem.generation = gen_number
            algorithm.next()

            # os.mkdir(f'{directory_name}/generation_{gen_number}')

            learn_transient_problem.count = 0
            best_X = algorithm.opt.get('X')
            click.echo(f'Found {len(best_X)} Pareto-optimal solutions')
            for x in best_X:
                learn_transient_problem._evaluate(x, {}, plot=True)
    except KeyboardInterrupt:
        return


async def _clear_learned_folder(node_name, stream_name):
    node_handle = get_node(node_name)
    try:
        await node_handle.folder_delete(stream_name + '/learned')
    except ApiError:
        pass
    await node_handle.close()


async def _get_data(node_name, stream_name, start_ts, end_ts):
    node_handle = get_node(node_name)
    pipe = await node_handle.data_read(stream_name + '/prep',
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

    await node_handle.close()
    return np.row_stack(data)
