<script>
    import { datasetStore, eventIndexStore } from "../stores";
    import Plot from "../Plot.svelte";

    export let brushedPointsIDs, brushedPointsIntervals;

    let mds_x = [],
        mds_y = [];

    $: if (brushedPointsIntervals && brushedPointsIntervals.length > 0) {
        eventIndexStore.set(-1);
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
            ids: brushedPointsIDs,
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

    const config = {
        showTips: false,
        modeBarButtonsToRemove: ["zoom2d", "pan2d", "select2d", "lasso2d"],
        displaylogo: false,
        scrollZoom: true,
        responsive: true,
    };

    let matchText = [];

    $: if (brushedPointsIDs && $eventIndexStore != -1) {
        const selectedIndex = brushedPointsIDs.findIndex(
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

        const selectedRadius = 16;
        layout.shapes = [
            {
                type: "circle",
                xsizemode: "pixel",
                ysizemode: "pixel",
                fillcolor: "#1f77b4",
                xanchor: mds_x[selectedIndex],
                yanchor: mds_y[selectedIndex],

                x0: -selectedRadius / 2,
                x1: selectedRadius / 2,
                y0: -selectedRadius / 2,
                y1: selectedRadius / 2,

                line: { color: "black", width: 4 },
            },
            {
                // Workaround for what I think is a bug in PlotlyJS:
                // The previous shape uses "pixel" as the x and y sizemodes,
                // which causes the lasso select to use the wrong coordinates.
                // This sets the last shape to use "scaled" sizemodes which seems to fix it.
                type: "path",
                path: "",
                xsizemode: "scaled",
                ysizemode: "scaled",
            },
        ];
    } else {
        layout.shapes = [];
    }
</script>

<Plot
    {data}
    {layout}
    {config}
    on:click={(event) => {
        const trace = event.detail.points[0];
        eventIndexStore.set(trace.id);
    }}
/>
