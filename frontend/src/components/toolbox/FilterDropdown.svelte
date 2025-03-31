<script>
    import {
        filterStore,
        eventStore,
        eventIndexStore,
        brushedStore,
        datasetStore,
    } from "../stores";

    $: loadLabels = [
        ...new Set($eventStore.map((event) => event.label)),
    ].sort();

    filterStore.subscribe((value) => {
        $eventIndexStore = -1;
        $brushedStore = [];
    });
</script>

Filter by:
<select
    disabled={$datasetStore == ""}
    class="form-select form-select-sm"
    bind:value={$filterStore}
>
    <option value="">-- show all --</option>
    {#each loadLabels as loadLabel}
        {#if loadLabel != null}
            <option>{loadLabel}</option>
        {:else}
            <option value={loadLabel}>-- unlabeled --</option>
        {/if}
    {/each}
</select>

<style>
    .form-select {
        display: inline;
        width: auto;
        margin-left: 10px;
        margin-right: 10px;
    }
</style>
