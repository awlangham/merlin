<script>
    import { datasetStore, brushedStore, eventStore } from "../stores";

    $: intervals = $brushedStore.map((point) => [
        $eventStore[point]["start_ts"],
        $eventStore[point]["end_ts"],
    ]);

    const downloadData = () => {
        fetch("api/download?stream_name=" + $datasetStore, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ intervals: intervals }),
        })
            .then((result) => result.blob())
            .then((blob) => {
                const fileURL = window.URL.createObjectURL(blob);
                const fileAnchor = document.createElement("a");
                fileAnchor.href = fileURL;
                fileAnchor.download =
                    $datasetStore.replace(" ", "_").replace("/", "") +
                    "_transients.npz";
                fileAnchor.click();
            });
    };
</script>

<button
    disabled={$brushedStore.length === 0}
    type="button"
    class="btn btn-secondary btn-sm"
    on:click={downloadData}
>
    Download Data
</button>
