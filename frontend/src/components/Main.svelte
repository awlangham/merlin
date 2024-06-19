<script>
    import { eventIndexStore, eventStore, filterStore } from "./stores";
    import TransientViewer from "./transients/TransientViewer.svelte";
    import Toolbox from "./Toolbox.svelte";
    import FeaturePlots from "./features/FeaturePlots.svelte";
    import Logo from "./Logo.svelte";
    import TopBar from "./TopBar.svelte";

    let topBar;

    let brushedPoints, featurePlots, clusterData;

    $: if ($eventStore && featurePlots) {
        featurePlots.clearBrushedSelection();
    }

    $: $filterStore, eventIndexStore.set(-1), (brushedPoints = undefined);
</script>

<div class="main">
    <Logo />
    <TopBar bind:this={topBar} bind:clusterData />
    <div class="left-column">
        <Toolbox
            {brushedPoints}
            on:clear={featurePlots.clearBrushedSelection}
            on:refresh_events={topBar.getEvents}
        />
        <TransientViewer />
    </div>
    <FeaturePlots bind:this={featurePlots} bind:brushedPoints {clusterData} />
</div>

<style>
    .main {
        display: flex;
        flex-wrap: wrap;
    }

    .left-column {
        width: 25%;
    }
</style>
