<script>
    import { datasetStore, eventIndexStore, eventStore } from "../stores";

    import VirtualList from "svelte-virtual-list-ce";

    import { tick } from "svelte";
    import TransientDiv from "./TransientDiv.svelte";
    import Plot from "../Plot.svelte";
    import { config, layout } from "./plot-settings";

    let scrollToIndex;

    let timestamps,
        transient_P,
        transient_Q,
        transientData = [{ name: "P" }, { name: "Q" }],
        firstVisibleTimestamp = "",
        lastVisibleTimestamp = "";

    let listDiv;

    const getBaseline = (dataArray) => {
        if (dataArray.length <= 5) {
            return 0;
        }

        const startAvg = dataArray.slice(0, 5).reduce((a, b) => a + b) / 5;
        const endAvg = dataArray.slice(-5).reduce((a, b) => a + b) / 5;
        return startAvg < endAvg ? startAvg : endAvg;
    };

    $: if (timestamps && transient_P && transient_Q) {
        transientData[0].x = timestamps;
        transientData[1].x = timestamps;

        const pBaseline = getBaseline(transient_P);
        transientData[0].y = transient_P.map((x) => x - pBaseline);

        const qBaseline = getBaseline(transient_Q);
        transientData[1].y = transient_Q.map((x) => x - qBaseline);
    }

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

    const clearTransientPlot = () => {
        timestamps = undefined;
        transient_P = undefined;
        transient_Q = undefined;
        transientData = [{ name: "P" }, { name: "Q" }];
    };

    let transientPromise;
    $: if ($eventIndexStore != -1) {
        clearTransientPlot();
        scrollToSelected();

        const selectedEvent = $eventStore[$eventIndexStore];
        transientPromise = fetch(
            "api/transient?" +
                "stream_name=" +
                $datasetStore +
                "&start_ts=" +
                selectedEvent.start_ts +
                "&end_ts=" +
                selectedEvent.end_ts,
        )
            .then((response) => response.json())
            .then((j) => {
                timestamps = j.timestamps;
                transient_P = j.P;
                transient_Q = j.Q;
            });
    } else {
        clearTransientPlot();
    }

    let virtualListStart, virtualListEnd;
    $: if (virtualListStart && virtualListEnd) {
        firstVisibleTimestamp = $eventStore[virtualListStart].timestamp;
        lastVisibleTimestamp = $eventStore[virtualListEnd - 1].timestamp;
    }

    const copyTimestamps = () => {
        const eventData = $eventStore[$eventIndexStore];
        navigator.clipboard.writeText(
            eventData.start_ts + ", " + eventData.end_ts,
        );
    };
</script>

<div class="transient-plot-div">
    <Plot data={transientData} {layout} {config} />
    {#if $eventIndexStore != -1}
        <button id="copy-timestamps-btn" on:click={copyTimestamps}>
            Copy timestamps
        </button>
    {/if}
</div>

<div class="timespan-date">
    Start: {firstVisibleTimestamp}
</div>

<div id="transient-viewer">
    {#if $eventStore}
        <div class="list" bind:this={listDiv}>
            <VirtualList
                bind:start={virtualListStart}
                bind:end={virtualListEnd}
                bind:scrollToIndex
                items={$eventStore}
                let:item
            >
                <TransientDiv eventData={item} />
            </VirtualList>
        </div>
    {/if}
</div>

<div class="timespan-date">
    End: {lastVisibleTimestamp}
</div>

<style>
    .list {
        width: 100%;
        height: 100%;
    }

    .timespan-date {
        height: 20px;
        padding-bottom: 5px;
        padding-top: 5px;
        padding-left: 10px;
    }

    #transient-viewer {
        height: calc(100vh - 110px + 20px - 144px - 50px - 290px - 7px);
        overflow: auto;
        border: 2px solid gray;
        border-radius: 10px;
        box-shadow: 3px 3px 4px #888;
        background-color: white;
    }

    .transient-plot-div {
        height: 290px;
        border: 2px solid gray;
        border-radius: 10px;
        box-shadow: 3px 3px 4px #888;
        background-color: white;
        overflow: hidden;
        padding-bottom: 5px;
        position: relative;
    }

    #copy-timestamps-btn {
        position: absolute;
        left: 10px;
        bottom: 4px;
    }
</style>
