<script>
    import {
        datasetStore,
        eventIndexStore,
        eventStore,
        clusterStore,
    } from "../stores";

    import DatasetList from "./DatasetList.svelte";
    import DateRange from "./DateRange.svelte";

    let autoRefresh = false,
        showLoading = false,
        rangeStart,
        rangeEnd;

    $: if ($datasetStore !== "") {
        getEvents();
    }

    let interval;
    $: if (autoRefresh) {
        interval = setInterval(() => {
            getEvents();
        }, 3000);
    } else {
        clearInterval(interval);
    }

    $: if ($eventStore.length > 0) {
        rangeStart = new Date($eventStore[0].start_ts / 1000);
        rangeEnd = new Date($eventStore.at(-1).end_ts / 1000);
    }

    export const getEvents = () => {
        showLoading = true;
        fetch("api/features?stream_name=" + $datasetStore)
            .then((response) => response.json())
            .then((j) => {
                $eventIndexStore = -1;
                $eventStore = j.events;
                showLoading = false;
            });
    };

    const getClusters = () => {
        showLoading = true;
        fetch("api/clusters?stream_name=" + $datasetStore)
            .then((response) => response.json())
            .then((j) => {
                $clusterStore = j.cluster_assignments;
                showLoading = false;
            });
    };
</script>

<div class="top-bar">
    <DatasetList />

    {#if $datasetStore != ""}
        {#if showLoading}
            Loading...
        {:else}
            <button on:click={getEvents}>Refresh</button>
        {/if}

        <input
            id="auto-refresh-checkbox"
            type="checkbox"
            bind:checked={autoRefresh}
        />
        <label id="auto-refresh-label" for="auto-refresh-checkbox">
            Auto Refresh
        </label>
        <button on:click={getClusters}>Cluster</button>
    {/if}

    <DateRange {rangeStart} {rangeEnd} />
</div>

<style>
    .top-bar {
        display: flex;
        width: 70%;
        margin-left: auto;
        margin-right: auto;
        margin-bottom: 10px;
        padding: 10px 10px 10px 10px;
        border: 2px solid gray;
        border-radius: 10px;
        box-shadow: 3px 1px 4px #888;
        background-color: white;
    }

    #auto-refresh-checkbox {
        margin-left: 20px;
    }

    #auto-refresh-label {
        margin-right: 20px;
    }
</style>
