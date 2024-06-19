<script>
    import { modeStore } from "../stores";
    import FeatureViewer from "./FeatureViewer.svelte";
    import MdsViewer from "./MdsViewer.svelte";

    export let featureData, brushedPoints, clusterData;

    let hasSelection1 = false,
        hasSelection2 = false,
        brushedPoints1,
        brushedPoints2;

    $: if (!hasSelection1 && !hasSelection2) {
        if ($modeStore === "explore") {
            brushedPoints1 = undefined;
            brushedPoints2 = undefined;
        } else if ($modeStore === "crossbrush") {
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
        cursor={$modeStore === "mds" ? "crossbrush" : $modeStore}
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
    {#if $modeStore === "mds"}
        <MdsViewer brushedPointsIDs={brushedPoints} {brushedPointsIntervals} />
    {:else}
        <FeatureViewer
            {featureData}
            sequence={1}
            cursor={$modeStore}
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
