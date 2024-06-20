<script>
    import {
        datasetStore,
        eventStore,
        eventIndexStore,
        brushedStore,
    } from "../stores";

    import { mdsConfig, makeSelectionShape, mdsLayout } from "./plot-settings";

    import Plot from "../Plot.svelte";

    let mdsX = [],
        mdsY = [];

    $: brushedPointsIntervals = $brushedStore.map((point) => [
        $eventStore[point]["start_ts"],
        $eventStore[point]["end_ts"],
    ]);

    $: if (brushedPointsIntervals.length > 0) {
        $eventIndexStore = -1;
        mdsX = [];
        mdsY = [];

        fetch("api/mds?stream_name=" + $datasetStore, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ intervals: brushedPointsIntervals }),
        })
            .then((response) => response.json())
            .then((j) => {
                mdsX = j.data0;
                mdsY = j.data1;
            });
    }

    $: data = [
        {
            x: mdsX,
            y: mdsY,
            text: matchText,
            ids: $brushedStore,
            type: "scattergl",
            mode: "markers",
            marker: { size: 10, opacity: 0.3 },
        },
    ];

    let matchText = [];

    $: if ($brushedStore && $eventIndexStore != -1) {
        const selectedIndex = $brushedStore.findIndex(
            (id) => id === $eventIndexStore,
        );

        matchText = mdsX.map((x, i) => {
            const y = mdsY[i];
            const distance = Math.sqrt(
                (mdsX[selectedIndex] - x) ** 2 + (mdsY[selectedIndex] - y) ** 2,
            );

            const percentMatch = (1 - distance) * 100;
            return +percentMatch.toFixed(2) + "% match";
        });

        mdsLayout.shapes = makeSelectionShape(
            mdsX[selectedIndex],
            mdsY[selectedIndex],
        );
    } else {
        mdsLayout.shapes = [];
    }
</script>

<Plot
    {data}
    layout={mdsLayout}
    config={mdsConfig}
    on:click={(event) => {
        const trace = event.detail.points[0];
        eventIndexStore.set(trace.id);
    }}
/>
