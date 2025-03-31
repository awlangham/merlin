<script>
    import { eventStore } from "../stores";

    // import VirtualList from "svelte-virtual-list-ce";

    import TransientListItem from "./TransientListItem.svelte";

    // let scrollToIndex;

    let firstVisibleTimestamp = "",
        lastVisibleTimestamp = "";

    // const scrollToSelected = async () => {
    //     scrollToIndex($eventIndexStore, { behavior: "instant" });

    //     await tick();

    //     const selectedElementList = document.getElementsByClassName("selected");
    //     if (selectedElementList.length > 0) {
    //         selectedElementList[0].scrollIntoView({
    //             block: "start",
    //         });
    //     }
    // };

    // $: if ($eventIndexStore != -1) {
    //     scrollToSelected();
    // }

    let virtualListStart, virtualListEnd;
    $: if (virtualListStart && virtualListEnd) {
        firstVisibleTimestamp = $eventStore[virtualListStart].timestamp;
        lastVisibleTimestamp = $eventStore[virtualListEnd - 1].timestamp;
    }
</script>

<div id="transients" class="h-100">
    <div class="timespan">
        Start: {firstVisibleTimestamp}
    </div>

    <div id="transients-inner">
        {#if $eventStore}
            <div class="list">
                <!-- <VirtualList
                bind:start={virtualListStart}
                bind:end={virtualListEnd}
                bind:scrollToIndex
                items={$eventStore}
                let:item
            > -->
                {#each $eventStore as item}
                    <TransientListItem eventData={item} />
                {/each}
                <!-- </VirtualList> -->
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
