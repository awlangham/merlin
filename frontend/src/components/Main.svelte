<script>
    import { eventIndexStore, eventStore } from "./stores";
    import TransientViewer from "./transients/TransientViewer.svelte";
    import Toolbox from "./Toolbox.svelte";
    import FeaturePlots from "./features/FeaturePlots.svelte";
    import Logo from "./Logo.svelte";
    import TopBar from "./TopBar.svelte";

    let topBar;

    let brushedPoints, featurePlots, filterType, clusterData;

    $: if ($eventStore && featurePlots) {
        featurePlots.clearBrushedSelection();
    }

    $: filterType, eventIndexStore.set(-1), (brushedPoints = undefined);

    $: filteredEvents =
        filterType === ""
            ? $eventStore
            : $eventStore.filter((event) => event.load_type === filterType);

    let featureData = {};
    $: if (filterType === "") {
        featureData["Steady-State P"] = $eventStore.map(({ P_ss }) => P_ss);
        featureData["Steady-State Q"] = $eventStore.map(({ Q_ss }) => Q_ss);
        featureData["Peak P"] = $eventStore.map(({ P_pk }) => P_pk);
        featureData["Peak Q"] = $eventStore.map(({ Q_pk }) => Q_pk);
        featureData["id"] = $eventStore.map(({ id }) => id);
        featureData["start_ts"] = $eventStore.map(({ start_ts }) => start_ts);
        featureData["end_ts"] = $eventStore.map(({ end_ts }) => end_ts);
    } else {
        featureData["Steady-State P"] = filteredEvents.map(({ P_ss }) => P_ss);
        featureData["Steady-State Q"] = filteredEvents.map(({ Q_ss }) => Q_ss);
        featureData["Peak P"] = filteredEvents.map(({ P_pk }) => P_pk);
        featureData["Peak Q"] = filteredEvents.map(({ Q_pk }) => Q_pk);
        featureData["id"] = filteredEvents.map(({ id }) => id);
        featureData["start_ts"] = filteredEvents.map(
            ({ start_ts }) => start_ts,
        );
        featureData["end_ts"] = filteredEvents.map(({ end_ts }) => end_ts);
    }
</script>

<div class="main">
    <Logo />
    <TopBar bind:this={topBar} bind:clusterData />
    <div class="left-column">
        <Toolbox
            bind:filterType
            {featureData}
            {brushedPoints}
            on:clear={featurePlots.clearBrushedSelection}
            on:refresh_events={topBar.getEvents}
        />
        <TransientViewer />
    </div>
    <FeaturePlots
        bind:this={featurePlots}
        {featureData}
        bind:brushedPoints
        {clusterData}
    />
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
