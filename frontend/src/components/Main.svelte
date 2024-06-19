<script>
    import {
        eventIndexStore,
        eventStore,
        filterStore,
        brushedStore,
    } from "./stores";

    import Logo from "./Logo.svelte";
    import TopBar from "./TopBar.svelte";
    import Toolbox from "./Toolbox.svelte";
    import TransientViewer from "./transients/TransientViewer.svelte";
    import FeaturePlots from "./features/FeaturePlots.svelte";

    let topBar, featurePlots;

    $: if ($eventStore && featurePlots) {
        featurePlots.clearBrushedSelection();
    }

    $: $filterStore, eventIndexStore.set(-1), ($brushedStore = undefined);
</script>

<div class="main">
    <Logo />
    <TopBar bind:this={topBar} />
    <div class="left-column">
        <Toolbox
            on:clear={featurePlots.clearBrushedSelection}
            on:refresh_events={topBar.getEvents}
        />
        <TransientViewer />
    </div>
    <FeaturePlots bind:this={featurePlots} />
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
