<script>
    import { eventStore, filterStore } from "../stores";

    import TransientListItem from "./TransientListItem.svelte";

    let firstVisibleTimestamp = "",
        lastVisibleTimestamp = "";

    let transientsInner;

    const updateStartEndTimes = () => {
        const itemHeight = 47;

        const firstIndex = Math.floor(transientsInner.scrollTop / itemHeight);
        const lastIndex = Math.min(
            Math.floor(
                (transientsInner.scrollTop + transientsInner.clientHeight) /
                    itemHeight,
            ),
            $eventStore.length - 1,
        );

        firstVisibleTimestamp = $eventStore[firstIndex].timestamp;
        lastVisibleTimestamp = $eventStore[lastIndex].timestamp;
    };

    $: if ($eventStore.length > 0) {
        updateStartEndTimes();
    }
</script>

<div id="transients" class="h-100">
    <div class="timespan">
        Start: {firstVisibleTimestamp}
    </div>

    <div
        bind:this={transientsInner}
        on:scroll={updateStartEndTimes}
        id="transients-inner"
    >
        {#if $eventStore}
            <div class="list">
                {#each $eventStore as item}
                    {#if $filterStore == "" || item.label == $filterStore}
                        <TransientListItem eventData={item} />
                    {/if}
                {/each}
            </div>
        {/if}
    </div>

    <div class="timespan">
        End: {lastVisibleTimestamp}
    </div>
</div>

<style>
    .list {
        height: 0;
    }

    .timespan {
        height: 20px;
        padding-left: 10px;
        align-items: center;
        display: flex;
    }

    #transients {
        border: 2px solid gray;
        border-radius: 10px;
        box-shadow: 3px 3px 4px #888;
        background-color: white;
    }

    #transients-inner {
        overflow: auto;
        height: calc(100% - 44px);
        border-top: 2px solid gray;
        border-bottom: 2px solid gray;
    }
</style>
