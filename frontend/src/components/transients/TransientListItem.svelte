<script>
    import { eventIndexStore } from "../stores";

    export let eventData;

    $: selected = $eventIndexStore === eventData.id;

    let thisItem;
    $: if (selected) {
        thisItem.scrollIntoView();
    }

    const formatTime = (timestampString) => {
        const timestampDate = new Date(timestampString);
        return timestampDate.toLocaleTimeString(undefined, { hour12: false });
    };
</script>

<div bind:this={thisItem} class="transient-list-item">
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
        <div class="load-family">
            {eventData.load_family ? eventData.load_family : "---"}
        </div>
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

    .load-family,
    .event-label {
        width: 31%;
    }

    .event-timestamp,
    .event-type,
    .load-family {
        border-right: 1px solid lightgray;
    }

    .transient-list-item {
        padding-bottom: 10px;
        border-bottom: 2px solid gray;
        border-bottom-left-radius: 10px;
        border-bottom-right-radius: 10px;
        background-color: white;
    }
</style>
