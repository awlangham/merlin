<script>
    import {
        filterStore,
        eventStore,
        eventIndexStore,
        brushedStore,
    } from "../stores";

    $: loadTypes = [
        ...new Set($eventStore.map((event) => event.load_type)),
    ].sort();

    filterStore.subscribe((value) => {
        $eventIndexStore = -1;
        $brushedStore = undefined;
    });
</script>

<div>
    Filter by:
    <select bind:value={$filterStore}>
        <option value="">-- show all --</option>
        {#each loadTypes as loadType}
            <option>{loadType}</option>
        {/each}
    </select>
</div>
