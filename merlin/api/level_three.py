import numpy as np
import json
# import matplotlib.pyplot as plt
from scipy import stats

from merlin.utilities import async_run

@async_run
async def level_three(self, load_name, start_ts: int, end_ts: int):
    json_filter = json.dumps([[['label', 'is', load_name]]])
    events = await self.node.event_stream_read_list(self.stream_name + '/events', start=start_ts, end=end_ts, json_filter=json_filter)

    arrival_times = [event.start_time for event in events if event.content['type'] == 'OFF to ON']
    interarrival_times = np.diff(arrival_times) / 1e6  # scale to seconds

    print('Trying a Gaussian fit...')
    gaussian_res = stats.fit(stats.norm, interarrival_times, [(0, 1e12), (0, 1e12)])
    print(f'Fitted mean: {round(gaussian_res.params.loc)} s, std. dev.: {round(gaussian_res.params.scale)} s')
    gaussian_nll = gaussian_res.nllf()
    # gaussian_res.plot()

    print('Trying an exponential fit...')
    exponential_res = stats.fit(stats.expon, interarrival_times, {'loc': (0, 0), 'scale': (0, 1e12)})
    print(f'Fitted rate param.: {round(exponential_res.params.scale)} s')
    exponential_nll = exponential_res.nllf()
    # exponential_res.plot()

    if gaussian_nll < exponential_nll:
        # Gaussian is better fit
        print('Gaussian', gaussian_res.params.loc, gaussian_res.params.scale)
    else:
        # Exponential is better fit
        print('Exponential', exponential_res.params.scale)


    print('Avg interarrival time:', np.mean(interarrival_times))

    # period = res.params.loc

    # start_time = None
    # durations = []
    # for event in events:
    #     if event.content['type'] == 'OFF to ON':
    #         start_time = event.start_time
    #     elif event.content['type'] == 'ON to OFF' and start_time is not None:
    #         durations.append((event.end_time - start_time) / 1e6)  # convert to seconds
    #         start_time = None

    # duty_cycle = np.mean(durations) / period
    # print(duty_cycle)

    # x = np.linspace(dist.ppf(0.01), dist.ppf(0.99), 100)
    # plt.plot(x, dist.pdf(x))

    # plt.hist(interarrival_times)
    # plt.show()
