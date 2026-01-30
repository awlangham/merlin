<script>
    import {
        unclusteredColor,
        selectedColor,
        colors,
        threePhaseFeatures,
        singlePhaseFeatures,
        labels,
    } from "../../utilities.js";

    import {
        filterStore,
        eventStore,
        eventIndexStore,
        clusterStore,
        numPhasesStore,
    } from "../stores";

    import { makeSelectionShape, featureConfig } from "./plot-settings";

    import Plot from "../Plot.svelte";
    import { createEventDispatcher } from "svelte";

    const dispatch = createEventDispatcher();

    export let cursor,
        sequence = 0,
        brushedPoints;

    let xFeature, yFeature;

    $: filteredEvents =
        $filterStore === ""
            ? $eventStore
            : $eventStore.filter((event) => event.label === $filterStore);

    let powerFeatures;
    $: if ($numPhasesStore === 3) {
        powerFeatures = threePhaseFeatures;
    } else {
        powerFeatures = singlePhaseFeatures;
    }

    // Set default views upon page load
    $: if (sequence == 1) {
        xFeature = powerFeatures[0];
        yFeature = powerFeatures[2];
    } else {
        xFeature = powerFeatures[0];
        yFeature = powerFeatures[1];
    }

    $: if ($clusterStore && data) {
        data[0].marker.color = $clusterStore.map((cluster) =>
            cluster === -1 ? unclusteredColor : colors[cluster % colors.length],
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
        };

    $: if (cursor === "explore") {
        layout.dragmode = "pan";
    } else if (cursor === "crossbrush") {
        layout.dragmode = "lasso";
    }

    $: xData = filteredEvents.map((e) => e[xFeature]);
    $: yData = filteredEvents.map((e) => e[yFeature]);

    $: if (xData && yData) {
        data = [
            {
                selectedpoints: brushedPoints,
                name: "Events",
                x: xData,
                y: yData,
                ids: filteredEvents.map(({ id }) => id),
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

        layout.xaxis.title = { text: labels[xFeature] };
        layout.yaxis.title = { text: labels[yFeature] };
    }

    $: if ($eventIndexStore != -1) {
        const selectedEvent = filteredEvents.find(
            (e) => e.id === $eventIndexStore,
        );
        layout.shapes = makeSelectionShape(
            selectedEvent[xFeature],
            selectedEvent[yFeature],
        );
    } else {
        layout.shapes = [];
    }
</script>

<div>
    <select class="form-select form-select-sm" bind:value={yFeature}>
        {#each powerFeatures as powerFeature}
            <option>{powerFeature}</option>
        {/each}
    </select>
    vs.
    <select class="form-select form-select-sm" bind:value={xFeature}>
        {#each powerFeatures as powerFeature}
            <option>{powerFeature}</option>
        {/each}
    </select>
</div>

<div class="feature-space-map">
    <div
        class="plot-container"
        style="--show-lasso-selection: {cursor === 'crossbrush'
            ? 'inline'
            : 'none'}"
    >
        <Plot
            {data}
            {layout}
            config={featureConfig}
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
        flex: 1 1 100%;
    }

    :global(.selectionlayer),
    :global(.zoomlayer) {
        display: var(--show-lasso-selection);
    }

    .plot-container {
        width: 100%;
        height: 100%;
    }

    .form-select {
        display: inline;
        width: auto;
    }
</style>
