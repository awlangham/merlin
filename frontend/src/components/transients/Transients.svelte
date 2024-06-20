<script>
    import { eventIndexStore, eventStore } from "../stores";

    import VirtualList from "svelte-virtual-list-ce";

    import { tick } from "svelte";

    import TransientListItem from "./TransientListItem.svelte";
    import TransientPlot from "./TransientPlot.svelte";

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
</script>

<TransientPlot />

<div class="timespan">
    Start: {firstVisibleTimestamp}
</div>

<div id="transients">
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
</div>

<div class="timespan">
    End: {lastVisibleTimestamp}
</div>

<style>
    .list {
        width: 100%;
        height: 100%;
    }

    .timespan {
        height: 20px;
        padding-bottom: 5px;
        padding-top: 5px;
        padding-left: 10px;
    }

    #transients {
        height: calc(100vh - 110px + 20px - 144px - 50px - 275px - 7px);
        overflow: auto;
        border: 2px solid gray;
        border-radius: 10px;
        box-shadow: 3px 3px 4px #888;
        background-color: white;
    }
</style>
