<script>
    import { config, layout } from "./plot-settings";
    import { eventStore, eventIndexStore, datasetStore } from "../stores";

    import Plot from "../Plot.svelte";

    let timestamps,
        transient_P,
        transient_Q,
        transientData = [{ name: "P" }, { name: "Q" }];

    export const clearTransientPlot = () => {
        timestamps = undefined;
        transient_P = undefined;
        transient_Q = undefined;
        transientData = [{ name: "P" }, { name: "Q" }];
    };

    $: if ($eventIndexStore != -1) {
        clearTransientPlot();
        const selectedEvent = $eventStore[$eventIndexStore];
        fetch(
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

    const getBaseline = (dataArray) => {
        const baselineLength = 5;

        if (dataArray.length <= baselineLength) {
            return 0;
        }

        const startAvg = dataArray.slice(0, baselineLength).reduce((a, b) => a + b) / baselineLength;
        const endAvg = dataArray.slice(-baselineLength).reduce((a, b) => a + b) / baselineLength;
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

<style>
    .transient-plot-div {
        height: 275px;
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
