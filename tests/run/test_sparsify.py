import numpy as np
import asyncio
import argparse
from joule.models.pipes import LocalPipe
from joule.utilities import human_to_timestamp as h2ts
from tabulate import tabulate
from unittest.mock import patch, Mock
import pytest

from merlin.run.sparsify import Sparsifier


start_ts = h2ts('01/01/2024 00:00')
end_ts = h2ts('01/01/2024 00:20')


def make_test_data(load_sequence, number_of_transitions):
    """
    Generate a set of 3-phase load transitions in
    steady-state real power.

    Returns a (N, 25)-shaped NumPy array and a dictionary
    containing each transition's number of occurences.
    """

    fs = 60

    timestamps = np.arange(start_ts, end_ts, 1e6 / fs)
    num_rows = len(timestamps)
    num_prep_columns = 24

    run_indices = np.linspace(0, num_rows, number_of_transitions + 1, endpoint=False, dtype=int)[1:]
    prep_data_diff = np.zeros((num_rows, num_prep_columns))

    generated_runs = {load_power: 0 for load_power in load_sequence}
    current_load_index = 0
    for run in run_indices:
        prep_data_diff[run, (0, 8, 16)] = load_sequence[current_load_index]
        generated_runs[load_sequence[current_load_index]] += 1
        current_load_index = (current_load_index + 1) % len(load_sequence)

    prep_data = np.cumsum(prep_data_diff, axis=0)
    return np.column_stack((timestamps, prep_data)), generated_runs


class FakeNode:
    def __init__(self):
        self.events = []

    async def event_stream_get(self, stream_path):
        fake_event_stream = Mock()
        fake_event_stream.id = ''
        return fake_event_stream

    async def event_stream_write(self, stream_name, events):
        self.events += events


class FakeInstallation():
    def __init__(self):
        self.num_phases = 3
        self.method = 'unsupervised'


@pytest.mark.asyncio
async def test_sparsify():
    """
    Local composite test of NILM edge detector and Merlin event processor.

    make_test_data -> [prep] -> EdgeDetector -> [transients] -> TestEventProcessor -> [events]
    """

    load1_power = 1000
    load2_power = 2000
    load3_power = 3000
    load4_power = 4000
    load_sequence = [load1_power, load2_power, load3_power, -load1_power, -load3_power, -load2_power, load4_power, -load4_power]

    original_consume = LocalPipe.consume

    def patched_consume(self, num_rows):
        original_consume(self, num_rows)
        self.reread_last()

    LocalPipe.consume = patched_consume

    test_prep_pipe = LocalPipe(name='prep', layout='float32_24')
    test_transients_pipe = LocalPipe(name='transients', layout='float32_24')

    print('Generating data...')
    test_data, generated_runs = make_test_data(load_sequence, number_of_transitions=60)

    test_prep_pipe.write_nowait(test_data)

    sparsifier = Sparsifier()
    fake_node = FakeNode()
    sparsifier.node = fake_node
    args = argparse.Namespace(
        pipes='unset',
        min_window_length=15,
        threshold=100,
        output=''
    )

    with patch('merlin.run.sparsify.run_installation', return_value=FakeInstallation()):
        # Run TestEventProcessor until we run out of data (causing a timeout)
        try:
            async with asyncio.timeout(1):
                await sparsifier.run(args, {'prep': test_prep_pipe}, {'transients': test_transients_pipe})
        except TimeoutError:
            pass

    num_events_found = len(fake_node.events)

    # Go through events and make sure that we have as many as we expected
    print('Analyzing output...')
    runs = {load_power: 0 for load_power in load_sequence}
    for event in fake_node.events:
        for load_power in load_sequence:
            if np.isclose(event.content['P_ss'] / 3, load_power):
                runs[load_power] += 1
                break

    runs_table = []
    passed_all_tests = True
    for load_power in load_sequence:
        passed_test = (runs[load_power] == generated_runs[load_power])
        if not passed_test:
            passed_all_tests = False

        passed_test_string = 'True ✅' if passed_test else 'False ❌'
        runs_table.append((load_power, runs[load_power], generated_runs[load_power], passed_test_string))

    passed_all_tests_string = 'True ✅' if passed_all_tests else 'False ❌'
    runs_table.append(('Total', num_events_found, sum(generated_runs.values()), passed_all_tests_string))
    headers = ('Load', 'Num. Found', 'Num. Expected', 'Test passed?')
    print(tabulate(runs_table, headers=headers, tablefmt='fancy_grid'))

    assert passed_all_tests
