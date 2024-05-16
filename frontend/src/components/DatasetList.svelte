<script>
    export let selectedStreamName;

    const datasetListPromise = fetch("api/datasets").then((response) =>
        response.json(),
    );
</script>

{#await datasetListPromise}
    <!-- Loading dataset list... -->
{:then data}
    Connected to [{data.joule_node}]
    <select class="stream-select" bind:value={selectedStreamName}>
        <option hidden value="">-- select a stream --</option>
        {#each data.dataset_names as dataset_name}
            <option value={dataset_name}>{dataset_name}</option>
        {/each}
    </select>
    <!-- {:catch error} -->
    <!-- {error.message} -->
{/await}

<style>
    .stream-select {
        margin-left: 10px;
        margin-right: 10px;
    }
</style>
