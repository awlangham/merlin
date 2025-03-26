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

    {#if $datasetStore != ""}
        <button on:click={getEvents}>Refresh</button>
        <button on:click={getClusters}>Cluster</button>
    {/if}

    <DateRange />
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
</style>
