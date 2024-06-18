<script>
    import {
        unclusteredColor,
        selectedColor,
        colors,
        powerFeatures,
        labels,
    } from "../../utilities.js";

    import { eventIndexStore } from "../stores";
    import Plot from "../Plot.svelte";
    import { createEventDispatcher } from "svelte";

    const dispatch = createEventDispatcher();

    export let featureData,
        sequence = 0,
        mode,
        brushedPoints,
        clusterData;

    let x_feature, y_feature;

    // Set default views upon page load
    if (sequence == 1) {
        x_feature = powerFeatures[0];
        y_feature = powerFeatures[2];
    } else {
        x_feature = powerFeatures[0];
        y_feature = powerFeatures[1];
    }

    $: if (clusterData && data) {
        data[0].marker.color = clusterData.map((cluster) =>
            cluster === -1 ? unclusteredColor : colors[cluster],
        );
    }

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

    let selectedEventID;
    eventIndexStore.subscribe((value) => {
        selectedEventID = value;
    });

    $: if (mode === "explore") {
        layout.dragmode = "pan";
    } else if (mode === "crossbrush") {
        layout.dragmode = "lasso";
    }

    $: if (featureData[x_feature] && featureData[y_feature]) {
        data = [
            {
                selectedpoints: brushedPoints,
                name: "Events",
                x: featureData[x_feature],
                y: featureData[y_feature],
                ids: featureData["id"],
                type: "scattergl",
                mode: "markers",
                selected: {
                    marker: {
                        size: 12,
                        color: selectedColor,
                        opacity: 0.8,
                    },
                },
                unselected: {
                    marker: { opacity: 0.1 },
                },
                marker: { size: 10, opacity: 0.3 },
            },
        ];

        layout.xaxis.title = { text: labels[x_feature] };
        layout.yaxis.title = { text: labels[y_feature] };
    }

    $: if (selectedEventID != -1) {
        const selectedRadius = 16;
        layout.shapes = [
            {
                type: "circle",
                xsizemode: "pixel",
                ysizemode: "pixel",
                fillcolor: "#1f77b4",
                xanchor: featureData[x_feature][selectedEventID],
                yanchor: featureData[y_feature][selectedEventID],

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

<div>
    <select bind:value={y_feature}>
        {#each powerFeatures as power_feature}
            <option>{power_feature}</option>
        {/each}
    </select>
    vs.
    <select bind:value={x_feature}>
        {#each powerFeatures as power_feature}
            <option>{power_feature}</option>
        {/each}
    </select>
</div>

<div class="feature-space-map">
    <div
        class="plot-container"
        style="--show-lasso-selection: {mode === 'crossbrush'
            ? 'inline'
            : 'none'}"
    >
        <Plot
            {data}
            {layout}
            {config}
            on:click={(event) => {
                const trace = event.detail.points[0];
                eventIndexStore.set(trace.id);
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
</div>

<style>
    .feature-space-map {
        width: 100%;
        height: 90%;
    }

    :global(.selectionlayer),
    :global(.zoomlayer) {
        display: var(--show-lasso-selection);
    }

    .plot-container {
        width: 100%;
        height: 100%;
    }
</style>
