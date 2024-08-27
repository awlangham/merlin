<script>
    import { getEvents } from "../api-calls";
    import { rangeStartStore, rangeEndStore } from "../stores";
</script>

<span id="date-range-span">
    <input type="date" bind:value={$rangeStartStore} />
    to
    <input type="date" bind:value={$rangeEndStore} />
    <button id="set-daterange-btn" on:click={getEvents}>Go</button>
</span>

<style>
    #date-range-span {
        margin-left: auto;
        margin-right: auto;
    }
</style>
