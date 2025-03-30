<script>
    import {
        filterStore,
        eventStore,
        eventIndexStore,
        brushedStore,
    } from "../stores";

    $: loadLabels = [
        ...new Set($eventStore.map((event) => event.label)),
    ].sort();

    filterStore.subscribe((value) => {
        $eventIndexStore = -1;
        $brushedStore = [];
    });
</script>

<div>
    Filter by:
    <select class="form-select form-select-sm" bind:value={$filterStore}>
        <option value="">-- show all --</option>
        {#each loadLabels as loadLabel}
            {#if loadLabel != null}
                <option>{loadLabel}</option>
            {:else}
                <option value={loadLabel}>-- unlabeled --</option>
            {/if}
        {/each}
    </select>
</div>

<style>
    .form-select {
        display: inline;
        width: auto;
    }
</style>