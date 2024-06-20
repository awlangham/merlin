<script>
    import { eventIndexStore } from "../stores";

    export let eventData;

    $: selected = $eventIndexStore === eventData.id;

    const formatTime = (timestampString) => {
        const timestampDate = new Date(timestampString);
        return timestampDate.toLocaleTimeString(undefined, { hour12: false });
    };
</script>

<div class="transient-list-item">
    <button
        class="transient-button"
        on:click={() => {
            if ($eventIndexStore === eventData.id) {
                $eventIndexStore = -1;
            } else {
                $eventIndexStore = eventData.id;
            }
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

    .transient-list-item {
        padding-bottom: 10px;
        border-bottom: 2px solid gray;
        border-bottom-left-radius: 10px;
        border-bottom-right-radius: 10px;
        background-color: white;
    }
</style>
