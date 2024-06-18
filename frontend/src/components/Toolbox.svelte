<script>
    import { createEventDispatcher } from "svelte";
    import { datasetStore, eventIndexStore } from "./stores";
    import DownloadData from "./DownloadData.svelte";

    const dispatch = createEventDispatcher();

    export let filterType, mode, loadTypes, brushedPoints, featureData;

    let selectedStreamName;
    datasetStore.subscribe((value) => {
        selectedStreamName = value;
    });

    let selectedEventID;
    eventIndexStore.subscribe((value) => {
        selectedEventID = value;
    });

    let newLabelName;

    const unselectPoint = () => {
        eventIndexStore.set(-1);
    };

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
                dispatch("refresh_events");
                newLabelName = "";
            });
    };
</script>

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
            <button
                on:click={() => {
                    dispatch("clear");
                }}
            >
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

<style>
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

    #tool-div div {
        padding-bottom: 5px;
    }
</style>
