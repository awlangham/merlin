<script>
    import {
        filterStore,
        eventStore,
        eventIndexStore,
        brushedStore,
    } from "../stores";

    $: loadTypes = [
        ...new Set($eventStore.map((event) => event.load_family)),
    ].sort();

    filterStore.subscribe((value) => {
        $eventIndexStore = -1;
        $brushedStore = [];
    });
</script>

<div>
    Filter by:
    <select bind:value={$filterStore}>
        <option value="">-- show all --</option>
        {#each loadTypes as loadType}
            {#if loadType != null}
                <option>{loadType}</option>
            {:else}
                <option value={loadType}>-- undefined --</option>
            {/if}
        {/each}
    </select>
</div>
