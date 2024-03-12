<script>
    export let selected_stream_name;

    const eventStreamListPromise = fetch("api/event_stream_list").then(
        (response) => response.json()
    );
</script>

{#await eventStreamListPromise}
    <!-- Loading event stream list... -->
{:then data}
    <select
        class="stream-select"
        bind:value={selected_stream_name}
    >
        <option hidden value="">-- select a stream --</option>
        {#each data.stream_names as stream_name}
            <option value={stream_name}>{stream_name}</option>
        {/each}
    </select>
    <!-- {:catch error} -->
    <!-- {error.message} -->
{/await}

<style>
    .stream-select {
        margin-right: 10px;
    }
</style>
