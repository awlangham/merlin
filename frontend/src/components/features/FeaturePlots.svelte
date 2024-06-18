<script>
    import FeatureViewer from "./FeatureViewer.svelte";
    import MdsViewer from "./MdsViewer.svelte";

    export let featureData,
        selectedEventID,
        mode,
        brushedPoints,
        clusterData;

    let hasSelection1 = false,
        hasSelection2 = false,
        brushedPoints1,
        brushedPoints2;

    $: if (!hasSelection1 && !hasSelection2) {
        if (mode === "explore") {
            brushedPoints1 = undefined;
            brushedPoints2 = undefined;
        } else if (mode === "crossbrush") {
            brushedPoints1 = [];
            brushedPoints2 = [];
        }
    }

    $: if (hasSelection1) {
        brushedPoints2 = brushedPoints;
    } else if (hasSelection2) {
        brushedPoints1 = brushedPoints;
    }

    export const clearBrushedSelection = () => {
        hasSelection1 = false;
        hasSelection2 = false;
        brushedPoints = undefined;
    };

    let brushedPointsIntervals;
    $: if (brushedPoints) {
        brushedPointsIntervals = brushedPoints.map((point) => [
            featureData["start_ts"][point],
            featureData["end_ts"][point],
        ]);
    }
</script>

<div class="feature-viewer">
    <FeatureViewer
        {featureData}
        bind:selectedEventID
        mode={mode === "mds" ? "crossbrush" : mode}
        brushedPoints={brushedPoints1}
        {clusterData}
        on:brush={(d) => {
            brushedPoints = d.detail;
            hasSelection1 = true;
            hasSelection2 = false;
        }}
    />
</div>

<div class="feature-viewer">
    {#if mode === "mds"}
        <MdsViewer
            bind:selectedEventID
            brushedPointsIDs={brushedPoints}
            {brushedPointsIntervals}
        />
    {:else}
        <FeatureViewer
            {featureData}
            bind:selectedEventID
            sequence={1}
            {mode}
            {clusterData}
            brushedPoints={brushedPoints2}
            on:brush={(d) => {
                brushedPoints = d.detail;
                hasSelection1 = false;
                hasSelection2 = true;
            }}
        />
    {/if}
</div>

<style>
    .feature-viewer {
        display: flex;
        height: calc(100vh - 110px);
        width: 35%;
        border: 2px solid gray;
        border-radius: 10px;
        padding: 10px;
        margin-left: auto;
        flex-wrap: wrap;
        box-shadow: 3px 3px 4px #888;
        background-color: white;
    }
</style>
