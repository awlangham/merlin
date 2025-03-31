<script>
    import { datasetStore, brushedStore, eventStore } from "../stores";
    import { getEvents } from "../api-calls";

    let newLabelName;

    const putLabel = () => {
        if (!newLabelName) {
            return;
        }

        fetch("api/label?stream_name=" + $datasetStore, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                label: newLabelName,
                intervals: $brushedStore.map((point) => [
                    $eventStore[point]["start_ts"],
                    $eventStore[point]["end_ts"],
                ]),
            }),
        })
            .then((response) => response.json())
            .then((j) => {
                getEvents();
                newLabelName = "";
            });
    };
</script>

<input
    type="text"
    class="form-control form-control-sm"
    bind:value={newLabelName}
/>
<button
    id="button-label"
    disabled={$brushedStore.length === 0}
    type="button"
    class="btn btn-secondary btn-sm"
    on:click={putLabel}
>
    Label Data
</button>

<style>
    .form-control {
        width: auto;
        display: inline;
    }

    #button-label {
        margin-left: 5px;
        margin-right: 10px;
    }
</style>
