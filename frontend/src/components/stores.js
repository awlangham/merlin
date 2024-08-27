import { writable } from 'svelte/store';

// datasetStore: currently selected dataset name
export const datasetStore = writable('');

// eventIndexStore: currently selected event index
export const eventIndexStore = writable(-1);

// eventStore: array of objects with props {timestamp, start_ts, end_ts, P_ss, Q_ss, P_pk, Q_pk}
export const eventStore = writable([]);

// modeStore: currently selected tool mode
export const modeStore = writable('explore');

// filterStore: currently selected filter
export const filterStore = writable('');

// brushedStore: currently selected point indices
export const brushedStore = writable([]);

// clusterStore: current point clustering
export const clusterStore = writable(undefined);

// rangeStartStore and rangeEndStore: selected date range
export const rangeStartStore = writable(undefined);
export const rangeEndStore = writable(undefined);