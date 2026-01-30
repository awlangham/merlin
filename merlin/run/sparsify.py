import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from joule.client import FilterModule
from joule.api import Event, EventStream
from joule.errors import ApiError

from merlin.api import run_installation


class Sparsifier(FilterModule):
    """
    Detect edges in a three-phase prep stream, outputting a sparse stream containing only edge events.
    """

    def custom_args(self, parser) -> None:
        grp = parser.add_argument_group('Sparsifier', 'Module-specific arguments')
        grp.add_argument('--min_window_length', type=int, required=True, help='Minimum separation between interesting events')
        grp.add_argument('--threshold', type=float, required=True, help='Threshold on the range of any feature across min_window_length')
        grp.add_argument('--output', type=str, required=True, help='Output event stream name')
        grp.add_argument('--method', type=str, required=True, help='Learning method')

    async def _get_output_stream(self, output_stream_path: str) -> EventStream:
        """
        Get the EventStream object corresponding to output_stream_path.
        Creates it if does not exist.
        """

        event_stream_name = output_stream_path.split('/')[-1]

        try:
            return await self.node.event_stream_get(output_stream_path)
        except ApiError:
            new_stream = EventStream(name=event_stream_name)
            return await self.node.event_stream_create(new_stream, output_stream_path[:-len(event_stream_name) - 1])

    async def run(self, parsed_args, inputs, outputs) -> None:
        """
        Run module, either in real-time or historic mode.

        Must be run from an async function or from the command line with ``merlin-process-events``.
        """

        prep_pipe = inputs['prep']
        transients_pipe = outputs['transients']
        self.out_event_stream = await self._get_output_stream(parsed_args.output)

        min_window_length = parsed_args.min_window_length
        threshold = parsed_args.threshold
        self.method = parsed_args.method

        self.current_installation = run_installation(self.node)

        while not self.stop_requested and not await prep_pipe.is_empty():
            sarray_in = await prep_pipe.read(flatten=True)
            prep_data = sarray_in[:, 1:]
            num_rows = len(prep_data)

            if num_rows < 120:
                continue

            start_index = 0
            while True:
                if start_index + min_window_length > num_rows - 60:
                    # Nothing to see here, consume the data
                    prep_pipe.consume(num_rows - 60 - min_window_length)
                    break

                # Check if first window of data is quiet
                first_window = prep_data[start_index:start_index + min_window_length]

                if self.compute_range(first_window) < threshold:
                    start_index += 1
                    continue

                # We found something interesting, let's see where it stops
                windows = sliding_window_view(prep_data[start_index:], min_window_length, axis=0)

                end_index = start_index + min_window_length
                for index, window in enumerate(windows):
                    max_range = self.compute_range(window.T)

                    if max_range < threshold:
                        end_index += index
                        break

                await transients_pipe.write(sarray_in[start_index:end_index])
                new_event = await self.create_event(sarray_in[start_index:end_index, 0], sarray_in[start_index:end_index, 1:])
                await self.node.event_stream_write(self.out_event_stream, [new_event])
                prep_pipe.consume(end_index)
                break

    def compute_range(self, window):
        min_values = np.min(window, axis=0)
        max_values = np.max(window, axis=0)
        ranges = max_values - min_values
        return np.max(ranges)

    async def create_event(self, timestamps, window):
        if self.current_installation.num_phases == 3:
            PA_ss = self._extract_ss(window[:, 0])
            QA_ss = self._extract_ss(window[:, 1])

            PB_ss = self._extract_ss(window[:, 8])
            QB_ss = self._extract_ss(window[:, 9])

            PC_ss = self._extract_ss(window[:, 16])
            QC_ss = self._extract_ss(window[:, 17])

            PA_pk = self._extract_pk(window[:, 0])
            QA_pk = self._extract_pk(window[:, 1])

            PB_pk = self._extract_pk(window[:, 8])
            QB_pk = self._extract_pk(window[:, 9])

            PC_pk = self._extract_pk(window[:, 16])
            QC_pk = self._extract_pk(window[:, 17])

            I0_i, I0_q = self._extract_zs(window)

            event_content = {
                'PA_ss': float(PA_ss),
                'QA_ss': float(QA_ss),

                'PB_ss': float(PB_ss),
                'QB_ss': float(QB_ss),

                'PC_ss': float(PC_ss),
                'QC_ss': float(QC_ss),

                'PA_pk': float(PA_pk),
                'QA_pk': float(QA_pk),

                'PB_pk': float(PB_pk),
                'QB_pk': float(QB_pk),

                'PC_pk': float(PC_pk),
                'QC_pk': float(QC_pk),

                'P_ss': float(PA_ss + PB_ss + PC_ss),
                'Q_ss': float(QA_ss + QB_ss + QC_ss),
                'P_pk': float(PA_pk + PB_pk + PC_pk),
                'Q_pk': float(QA_pk + QB_pk + QC_pk),

                'I0_i': float(I0_i),
                'I0_q': float(I0_q)
            }

            type = 'OFF to ON' if (PA_ss + PB_ss + PC_ss) > 0 else 'ON to OFF'
        else:
            P_ss = self._extract_ss(window[:, 0])
            Q_ss = self._extract_ss(window[:, 1])

            P_pk = self._extract_pk(window[:, 0])
            Q_pk = self._extract_pk(window[:, 1])

            I0_i, I0_q = 0, 0

            event_content = {
                'P_ss': float(P_ss),
                'Q_ss': float(Q_ss),
                'P_pk': float(P_pk),
                'Q_pk': float(Q_pk),

                'I0_i': float(I0_i),
                'I0_q': float(I0_q)
            }
            type = 'OFF to ON' if P_ss > 0 else 'ON to OFF'

        if self.method == 'unsupervised':
            event_content['type'] = type
        else:
            # Find closest matching exemplar
            matching_exemplar, match_score = await self.current_installation.find_matching_exemplar(window)

            if matching_exemplar is not None and matching_exemplar['transitions'] is not None:
                # TODO: support multi-transition exemplars
                if len(matching_exemplar['transitions']) > 1:
                    raise Exception('Multi-transition exemplars not implemented yet.')
                    # Implement as list of labels, list of types?
                    # E.g. labels: ['load 1', 'load 2'], types: ['OFF to ON', 'HALF to OFF']
                else:
                    transition = matching_exemplar['transitions'][0]
                    event_content['label'] = transition[0]
                    event_content['type'] = transition[1] + ' to ' + transition[2]

                    cf = self.current_installation.read_config()
                    load_family = cf['loads'][transition[0]]['family']
                    event_content['load_family'] = load_family

                    event_content['distance'] = float(match_score)

        new_event = Event(start_time=timestamps[0],
                          end_time=timestamps[-1],
                          content=event_content,
                          event_stream_id=self.out_event_stream.id
                          )
        return new_event

    def _extract_ss(self, x: np.array):
        return np.mean(x[-5:]) - np.mean(x[:5])

    def _extract_pk(self, x: np.array):
        return np.max(x) - np.mean(x[:5])

    def _extract_zs(self, x: np.array):
        # v_rms = parsed_args.rms_voltage
        v_rms = 120  # TO DO: make parameter

        alpha = np.exp(2 * np.pi * 1j / 3)
        A_inverse = np.ones((3, 3), dtype=complex)

        # TO DO: make parameter
        # if parsed_args.sequence == 'acb':
        #     alpha = 1 / alpha

        A_inverse[1, 1] = alpha
        A_inverse[2, 2] = alpha
        A_inverse[1, 2] = alpha ** 2
        A_inverse[2, 1] = alpha ** 2

        PA, QA, PB, QB, PC, QC = x[:, (1, 2, 9, 10, 17, 18)].T
        IA = (PA - QA * 1j) / v_rms
        IB = (PB - QB * 1j) / (v_rms * alpha)
        IC = (PC - QC * 1j) / (v_rms * alpha ** 2)

        I_phase = np.array([IA, IB, IC])
        I_sequence = (A_inverse @ I_phase).T / 3

        I0_i, I0_q = np.real(I_sequence[:, 0]), np.imag(I_sequence[:, 0])

        I0_i_ss = np.mean(I0_i[-5:]) - np.mean(I0_i[:5])
        I0_q_ss = np.mean(I0_q[-5:]) - np.mean(I0_q[:5])

        return I0_i_ss, I0_q_ss


def main() -> None:
    sparsifier = Sparsifier()
    sparsifier.start()


if __name__ == '__main__':
    main()
