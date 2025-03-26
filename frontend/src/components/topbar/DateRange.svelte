<script>
    import { getEvents } from "../api-calls";
    import { rangeStartStore, rangeEndStore, rangeModeStore } from "../stores";

    let interval;
    $: if ($rangeModeStore === "live") {
        interval = setInterval(() => {
            getEvents();
        }, 5000);
    } else {
        clearInterval(interval);
    }
</script>

<span id="date-range-span">
    <select bind:value={$rangeModeStore}>
        <option value="start">Start</option>
        <option value="end">End</option>
        <option value="live">Live</option>
    </select>

    <input
        type="date"
        bind:value={$rangeStartStore}
        disabled={$rangeModeStore != "start"}
    />
    to
    <input
        type="date"
        bind:value={$rangeEndStore}
        disabled={$rangeModeStore != "end"}
    />
    <button id="set-daterange-btn" on:click={getEvents}>Go</button>
</span>

<style>
    #date-range-span {
        margin-left: auto;
        margin-right: auto;
    }
</style>
