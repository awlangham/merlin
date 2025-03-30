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
        <button type="button" class="btn btn-primary" on:click={getEvents}>Refresh</button>
        <button type="button" class="btn btn-primary" on:click={getClusters}>Cluster</button>

        <DateRange />
    {/if}
</div>

<style>
    .top-bar {
        margin-bottom: 10px;
        padding: 10px 10px 10px 10px;
        border: 2px solid gray;
        border-radius: 10px;
        box-shadow: 3px 1px 4px #888;
        background-color: white;
    }
</style>
