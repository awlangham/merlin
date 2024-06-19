import { writable } from 'svelte/store';

export const datasetStore = writable('');
export const eventIndexStore = writable(-1);
export const eventStore = writable([]);
export const modeStore = writable('explore');