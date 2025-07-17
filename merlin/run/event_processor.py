import numpy as np
from joule.client import FilterModule
from joule.api import Event, EventStream
from joule.errors import ApiError
from joule.utilities import yesno

from merlin.api import Installation


class EventProcessor(FilterModule):
    """
    Filter module to process a sparse time-domain prep stream
    into a collection of Joule events.
    """

    gap_time = 20000 # microseconds

    def custom_args(self, parser):
        grp = parser.add_argument_group('Merlin', 'Module-specific arguments')
        grp.add_argument('--output', type=str, required=True, help='Output event stream name')
        grp.add_argument('--method', type=str, required=True, help='Learning method')
        grp.add_argument('--combinatorial', type=yesno, required=True, help='Use combinatorial matching')

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

        transients_pipe = inputs['transients']
        out_event_stream = await self._get_output_stream(parsed_args.output)

        if parsed_args.method == 'supervised':
            current_installation = Installation(self.node)

        while not self.stop_requested and not await transients_pipe.is_empty():
            sarray_in = await self.read_from_input(transients_pipe)

            if len(sarray_in) == 0:
                continue

            timestamps = sarray_in['timestamp']
            timestamps_diff = np.diff(timestamps)

            if np.all(timestamps_diff < self.gap_time):
                # Fix to prevent premature event end when
                # there's still more transient data left to process.
                # The downside is that events can't be ended before another begins.

                if transients_pipe.closed:
                    # Flush the pipe
                    end_index = len(timestamps) - 1
                else:
                    continue
            else:
                end_index = np.argmax(timestamps_diff >= self.gap_time)

            timestamps = timestamps[:end_index + 1]
            truncated_data = sarray_in['data'][:end_index + 1]

            PA_ss = self._extract_ss(truncated_data[:, 0])
            QA_ss = self._extract_ss(truncated_data[:, 1])

            PB_ss = self._extract_ss(truncated_data[:, 8])
            QB_ss = self._extract_ss(truncated_data[:, 9])

            PC_ss = self._extract_ss(truncated_data[:, 16])
            QC_ss = self._extract_ss(truncated_data[:, 17])

            PA_pk = self._extract_pk(truncated_data[:, 0])
            QA_pk = self._extract_pk(truncated_data[:, 1])

            PB_pk = self._extract_pk(truncated_data[:, 8])
            QB_pk = self._extract_pk(truncated_data[:, 9])

            PC_pk = self._extract_pk(truncated_data[:, 16])
            QC_pk = self._extract_pk(truncated_data[:, 17])

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
                'Q_pk': float(QA_pk + QB_pk + QC_pk)
            }

            if parsed_args.method == 'unsupervised':
                event_content['type'] = 'OFF to ON' if (PA_ss + PB_ss + PC_ss) > 0 else 'ON to OFF'
            else:
                # Find closest matching exemplar
                matching_exemplar, match_score = await current_installation.find_matching_exemplar(truncated_data)

                if matching_exemplar is None and parsed_args.combinatorial:
                    comb_match = await current_installation.combinatorial_match(PA_ss + PB_ss + PC_ss, QA_ss + QB_ss + QC_ss)
                    if comb_match is not None:
                        event_content['label'] = comb_match[0]
                        event_content['type'] = comb_match[1]
                        event_content['distance'] = None
                elif matching_exemplar is not None and matching_exemplar['transitions'] is not None:
                    # TODO: support multi-transition exemplars
                    if len(matching_exemplar['transitions']) > 1:
                        raise Exception('Multi-transition exemplars not implemented yet.')
                        # Implement as list of labels, list of types?
                        # E.g. labels: ['load 1', 'load 2'], types: ['OFF to ON', 'HALF to OFF']
                    else:
                        transition = matching_exemplar['transitions'][0]
                        event_content['label'] = transition[0]
                        event_content['type'] = transition[1] + ' to ' + transition[2]

                        cf = current_installation.read_config()
                        load_family = cf['loads'][transition[0]]['family']
                        event_content['load_family'] = load_family

                        event_content['distance'] = float(match_score)

            new_event = Event(start_time=timestamps[0],
                              end_time=timestamps[-1],
                              content=event_content,
                              event_stream_id=out_event_stream.id
                              )

            await self.write_to_output(out_event_stream, [new_event])
            transients_pipe.consume(end_index + 1)

    async def read_from_input(self, transients_pipe):
        return await transients_pipe.read()

    async def write_to_output(self, event_stream_name: str, event_list: list[Event]):
        await self.node.event_stream_write(event_stream_name, event_list)

    def _extract_ss(self, x: np.array):
        return np.mean(x[-5:]) - np.mean(x[:5])

    def _extract_pk(self, x: np.array):
        return np.max(x) - np.mean(x[:5])


def main() -> None:
    merlin_event_processor = EventProcessor()
    merlin_event_processor.start()


if __name__ == '__main__':
    main()
