<script>
    import { config, layout } from "./plot-settings";
    import {
        eventStore,
        eventIndexStore,
        datasetStore,
        numPhasesStore,
    } from "../stores";
    import { getStartBaseline, getEndBaseline } from "../../utilities";

    import Plot from "../Plot.svelte";
    import Learn from "./Learn.svelte";

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
                if ($numPhasesStore === 3) {
                    transientData = [
                        { name: "PA", line: { color: "#0072B2" } },
                        { name: "QA", line: { color: "#E69F00" } },
                        { name: "PB", line: { color: "#56B4E9" } },
                        { name: "QB", line: { color: "#F0E442" } },
                        { name: "PC", line: { color: "#92C5DE" } },
                        { name: "QC", line: { color: "#D55E00" } },
                    ];

                    for (const index of Array(6).keys()) {
                        transientData[index].x = j.timestamps;
                    }

                    if (selectedEvent.type === "ON to OFF") {
                        transientData[0].y = j.PA.map(
                            (p) => p - getEndBaseline(j.PA),
                        );
                        transientData[2].y = j.PB.map(
                            (p) => p - getEndBaseline(j.PB),
                        );
                        transientData[4].y = j.PC.map(
                            (p) => p - getEndBaseline(j.PC),
                        );

                        transientData[1].y = j.QA.map(
                            (q) => q - getEndBaseline(j.QA),
                        );
                        transientData[3].y = j.QB.map(
                            (q) => q - getEndBaseline(j.QB),
                        );
                        transientData[5].y = j.QC.map(
                            (q) => q - getEndBaseline(j.QC),
                        );
                    } else {
                        transientData[0].y = j.PA.map(
                            (p) => p - getStartBaseline(j.PA),
                        );
                        transientData[2].y = j.PB.map(
                            (p) => p - getStartBaseline(j.PB),
                        );
                        transientData[4].y = j.PC.map(
                            (p) => p - getStartBaseline(j.PC),
                        );

                        transientData[1].y = j.QA.map(
                            (q) => q - getStartBaseline(j.QA),
                        );
                        transientData[3].y = j.QB.map(
                            (q) => q - getStartBaseline(j.QB),
                        );
                        transientData[5].y = j.QC.map(
                            (q) => q - getStartBaseline(j.QC),
                        );
                    }
                } else {
                    transientData = [
                        { name: "P", line: { color: "#0072B2" } },
                        { name: "Q", line: { color: "#E69F00" } },
                    ];

                    for (const index of Array(2).keys()) {
                        transientData[index].x = j.timestamps;
                    }

                    if (selectedEvent.type === "ON to OFF") {
                        transientData[0].y = j.P.map(
                            (p) => p - getEndBaseline(j.P),
                        );

                        transientData[1].y = j.Q.map(
                            (q) => q - getEndBaseline(j.Q),
                        );
                    } else {
                        transientData[0].y = j.P.map(
                            (p) => p - getStartBaseline(j.P),
                        );

                        transientData[1].y = j.Q.map(
                            (q) => q - getStartBaseline(j.Q),
                        );
                    }
                }
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
    <div id="plot">
        <Plot data={transientData} {layout} {config}></Plot>
    </div>

    <div>
        <button
            id="copy-timestamps-btn"
            type="button"
            class="btn btn-secondary btn-sm"
            disabled={$eventIndexStore == -1}
            on:click={copyTimestamps}
        >
            Copy timestamps
        </button>

        <Learn></Learn>
    </div>
</div>

<style>
    #plot {
        height: 88%;
        padding-bottom: 5px;
    }

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
        margin-left: 10px;
    }
</style>
