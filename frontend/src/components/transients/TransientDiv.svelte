<script>
    import { createEventDispatcher } from "svelte";

    export let eventData, selected;

    const dispatch = createEventDispatcher();

    const formatTime = (timestampString) => {
        const timestampDate = new Date(timestampString);
        return timestampDate.toLocaleTimeString(undefined, { hour12: false });
    };
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
            {eventData.type ? eventData.type : "---"}
        </div>
        <div class="event-label">
            {eventData.label ? eventData.label : "unlabeled"}
        </div>
    </button>
</div>

<style>
    .transient-button.selected {
        font-weight: bold;
        /* border-bottom: none; */
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

    /* .transient-button.selected .event-timestamp {
        border-right-color: gray;
    } */

    .transient-div {
        padding-bottom: 10px;
        border-bottom: 2px solid gray;
        border-bottom-left-radius: 10px;
        border-bottom-right-radius: 10px;
        background-color: white;
    }
</style>
