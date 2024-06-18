<script>
    import { eventIndexStore } from "./stores";
    import TransientViewer from "./transients/TransientViewer.svelte";
    import Toolbox from "./Toolbox.svelte";
    import FeaturePlots from "./features/FeaturePlots.svelte";
    import Logo from "./Logo.svelte";
    import TopBar from "./TopBar.svelte";

    let topBar;

    let mode = "explore",
        brushedPoints,
        featurePlots,
        filterType,
        clusterData;

    // events: array of objects with props {timestamp, start_ts, end_ts, P_ss, Q_ss, P_pk, Q_pk}
    let events = [];

    $: if (events && featurePlots) {
        featurePlots.clearBrushedSelection();
    }

    $: loadTypes = [...new Set(events.map((event) => event.load_type))].sort();
    $: filterType, eventIndexStore.set(-1), (brushedPoints = undefined);

    $: filteredEvents =
        filterType === ""
            ? events
            : events.filter((event) => event.load_type === filterType);

    let featureData = {};
    $: if (filterType === "") {
        featureData["Steady-State P"] = events.map(({ P_ss }) => P_ss);
        featureData["Steady-State Q"] = events.map(({ Q_ss }) => Q_ss);
        featureData["Peak P"] = events.map(({ P_pk }) => P_pk);
        featureData["Peak Q"] = events.map(({ Q_pk }) => Q_pk);
        featureData["id"] = events.map(({ id }) => id);
        featureData["start_ts"] = events.map(({ start_ts }) => start_ts);
        featureData["end_ts"] = events.map(({ end_ts }) => end_ts);
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
    <TopBar bind:this={topBar} bind:events bind:clusterData />
    <div class="left-column">
        <Toolbox
            bind:filterType
            bind:mode
            {featureData}
            {loadTypes}
            {brushedPoints}
            on:clear={featurePlots.clearBrushedSelection}
            on:refresh_events={topBar.getEvents}
        />
        <TransientViewer {events} />
    </div>
    <FeaturePlots
        bind:this={featurePlots}
        {featureData}
        {mode}
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
