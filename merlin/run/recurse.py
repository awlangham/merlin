import asyncio
from joule.api import get_node
from joule.utilities import timestamp_to_human as ts2h, human_to_timestamp as h2ts
import numpy as np
from scipy.optimize import minimize_scalar

import matplotlib.pyplot as plt

from time import time

min_window_length = 10
# threshold = 1500


def compute_range(window):
    min_values = np.min(window, axis=0)
    max_values = np.max(window, axis=0)
    ranges = max_values - min_values
    return np.max(ranges)


async def main():
    node = get_node()

    # pipe = await node.data_read('/USCG William Chadwick/Port/prep',
    #                             start=h2ts('07:44:00 05/18/2025'),
    #                             end=h2ts('10:50 05/18/2025'),
    #                             max_rows=int(1e6))

    # pipe = await node.data_read('/meter1/prep',
    #                             start=h2ts('01/13/2026 00:00'),
    #                             end=h2ts('01/14/2026 00:00'),
    #                             max_rows=int(1e6))

    pipe = await node.data_read('/USCG Sturgeon/Port/prep',
                                # start=1745052388280000,
                                # end=1745080434717000,

                                start=1746436340023000,
                                end=1746466469620000,
                                max_rows=int(1e6))

    data = await pipe.read_all(flatten=True, error_on_overflow=True, maxrows=int(1e6))

    timestamps = data[:, 0] / 1e6 / 60
    timestamps -= timestamps[0]
    P_total = data[:, 1] + data[:, 9] + data[:, 17]

    entire_ss_change = np.mean(P_total[-5:]) - np.mean(P_total[:5])

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
            plt.figure()
            plt.plot(timestamps, P_total / 1e3)

        total_ss_change = 0
        for (start, end) in intervals:
            if plot:
                plt.axvspan(timestamps[start], timestamps[min(end, len(timestamps) - 1)], color='green', alpha=0.4)

            # Add 5 points to start and end
            new_start, new_end = start - 5, end + 5

            ss_change = np.mean(P_total[end:new_end]) - np.mean(P_total[new_start:start])
            total_ss_change += ss_change

        if plot:
            plt.title(f'threshold = {threshold} W, min_window_length = {min_window_length}')
            plt.xlabel('Time (min)')
            plt.ylabel('Total Real Power (kW)')
            plt.xlim(timestamps[0], timestamps[-1])
            plt.show()

        return np.abs(total_ss_change - entire_ss_change) + sum_of_flat_ranges

    print('Starting optimization...')
    result = minimize_scalar(evaluate_threshold, bounds=(0, 3000))
    print(result)

    start_time = time()
    evaluate_threshold(result.x, plot=False)
    duration = time() - start_time
    print(f'Took {duration} s for one evaluation')

    evaluate_threshold(result.x, plot=True)

    await node.close()

if __name__ == '__main__':
    asyncio.run(main())
