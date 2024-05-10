<script>
    import DatasetList from "./DatasetList.svelte";
    import TransientViewer from "./transients/TransientViewer.svelte";
    import DownloadData from "./DownloadData.svelte";
    import FeaturePlots from "./features/FeaturePlots.svelte";

    export let selectedStreamName = "";

    let showLoading = false,
        mode = "explore",
        autoRefresh = false,
        range_start,
        range_end,
        selectedEventID = -1,
        brushedPoints,
        featurePlots,
        newLabelName,
        filterType,
        clusterData;

    // events: array of objects with props {timestamp, start_ts, end_ts, P_ss, Q_ss, P_pk, Q_pk}
    let events = [];

    const getEvents = () => {
        showLoading = true;
        fetch("api/features?stream_name=" + selectedStreamName)
            .then((response) => response.json())
            .then((j) => {
                selectedEventID = -1;
                range_start = new Date(j.range_start / 1000);
                range_end = new Date(j.range_end / 1000);
                events = j.events;
                showLoading = false;
                featurePlots.clearBrushedSelection();
            });
    };

    const getClusters = () => {
        showLoading = true;
        fetch("api/clusters?stream_name=" + selectedStreamName)
            .then((response) => response.json())
            .then((j) => {
                clusterData = j.labels;
                showLoading = false;
            });
    };

    $: loadTypes = [...new Set(events.map((event) => event.load_type))].sort();
    $: filterType, (selectedEventID = -1), (brushedPoints = undefined);

    const putLabel = () => {
        if (!newLabelName) {
            return;
        }

        fetch("api/" + selectedStreamName + "/label/" + newLabelName, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                ids: brushedPoints.map((p) => filteredEvents[p].id),
            }),
        })
            .then((response) => response.json())
            .then((j) => {
                getEvents();
                newLabelName = "";
            });
    };

    $: if (selectedStreamName !== "") {
        getEvents();
    }

    const unselectPoint = () => {
        selectedEventID = -1;
    };

    let interval;
    $: if (autoRefresh) {
        interval = setInterval(() => {
            getEvents();
        }, 3000);
    } else {
        clearInterval(interval);
    }

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
    <div class="logo-bar">
        <span class="logo"> ⚡️ Merlin </span>
    </div>
    <div class="top-bar">
        <div class="event-stream-list">
            <DatasetList bind:selected_stream_name={selectedStreamName} />
            {#if showLoading}
                Loading...
            {/if}
        </div>

        {#if events}
            <button on:click={getEvents}>Refresh</button>
            <input
                id="auto-refresh-checkbox"
                type="checkbox"
                bind:checked={autoRefresh}
            />
            <label id="auto-refresh-label" for="auto-refresh-checkbox">
                Auto Refresh
            </label>
            <button on:click={getClusters}>Cluster</button>
        {/if}

        {#if range_start && range_end}
            <span id="date-range-span">
                {range_start.toLocaleString(undefined, { hour12: false })} to {range_end.toLocaleString(
                    undefined,
                    { hour12: false },
                )}
            </span>
        {/if}
    </div>
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

        <TransientViewer
            on:update_events={getEvents}
            {events}
            bind:selectedEventID
            {selectedStreamName}
        />
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

    .event-stream-list {
        display: flex;
    }

    .logo-bar {
        display: flex;
        width: 25%;
    }

    .logo {
        font-size: 2.3em;
        margin-left: auto;
        margin-right: auto;
    }

    .top-bar {
        display: flex;
        width: 70%;
        margin-left: auto;
        margin-right: auto;
        margin-bottom: 10px;
        padding: 10px 10px 10px 10px;
        border: 2px solid gray;
        border-radius: 10px;
        box-shadow: 3px 1px 4px #888;
        background-color: white;
    }

    #date-range-span {
        margin-left: auto;
        margin-right: auto;
    }

    #unselect-btn {
        visibility: hidden;
        margin-left: auto;
    }

    #unselect-btn.visible {
        visibility: visible;
    }

    #auto-refresh-checkbox {
        margin-left: 20px;
    }

    #auto-refresh-label {
        margin-right: 20px;
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
