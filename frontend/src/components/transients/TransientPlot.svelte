<script>
    import { config, layout } from "./plot-settings";
    import { eventStore, eventIndexStore, datasetStore } from "../stores";
    import { getBaseline } from "../../utilities";

    import Plot from "../Plot.svelte";

    let transientData = [];

    export const clearTransientPlot = () => {
        transientData = [];
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
                transientData = [
                    { name: "A Real", line: { color: "#0072B2" } },
                    { name: "A Reactive", line: { color: "#E69F00" } },
                    { name: "B Real", line: { color: "#56B4E9" } },
                    { name: "B Reactive", line: { color: "#F0E442" } },
                    { name: "C Real", line: { color: "#92C5DE" } },
                    { name: "C Reactive", line: { color: "#D55E00" } },
                ];

                for (const index of Array(6).keys()) {
                    transientData[index].x = j.timestamps;
                }

                transientData[0].y = j.PA.map((p) => p - getBaseline(j.PA));
                transientData[2].y = j.PB.map((p) => p - getBaseline(j.PB));
                transientData[4].y = j.PC.map((p) => p - getBaseline(j.PC));

                transientData[1].y = j.QA.map((q) => q - getBaseline(j.QA));
                transientData[3].y = j.QB.map((q) => q - getBaseline(j.QB));
                transientData[5].y = j.QC.map((q) => q - getBaseline(j.QC));
            });
    } else {
        clearTransientPlot();
    }

    const copyTimestamps = () => {
        const eventData = $eventStore[$eventIndexStore];
        navigator.clipboard.writeText(
            eventData.start_ts + ", " + eventData.end_ts,
        );
    };
</script>

<div class="transient-plot-div h-100">
    <Plot data={transientData} {layout} {config} />
    {#if $eventIndexStore != -1}
        <button
            id="copy-timestamps-btn"
            type="button"
            class="btn btn-secondary btn-sm"
            on:click={copyTimestamps}
        >
            Copy timestamps
        </button>
    {/if}
</div>

<style>
    .transient-plot-div {
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
        right: 10px;
        bottom: 4px;
    }
</style>
