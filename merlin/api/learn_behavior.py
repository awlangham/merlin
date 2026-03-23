import numpy as np
import json
import matplotlib.pyplot as plt
from scipy import stats


async def learn_behavior(self, start_ts, end_ts, load_name):
    json_filter = json.dumps([[['label', 'is', load_name]]])
    events = await self.node.event_stream_read_list(self.stream_name + '/events', start=start_ts, end=end_ts, json_filter=json_filter)

    arrival_times = [event.start_time for event in events if event.content['type'] == 'OFF to ON']
    interarrival_times = np.diff(arrival_times) / 1e6  # scale to seconds

    gaussian_res = stats.fit(stats.norm, interarrival_times, [(0, 1e12), (0, 1e12)])
    gaussian_nll = gaussian_res.nllf()

    exponential_res = stats.fit(stats.expon, interarrival_times, {'loc': (0, 0), 'scale': (0, 1e12)})
    exponential_nll = exponential_res.nllf()

    print(f'Avg interarrival time: {round(np.mean(interarrival_times))} s')

    plt.figure(tight_layout=True)
    plt.rcParams.update({'font.size': 14})
    plt.hist(interarrival_times, density=True, bins=30, label='Observed Data')
    x = np.linspace(min(interarrival_times), max(interarrival_times), 200)

    if gaussian_nll < exponential_nll:
        # Gaussian is better fit
        print(f'Gaussian: μ = {round(gaussian_res.params.loc)} s, σ = {round(gaussian_res.params.scale)} s')
        # gaussian_res.plot()
        pdf = stats.norm.pdf(x, loc=gaussian_res.params.loc, scale=gaussian_res.params.scale)
        plt.title(f'Gaussian: μ = {round(gaussian_res.params.loc)} s, σ = {round(gaussian_res.params.scale)} s')
        
    else:
        # Exponential is better fit
        print(f'Exponential: λ = {round(exponential_res.params.scale)} s')
        # exponential_res.plot()
        pdf = stats.expon.pdf(x, loc=0, scale=exponential_res.params.scale)
        plt.title(f'Exponential: λ = {round(exponential_res.params.scale)} s')

    plt.xlabel('Interarrival times (s)')
    plt.ylabel('Probability Density (1/s)')
    plt.plot(x, pdf, color='C1', lw=4, label='Fit Distribution')
    plt.legend()
    plt.gcf().patch.set_linewidth(5)
    plt.gcf().patch.set_edgecolor('black')
    plt.xlim(np.min(interarrival_times), np.max(interarrival_times))
    plt.grid()

    plt.show()
