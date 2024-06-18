<script>
    import { datasetStore } from "./stores";
    import DatasetList from "./DatasetList.svelte";

    export let selectedEventID, events, clusterData;

    let selectedStreamName;
    datasetStore.subscribe((value) => {
        selectedStreamName = value;
    });

    let autoRefresh = false,
        showLoading = false,
        rangeStart,
        rangeEnd;

    $: if (selectedStreamName !== "") {
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

    export const getEvents = () => {
        showLoading = true;
        fetch("api/features?stream_name=" + selectedStreamName)
            .then((response) => response.json())
            .then((j) => {
                selectedEventID = -1;
                rangeStart = j.range_start
                    ? new Date(j.range_start / 1000)
                    : null;
                rangeEnd = j.range_end ? new Date(j.range_end / 1000) : null;
                events = j.events;
                showLoading = false;
            });
    };

    const getClusters = () => {
        showLoading = true;
        fetch("api/clusters?stream_name=" + selectedStreamName)
            .then((response) => response.json())
            .then((j) => {
                clusterData = j.cluster_assignments;
                showLoading = false;
            });
    };
</script>

<div class="top-bar">
    <DatasetList />

    {#if selectedStreamName != ""}
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

    <span id="date-range-span">
        {#if rangeStart && rangeEnd}
            {rangeStart.toLocaleString(undefined, { hour12: false })} to {rangeEnd.toLocaleString(
                undefined,
                { hour12: false },
            )}
        {/if}
    </span>
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

    #date-range-span {
        margin-left: auto;
        margin-right: auto;
    }
</style>
