<script>
    import { datasetStore } from "../stores";
    import { getEvents, getClusters } from "../api-calls";

    import DatasetList from "./DatasetList.svelte";
    import DateRange from "./DateRange.svelte";

    $: if ($datasetStore !== "") {
        getEvents();
    }
</script>

<div class="top-bar">
    <DatasetList />

    <button
        id="button-refresh"
        disabled={$datasetStore == ""}
        type="button"
        class="btn btn-secondary btn-sm"
        on:click={getEvents}
    >
        Refresh
    </button>
    <button
        disabled={$datasetStore == ""}
        type="button"
        class="btn btn-secondary btn-sm"
        on:click={getClusters}
    >
        Cluster
    </button>

    <DateRange />
</div>

<style>
    .top-bar {
        padding: 10px 10px 10px 10px;
        border: 2px solid gray;
        border-radius: 10px;
        box-shadow: 3px 1px 4px #888;
        background-color: white;
        display: flex;
        align-items: center;
    }

    #button-refresh {
        margin-right: 10px;
    }
</style>
