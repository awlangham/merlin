import numpy as np
from joule import FilterModule
from joule.api import Event, EventStream
from joule.errors import ApiError

from merlin.config import config_file


class EventProcessor(FilterModule):
    gap_time = 0.5 * 1e6  # microseconds

    def custom_args(self, parser):
        grp = parser.add_argument_group('Merlin', 'Module-specific arguments')
        grp.add_argument('--output', type=str, required=True, help='Output event stream name')
        grp.add_argument('--method', type=str, required=True, help='Learning method')

    async def _get_output_stream(self, output_stream_path: str) -> EventStream:
        event_stream_name = output_stream_path.split('/')[-1]

        try:
            return await self.node.event_stream_get(output_stream_path)
        except ApiError:
            new_stream = EventStream(name=event_stream_name)
            return await self.node.event_stream_create(new_stream, output_stream_path[:-len(event_stream_name) - 1])

    async def run(self, parsed_args, inputs, outputs):
        transients_pipe = inputs['transients']
        out_event_stream = await self._get_output_stream(parsed_args.output)

        while not self.stop_requested:
            sarray_in = await transients_pipe.read()
            timestamps = sarray_in['timestamp']

            timestamps_diff = np.diff(timestamps)
            end_index = np.argmax(timestamps_diff >= self.gap_time)

            if np.all(timestamps_diff < self.gap_time):
                end_index = len(timestamps) - 1

            timestamps = timestamps[:end_index + 1]
            P, Q = sarray_in['data'][:end_index + 1, 0], sarray_in['data'][:end_index + 1, 1]

            P_ss = np.mean(P[-5:]) - np.mean(P[:5])
            Q_ss = np.mean(Q[-5:]) - np.mean(Q[:5])

            P_pk = np.max(P) - np.mean(P[:5])
            Q_pk = np.max(Q) - np.mean(Q[:5])

            features_ss = np.array([P_ss, Q_ss, P_pk, Q_pk])

            event_content = {
                'P_ss': float(P_ss),
                'Q_ss': float(Q_ss),
                'P_pk': float(P_pk),
                'Q_pk': float(Q_pk)
            }

            if parsed_args.method == 'unsupervised':
                event_content['type'] = 'ON' if P_ss > 0 else 'OFF'
            else:
                # Find closest matching exemplar
                best_error = np.inf
                matching_load = None
                matching_exemplar = None
                with config_file() as loads_json:
                    for load_name in loads_json:
                        print(loads_json[load_name])
                        print('--')
                        for exemplar_name in loads_json[load_name]:
                            print(exemplar_name)
                            exemplar_ss = np.array(loads_json[load_name][exemplar_name]['ss'])
                            error = np.linalg.norm(features_ss - exemplar_ss)
                            if error < best_error:
                                best_error = error
                                matching_load = load_name
                                matching_exemplar = exemplar_name

                if matching_load is not None:
                    event_content['label'] = matching_load

                if matching_exemplar is not None:
                    event_content['type'] = exemplar_name

            start_ts, end_ts = timestamps[0], timestamps[-1]
            new_event = Event(start_time=start_ts,
                              end_time=end_ts,
                              content=event_content
                              )

            await self.node.event_stream_write(out_event_stream, [new_event])

            transients_pipe.consume(end_index + 1)


def main():
    merlin = EventProcessor()
    merlin.start()


if __name__ == '__main__':
    main()
