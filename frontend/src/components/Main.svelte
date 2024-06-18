<script>
    import TransientViewer from "./transients/TransientViewer.svelte";
    import DownloadData from "./DownloadData.svelte";
    import FeaturePlots from "./features/FeaturePlots.svelte";
    import Logo from "./Logo.svelte";
    import TopBar from "./TopBar.svelte";

    let topBar;

    let mode = "explore",
        selectedStreamName = "",
        selectedEventID = -1,
        brushedPoints,
        featurePlots,
        newLabelName,
        filterType,
        clusterData;

    // events: array of objects with props {timestamp, start_ts, end_ts, P_ss, Q_ss, P_pk, Q_pk}
    let events = [];

    $: if (events && featurePlots) {
        featurePlots.clearBrushedSelection();
    }

    $: loadTypes = [...new Set(events.map((event) => event.load_type))].sort();
    $: filterType, (selectedEventID = -1), (brushedPoints = undefined);

    const putLabel = () => {
        if (!newLabelName) {
            return;
        }

        fetch("api/label?stream_name=" + selectedStreamName, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                label: newLabelName,
                intervals: brushedPoints.map((point) => [
                    featureData["start_ts"][point],
                    featureData["end_ts"][point],
                ]),
            }),
        })
            .then((response) => response.json())
            .then((j) => {
                topBar.getEvents();
                newLabelName = "";
            });
    };

    const unselectPoint = () => {
        selectedEventID = -1;
    };

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
    <TopBar
        bind:this={topBar}
        bind:selectedStreamName
        bind:events
        bind:clusterData
        bind:selectedEventID
    />
    <div class="left-column">
        <div id="tool-div">
            <div>
                Filter by:
                <select bind:value={filterType}>
                    <option value="">-- show all --</option>
                    {#each loadTypes as loadType}
                        <option>{loadType}</option>
                    {/each}
                </select>
            </div>

            <div>
                Tool:
                <select bind:value={mode}>
                    <option value="explore">Explore 🔦</option>
                    <option value="crossbrush">CrossBrush 🖌️</option>
                    <option value="mds">MDS 🔍</option>
                </select>

                <button
                    class:visible={selectedEventID != -1}
                    id="unselect-btn"
                    on:click={unselectPoint}
                >
                    Unselect Point ⭕️
                </button>
            </div>

            {#if brushedPoints}
                <div>
                    <input bind:value={newLabelName} />
                    <button on:click={putLabel}>Label Data</button>
                </div>
                <div>
                    <button on:click={featurePlots.clearBrushedSelection}>
                        Clear Brush Selection
                    </button>
                    <DownloadData
                        stream={selectedStreamName}
                        intervals={brushedPoints.map((point) => [
                            featureData["start_ts"][point],
                            featureData["end_ts"][point],
                        ])}
                    />
                </div>
            {/if}
        </div>

        <TransientViewer {events} bind:selectedEventID {selectedStreamName} />
    </div>
    <FeaturePlots
        bind:this={featurePlots}
        {featureData}
        bind:selectedEventID
        {mode}
        bind:brushedPoints
        {selectedStreamName}
        {clusterData}
    />
</div>

<style>
    .main {
        display: flex;
        flex-wrap: wrap;
    }

    #unselect-btn {
        visibility: hidden;
        margin-left: auto;
    }

    #unselect-btn.visible {
        visibility: visible;
    }

    #tool-div {
        height: 110px;
        border: 2px solid gray;
        border-radius: 10px;
        box-shadow: 3px 3px 4px #888;
        margin-bottom: 10px;
        padding-top: 10px;
        padding-bottom: 10px;
        padding-left: 5px;
        padding-right: 5px;
        background-color: white;
    }

    .left-column {
        width: 25%;
    }

    #tool-div div {
        padding-bottom: 5px;
    }
</style>
