<script>
    import {
        datasetStore,
        eventStore,
        eventIndexStore,
        brushedStore,
    } from "../stores";

    import { mdsConfig, makeSelectionShape } from "./plot-settings";

    import Plot from "../Plot.svelte";

    let mds_x = [],
        mds_y = [];

    $: brushedPointsIntervals = $brushedStore.map((point) => [
        $eventStore[point]["start_ts"],
        $eventStore[point]["end_ts"],
    ]);

    $: if (brushedPointsIntervals.length > 0) {
        $eventIndexStore = -1;
        mds_x = [];
        mds_y = [];

        fetch("api/mds?stream_name=" + $datasetStore, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ intervals: brushedPointsIntervals }),
        })
            .then((response) => response.json())
            .then((j) => {
                mds_x = j.data0;
                mds_y = j.data1;
            });
    }

    $: data = [
        {
            x: mds_x,
            y: mds_y,
            text: matchText,
            ids: $brushedStore,
            type: "scattergl",
            mode: "markers",
            marker: { size: 10, opacity: 0.3 },
        },
    ];

    let layout = {
        autosize: true,
        margin: { l: 70, r: 20, b: 40, t: 20 },
        dragmode: "pan",
        uirevision: true,
        xaxis: {
            title: { text: "MDS 0" },
            fixedrange: false,
            range: [-1, 1],
        },
        yaxis: {
            title: { text: "MDS 1" },
            fixedrange: false,
            range: [-1, 1],
        },
        showlegend: false,
    };

    let matchText = [];

    $: if ($brushedStore && $eventIndexStore != -1) {
        const selectedIndex = $brushedStore.findIndex(
            (id) => id === $eventIndexStore,
        );

        matchText = mds_x.map((x, i) => {
            const y = mds_y[i];
            const distance = Math.sqrt(
                (mds_x[selectedIndex] - x) ** 2 +
                    (mds_y[selectedIndex] - y) ** 2,
            );

            const percentMatch = (1 - distance) * 100;
            return +percentMatch.toFixed(2) + "% match";
        });

        layout.shapes = makeSelectionShape(
            mds_x[selectedIndex],
            mds_y[selectedIndex],
        );
    } else {
        layout.shapes = [];
    }
</script>

<Plot
    {data}
    {layout}
    config={mdsConfig}
    on:click={(event) => {
        const trace = event.detail.points[0];
        eventIndexStore.set(trace.id);
    }}
/>
