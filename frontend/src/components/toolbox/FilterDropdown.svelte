<script>
    import { filterStore, eventStore } from "../stores";

    $: loadTypes = [
        ...new Set($eventStore.map((event) => event.load_type)),
    ].sort();
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
