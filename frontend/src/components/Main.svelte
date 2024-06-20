<script>
    import {
        eventIndexStore,
        eventStore,
        filterStore,
        brushedStore,
    } from "./stores";

    import Logo from "./Logo.svelte";
    import TopBar from "./topbar/TopBar.svelte";
    import Toolbox from "./toolbox/Toolbox.svelte";
    import Transients from "./transients/Transients.svelte";
    import Features from "./features/Features.svelte";

    let featurePlots;

    $: if ($eventStore && featurePlots) {
        featurePlots.clearBrushedSelection();
    }

    $: $filterStore, eventIndexStore.set(-1), ($brushedStore = undefined);
</script>

<div class="main">
    <Logo />
    <TopBar />
    <div class="left-column">
        <Toolbox on:clear={featurePlots.clearBrushedSelection} />
        <Transients />
    </div>
    <Features bind:this={featurePlots} />
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
