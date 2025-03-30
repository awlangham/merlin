<script>
    import { datasetStore, rangeStartStore, rangeEndStore } from "../stores";

    const datasetListPromise = fetch("api/datasets").then((response) =>
        response.json(),
    );
</script>

{#await datasetListPromise}
    <!-- Loading dataset list... -->
    Connecting...
    <select disabled class="stream-select form-select form-select-sm">
        <option hidden value="">-- select a stream --</option>
    </select>
{:then data}
    Connected to [{data.joule_node}]
    <select
        class="stream-select form-select form-select-sm"
        bind:value={$datasetStore}
        on:change={() => {
            $rangeStartStore = undefined;
            $rangeEndStore = undefined;
        }}
    >
        <option hidden value="">-- select a stream --</option>
        {#each data.dataset_names as dataset_name}
            <option value={dataset_name}>{dataset_name}</option>
        {/each}
    </select>
    <!-- {:catch error} -->
    <!-- {error.message} -->
{:catch}
    Connection error
{/await}

<style>
    .stream-select {
        display: inline;
        width: auto;
        margin-left: 10px;
        margin-right: 10px;
    }
</style>
