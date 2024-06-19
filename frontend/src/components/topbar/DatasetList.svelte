<script>
    import { datasetStore } from "../stores";

    let selection;

    $: if (selection) {
        datasetStore.set(selection);
    }

    const datasetListPromise = fetch("api/datasets").then((response) =>
        response.json(),
    );
</script>

<div class="event-stream-list">
    {#await datasetListPromise}
        <!-- Loading dataset list... -->
    {:then data}
        Connected to [{data.joule_node}]
        <select class="stream-select" bind:value={selection}>
            <option hidden value="">-- select a stream --</option>
            {#each data.dataset_names as dataset_name}
                <option value={dataset_name}>{dataset_name}</option>
            {/each}
        </select>
        <!-- {:catch error} -->
        <!-- {error.message} -->
    {/await}
</div>

<style>
    .event-stream-list {
        display: flex;
    }

    .stream-select {
        margin-left: 10px;
        margin-right: 10px;
    }
</style>
