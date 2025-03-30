<script>
    import { eventIndexStore, eventStore } from "../stores";

    import VirtualList from "svelte-virtual-list-ce";

    import { tick } from "svelte";

    import TransientListItem from "./TransientListItem.svelte";

    let scrollToIndex;

    let firstVisibleTimestamp = "",
        lastVisibleTimestamp = "";

    const scrollToSelected = async () => {
        scrollToIndex($eventIndexStore, { behavior: "instant" });

        await tick();

        const selectedElementList = document.getElementsByClassName("selected");
        if (selectedElementList.length > 0) {
            selectedElementList[0].scrollIntoView({
                block: "start",
            });
        }
    };

    $: if ($eventIndexStore != -1) {
        scrollToSelected();
    }

    let virtualListStart, virtualListEnd;
    $: if (virtualListStart && virtualListEnd) {
        firstVisibleTimestamp = $eventStore[virtualListStart].timestamp;
        lastVisibleTimestamp = $eventStore[virtualListEnd - 1].timestamp;
    }

    $: console.log($eventStore);
</script>

<div id="transients" class="h-100">
    <div class="timespan">
        Start: {firstVisibleTimestamp}
    </div>

    {#if $eventStore}
        <div class="list">
            <VirtualList
                bind:start={virtualListStart}
                bind:end={virtualListEnd}
                bind:scrollToIndex
                items={$eventStore}
                let:item
            >
                <TransientListItem eventData={item} />
            </VirtualList>
        </div>
    {/if}

    <div class="timespan">
        End: {lastVisibleTimestamp}
    </div>
</div>

<style>
    .list {
        height: calc(33.75vh - 20px - 20px - 20px);
        border-top: 2px solid gray;
        border-bottom: 2px solid gray;
    }

    .timespan {
        height: 20px;
        padding-left: 10px;
    }

    #transients {
        overflow: auto;
        border: 2px solid gray;
        border-radius: 10px;
        box-shadow: 3px 3px 4px #888;
        background-color: white;
    }
</style>
