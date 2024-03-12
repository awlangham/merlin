<script>
    import { createEventDispatcher, onDestroy } from "svelte";
    import Plot from "../Plot.svelte";
    import { slide } from "svelte/transition";

    export let eventData,
        transientData,
        transientPromise,
        selected,
        confirmDelete,
        deleteEvent;

    const dispatch = createEventDispatcher();

    const formatTime = (timestampString) => {
        const timestampDate = new Date(timestampString);
        return timestampDate.toLocaleTimeString(undefined, { hour12: false });
    };

    const layout = {
            autosize: true,
            margin: { l: 60, r: 20, b: 40, t: 20 },
            xaxis: {
                title: { text: "Time (s)" },
            },
            yaxis: {
                title: { text: "Power (W)" },
            },
        },
        config = { staticPlot: true };

    onDestroy(() => {
        if (selected) {
            dispatch("selected");
        }
    });
</script>

<div class="transient-div" timestamp={eventData.timestamp}>
    <button
        class="transient-button"
        on:click={() => {
            dispatch("selected");
        }}
        class:selected
    >
        <div class="event-timestamp">
            {formatTime(eventData.timestamp)}
        </div>
        <div class="load-type">{eventData.load_type}</div>
        <div class="event-type">
            {eventData.event_type ? eventData.event_type : "---"}
        </div>
        <div class="event-label">
            {eventData.label ? eventData.label : "unlabeled"}
        </div>
    </button>

    {#if selected}
        {#await transientPromise}
            <div>Waiting...</div>
        {:then}
            <div in:slide>
                <div class="transient-plot-div">
                    <Plot data={transientData} {layout} {config} />
                </div>
                <div class="event-buttons-div">
                    <button on:click={deleteEvent} class="delete-event-btn">
                        {#if confirmDelete}
                            Really?
                        {:else}
                            Delete Event
                        {/if}
                    </button>
                </div>
            </div>
        {/await}
    {/if}
</div>

<style>
    .transient-plot-div {
        height: 300px;
    }

    .transient-button.selected {
        font-weight: bold;
        border-bottom: none;
    }

    .transient-button {
        cursor: pointer;
        display: flex;
        width: 100%;
        background-color: white;
        padding-top: 10px;
        border: none;
    }

    .event-type {
        width: 18%;
    }

    .event-timestamp {
        width: 20%;
    }

    .load-type,
    .event-label {
        width: 31%;
    }

    .event-timestamp,
    .event-type,
    .load-type {
        border-right: 1px solid lightgray;
    }

    .transient-button.selected .event-timestamp {
        border-right-color: gray;
    }

    .transient-div {
        padding-bottom: 10px;
        border-bottom: 2px solid gray;
        border-bottom-left-radius: 10px;
        border-bottom-right-radius: 10px;
        background-color: white;
    }

    .event-buttons-div {
        text-align: right;
    }

    .delete-event-btn {
        margin-right: 20px;
    }
</style>
