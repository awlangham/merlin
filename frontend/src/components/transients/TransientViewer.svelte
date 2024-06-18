<script>
    import VirtualList from "svelte-virtual-list-ce";

    import { tick } from "svelte";
    import TransientDiv from "./TransientDiv.svelte";
    import Plot from "../Plot.svelte";
    import { config, layout } from "./plot-settings";

    export let events, selectedEventID, selectedStreamName;

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
        scrollToIndex(selectedEventID, { behavior: "instant" });

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
    $: if (selectedEventID != -1) {
        clearTransientPlot();
        scrollToSelected();

        const selectedEvent = events[selectedEventID];
        transientPromise = fetch(
            "api/transient?" +
                "stream_name=" +
                selectedStreamName +
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
        firstVisibleTimestamp = events[virtualListStart].timestamp;
        lastVisibleTimestamp = events[virtualListEnd - 1].timestamp;
    }

    const copyTimestamps = () => {
        const eventData = events[selectedEventID];
        navigator.clipboard.writeText(
            eventData.start_ts + ", " + eventData.end_ts,
        );
    };
</script>

<div class="transient-plot-div">
    <Plot data={transientData} {layout} {config} />
    {#if selectedEventID != -1}
        <button id="copy-timestamps-btn" on:click={copyTimestamps}>
            Copy timestamps
        </button>
    {/if}
</div>

<div class="timespan-date">
    Start: {firstVisibleTimestamp}
</div>

<div id="transient-viewer">
    {#if events}
        <div class="list" bind:this={listDiv}>
            <VirtualList
                bind:start={virtualListStart}
                bind:end={virtualListEnd}
                bind:scrollToIndex
                items={events}
                let:item
            >
                <TransientDiv
                    eventData={item}
                    selected={selectedEventID === item.id}
                    on:selected={() => {
                        if (selectedEventID === item.id) {
                            selectedEventID = -1;
                        } else {
                            selectedEventID = item.id;
                        }
                    }}
                />
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
