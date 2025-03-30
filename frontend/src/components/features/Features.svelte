<script>
    import { modeStore, brushedStore } from "../stores";
    import FeaturePlot from "./FeaturePlot.svelte";
    import MdsPlot from "./MdsPlot.svelte";

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
        $brushedStore = [];
    };
</script>

<div class="col-4">
    <div class="feature-viewer h-100">
        <FeaturePlot
            cursor={$modeStore === "mds" ? "crossbrush" : $modeStore}
            brushedPoints={brushedPoints1}
            on:brush={(d) => {
                $brushedStore = d.detail;
                hasSelection1 = true;
                hasSelection2 = false;
            }}
        />
    </div>
</div>

<div class="col-4">
    <div class="feature-viewer h-100">
        {#if $modeStore === "mds"}
            <MdsPlot />
        {:else}
            <FeaturePlot
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
</div>

<style>
    .feature-viewer {
        border: 2px solid gray;
        border-radius: 10px;
        /* padding: 10px; */
        /* margin-left: auto; */
        /* flex-wrap: wrap; */
        padding: 10px;
        /* margin-left: 0px; */
        /* margin-right: 0px; */
        box-shadow: 3px 3px 4px #888;
        background-color: white;
    }
</style>
