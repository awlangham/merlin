import { get } from "svelte/store";
import { datasetStore, eventIndexStore, eventStore, clusterStore, rangeStartStore, rangeEndStore } from "./stores";

const formatDate = (dateTime) => {
    const year = dateTime.getFullYear();
    const month = dateTime.getMonth() + 1;
    const date = dateTime.getDate();
    return (
        year +
        "-" +
        month.toString().padStart(2, "0") +
        "-" +
        date.toString().padStart(2, "0")
    );
};

const unformatDate = (dateString, end = false) => {
    const [year, month, date] = dateString.split("-");
    let outputDate = new Date();
    outputDate.setFullYear(year);
    outputDate.setMonth(month - 1);
    if (end) {
        outputDate.setDate(+date + 1);
    } else {
        outputDate.setDate(date)
    }
    outputDate.setHours(0);
    outputDate.setMinutes(0);
    outputDate.setSeconds(0);
    outputDate.setMilliseconds(0);

    return outputDate.getTime() * 1000;
}

export const getEvents = () => {
    let endpoint = "api/features?stream_name=" + get(datasetStore);

    if (get(rangeStartStore) && get(rangeEndStore)) {
        endpoint += '&start_ts=';
        endpoint += unformatDate(get(rangeStartStore));
        endpoint += '&end_ts=';
        endpoint += unformatDate(get(rangeEndStore), true);
    }

    fetch(endpoint)
        .then((response) => response.json())
        .then((j) => {
            eventIndexStore.set(-1);
            eventStore.set(j.events);
            rangeStartStore.set(formatDate(new Date(j.events[0].start_ts / 1000)))
            rangeEndStore.set(formatDate(new Date(j.events.at(-1).end_ts / 1000)))
        });
};

export const getClusters = () => {
    fetch("api/clusters?stream_name=" + get(datasetStore))
        .then((response) => response.json())
        .then((j) => {
            clusterStore.set(j.cluster_assignments);
        });
};