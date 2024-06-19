import { get } from "svelte/store";
import { datasetStore, eventIndexStore, eventStore, clusterStore } from "./stores";

export const getEvents = () => {
    fetch("api/features?stream_name=" + get(datasetStore))
        .then((response) => response.json())
        .then((j) => {
            eventIndexStore.set(-1);
            eventStore.set(j.events);
        });
};

export const getClusters = () => {
    fetch("api/clusters?stream_name=" + get(datasetStore))
        .then((response) => response.json())
        .then((j) => {
            clusterStore.set(j.cluster_assignments);
        });
};