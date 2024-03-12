<script>
    import Plot from "../Plot.svelte";
    import { createEventDispatcher } from "svelte";

    const dispatch = createEventDispatcher();

    export let x_data,
        x_label,
        y_data,
        y_label,
        ids,
        selectedEventID,
        mode,
        brushedPoints;

    let data,
        layout = {
            autosize: true,
            margin: { l: 70, r: 20, b: 40, t: 20 },
            dragmode: "pan",
            uirevision: true,
            xaxis: { fixedrange: false },
            yaxis: { fixedrange: false },
            showlegend: false,
        },
        config = {
            showTips: false,
            modeBarButtonsToRemove: ["zoom2d", "select2d", "pan2d", "lasso2d"],
            displaylogo: false,
            scrollZoom: true,
            responsive: true,
        };

    $: if (mode === "explore") {
        layout.dragmode = "pan";
    } else if (mode === "crossbrush") {
        layout.dragmode = "lasso";
    }

    $: if (x_data && y_data) {
        data = [
            {
                selectedpoints: brushedPoints,
                name: "Events",
                x: x_data,
                y: y_data,
                ids: ids,
                type: "scattergl",
                mode: "markers",
                selected: {
                    marker: {
                        size: 12,
                        color: "orange",
                        opacity: 0.8,
                    },
                },
                unselected: {
                    marker: { opacity: 0.1 },
                },
                marker: { size: 10, opacity: 0.3 },
            },
        ];

        layout.xaxis.title = { text: x_label };
        layout.yaxis.title = { text: y_label };
    }

    $: if (selectedEventID != -1) {
        const selectedRadius = 16;
        layout.shapes = [
            {
                type: "circle",
                xsizemode: "pixel",
                ysizemode: "pixel",
                fillcolor: "#1f77b4",
                xanchor: x_data[selectedEventID],
                yanchor: y_data[selectedEventID],

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

<div
    class="plot-container"
    style="--show-lasso-selection: {mode === 'crossbrush' ? 'inline' : 'none'}"
>
    <Plot
        {data}
        {layout}
        {config}
        on:click={(event) => {
            const trace = event.detail.points[0];
            selectedEventID = trace.id;
        }}
        on:selected={(event) => {
            if (event.detail.selections.length > 0) {
                dispatch(
                    "brush",
                    event.detail.points.map((point) => point.pointIndex),
                );
            }
        }}
    />
</div>

<style>
    :global(.selectionlayer),
    :global(.zoomlayer) {
        display: var(--show-lasso-selection);
    }

    .plot-container {
        width: 100%;
        height: 100%;
    }
</style>
