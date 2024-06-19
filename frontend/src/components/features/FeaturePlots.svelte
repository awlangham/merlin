<script>
    import { modeStore, brushedStore, eventStore } from "../stores";
    import FeatureViewer from "./FeatureViewer.svelte";
    import MdsViewer from "./MdsViewer.svelte";


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
        brushedPoints2 = $brushedStore;
    } else if (hasSelection2) {
        brushedPoints1 = $brushedStore;
    }

    export const clearBrushedSelection = () => {
        hasSelection1 = false;
        hasSelection2 = false;
        $brushedStore = undefined;
    };

    let brushedPointsIntervals;
    $: if ($brushedStore) {
        brushedPointsIntervals = $brushedStore.map((point) => [
            $eventStore[point]["start_ts"],
            $eventStore[point]["end_ts"],
        ]);
    }
</script>

<div class="feature-viewer">
    <FeatureViewer
        cursor={$modeStore === "mds" ? "crossbrush" : $modeStore}
        brushedPoints={brushedPoints1}
        on:brush={(d) => {
            $brushedStore = d.detail;
            hasSelection1 = true;
            hasSelection2 = false;
        }}
    />
</div>

<div class="feature-viewer">
    {#if $modeStore === "mds"}
        <MdsViewer brushedPointsIDs={$brushedStore} {brushedPointsIntervals} />
    {:else}
        <FeatureViewer
            sequence={1}
            cursor={$modeStore}
            brushedPoints={brushedPoints2}
            on:brush={(d) => {
                $brushedStore = d.detail;
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
