<script>
    export let rangeStart, rangeEnd;
</script>

<span id="date-range-span">
    {#if rangeStart && rangeEnd}
        {rangeStart.toLocaleString(undefined, { hour12: false })} to {rangeEnd.toLocaleString(
            undefined,
            { hour12: false },
        )}
    {/if}
</span>

<style>
    #date-range-span {
        margin-left: auto;
        margin-right: auto;
    }
</style>
