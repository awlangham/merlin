<script>
    import Plot from "./Plot.svelte";

    export let selectedEventID, brushedPointsIDs, selectedStreamName;

    let sortedIDs,
        mds0 = [],
        mds1 = [];

    $: if (brushedPointsIDs) {
        sortedIDs = [...brushedPointsIDs].sort((a, b) => a - b);
    }

    $: if (brushedPointsIDs && brushedPointsIDs.length > 0) {
        selectedEventID = -1;
        mds0 = [];
        mds1 = [];

        fetch("api/" + selectedStreamName + "/mds", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ids: sortedIDs }),
        })
            .then((response) => response.json())
            .then((j) => {
                mds0 = j.data0;
                mds1 = j.data1;
            });
    }

    $: data = [
        {
            x: mds0,
            y: mds1,
            text: matchText,
            ids: sortedIDs,
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

    $: if (sortedIDs && selectedEventID != -1) {
        const selectedIndex = sortedIDs.findIndex(
            (id) => id === selectedEventID
        );

        matchText = mds0.map((x, i) => {
            const y = mds1[i];
            const distance = Math.sqrt(
                (mds0[selectedIndex] - x) ** 2 + (mds1[selectedIndex] - y) ** 2
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
                xanchor: mds0[selectedIndex],
                yanchor: mds1[selectedIndex],

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
        selectedEventID = trace.id;
    }}
/>
