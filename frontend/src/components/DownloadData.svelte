<script>
    export let stream, intervals;

    const downloadData = () => {
        fetch("api/download?stream_name=" + stream, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ intervals: intervals }),
        })
            .then((result) => result.blob())
            .then((blob) => {
                const fileURL = window.URL.createObjectURL(blob);
                const fileAnchor = document.createElement("a");
                fileAnchor.href = fileURL;
                fileAnchor.download = stream.replace(' ', '_').replace('/', '') + "_transients.npz";
                fileAnchor.click();
            });
    };
</script>

<button on:click={downloadData}> Download Data </button>
