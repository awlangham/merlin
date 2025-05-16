import numpy as np
from pandas import Series
from joule.client import FilterModule


class EdgeDetector(FilterModule):
    """
    Name: NILM Edge Detector
    Author: Aaron Langham
    Description: Extract event edges from 3-phase prep stream
    """

    def custom_args(self, parser):
        grp = parser.add_argument_group('Edge detector', 'Module-specific arguments')
        grp.add_argument('--min_ss_change', type=float, required=True, help='Minimum steady-state change required to be an event')
        grp.add_argument('--settling_window_length', type=int, required=True, help='Length of rolling standard deviation filter for flatness detection')
        grp.add_argument('--settling_std_dev', type=float, required=True, help='Standard deviation threshold for flatness detection')

    async def run(self, parsed_args, inputs, outputs):
        prep_pipe = inputs['prep']
        transients_pipe = outputs['transients']

        self.minimum_ss_change = parsed_args.min_ss_change
        self.settling_std_dev = parsed_args.settling_std_dev
        self.settling_window_length = parsed_args.settling_window_length

        last_timestamp = -1
        while not self.stop_requested and not await prep_pipe.is_empty():
            sarray_in = await prep_pipe.read()
            num_rows = len(sarray_in)

            # Wait for more data if we don't have enough and we're not on an interval boundary
            if num_rows <= 2 * self.settling_window_length - 1:
                prep_pipe.consume(num_rows)
                continue

            interval_list = self.process_window(sarray_in)

            for (interval_start, interval_end) in interval_list:
                timestamps = sarray_in['timestamp'][interval_start + self.settling_window_length // 2:interval_end + self.settling_window_length // 2]
                prep_interval = sarray_in['data'][interval_start + self.settling_window_length // 2:interval_end + self.settling_window_length // 2]

                # If this interval overlaps with a previous interval, just trim it
                valid_indices = np.where(timestamps > last_timestamp)
                timestamps, prep_interval = timestamps[valid_indices], prep_interval[valid_indices]

                if len(timestamps) == 0:
                    # Something went wrong, just skip this interval
                    continue

                last_timestamp = timestamps[-1]
                await transients_pipe.write(np.column_stack((timestamps, prep_interval)))

            # Leave invalid rows for the next read
            prep_pipe.consume(num_rows - 2 * self.settling_window_length + 1)

    def process_window(self, sarray_in: np.array) -> list[tuple]:
        prep_in = sarray_in['data']

        PQ = prep_in[:, (0, 1, 8, 9, 16, 17)]
        P_total = PQ[:, 0] + PQ[:, 2] + PQ[:, 4]
        Q_total = PQ[:, 1] + PQ[:, 3] + PQ[:, 5]

        P_total = rolling_median(P_total, 7)
        Q_total = rolling_median(Q_total, 7)

        P_sigma = rolling_std(P_total, self.settling_window_length)
        Q_sigma = rolling_std(Q_total, self.settling_window_length)

        flat_indices = np.where(np.logical_and(P_sigma < self.settling_std_dev, Q_sigma < self.settling_std_dev))[0]

        is_flat = np.zeros(len(P_sigma))
        is_flat[flat_indices] = 1

        # Now we have the points where the streams are flat, but we actually want the intervals
        # Let's find every interval [a, b] such that all points in [a, b] are part of a non-flat interval

        flat_changes = np.diff(np.pad(1 - is_flat, 1))
        intervals = list(zip(np.where(flat_changes == 1)[0], np.where(flat_changes == -1)[0] - 1))

        output_events = []
        for interval_start, interval_end in intervals:
            if interval_end - interval_start < self.settling_window_length - 4:
                # Interval too short
                continue

            ss_window = 5
            ss_start = np.mean(PQ[interval_start + self.settling_window_length // 2:interval_start + self.settling_window_length // 2 + ss_window], axis=0)
            ss_end = np.mean(PQ[interval_end + self.settling_window_length // 2 - ss_window:interval_end + self.settling_window_length // 2], axis=0)
            PQ_ss_interval = ss_end - ss_start

            if np.max(np.abs(PQ_ss_interval)) < self.minimum_ss_change:
                # Steady-state change too small, just skip it
                continue

            output_events.append((interval_start, interval_end))
        return output_events


def rolling_std(data, window_size: int) -> np.array:
    window = np.ones(window_size) / window_size
    mean_square = np.convolve(data ** 2, window, mode='valid')
    mean = np.convolve(data, window, mode='valid')
    return np.sqrt(mean_square - mean ** 2)


def rolling_median(data, window_size: int):
    return Series(data).rolling(window=window_size, center=True, min_periods=1).median().values


def main():
    edge_detector = EdgeDetector()
    edge_detector.start()


if __name__ == '__main__':
    main()
