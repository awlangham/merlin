<script>
    import FeatureSpaceMap from "./FeatureSpaceMap.svelte";
    import { createEventDispatcher } from "svelte";

    const dispatch = createEventDispatcher();

    export let featureData,
        selectedEventID,
        sequence = 0,
        mode,
        brushedPoints,
        clusterData;

    let x_feature, y_feature;

    // Set default views upon page load
    if (sequence == 1) {
        x_feature = "Steady-State P";
        y_feature = "Peak P";
    } else {
        x_feature = "Steady-State P";
        y_feature = "Steady-State Q";
    }

    const power_features = [
        "Steady-State P",
        "Steady-State Q",
        "Peak P",
        "Peak Q",
    ];
    const labels = {
        "Steady-State P": "Steady-State Active Power (W)",
        "Steady-State Q": "Steady-State Reactive Power (Var)",
        "Peak P": "Peak Active Power (W)",
        "Peak Q": "Peak Reactive Power (Var)",
    };

    let brushedPointsIDs;
    $: if (brushedPoints) {
        brushedPointsIDs = brushedPoints.map((point) => indexToID(point));
    }

    const indexToID = (index) => {
        return featureData["id"][index];
    };
</script>

<div>
    <select bind:value={y_feature}>
        {#each power_features as power_feature}
            <option>{power_feature}</option>
        {/each}
    </select>
    vs.
    <select bind:value={x_feature}>
        {#each power_features as power_feature}
            <option>{power_feature}</option>
        {/each}
    </select>
</div>
<div class="feature-space-map">
    <FeatureSpaceMap
        x_data={featureData[x_feature]}
        x_label={labels[x_feature]}
        y_data={featureData[y_feature]}
        y_label={labels[y_feature]}
        ids={featureData["id"]}
        clusters={clusterData}
        bind:selectedEventID
        {brushedPoints}
        {mode}
        on:brush={(d) => {
            dispatch("brush", d.detail);
        }}
    />
</div>

<style>
    .feature-space-map {
        width: 100%;
        height: 90%;
    }
</style>
