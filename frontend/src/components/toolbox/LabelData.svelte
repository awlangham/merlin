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

<div>
    <input bind:value={newLabelName} />
    <button on:click={putLabel}>Label Data</button>
</div>
