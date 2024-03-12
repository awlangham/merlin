<script>
    export let stream, ids;

    const downloadData = () => {
        fetch("api/download/" + stream, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ids: ids }),
        })
            .then((result) => result.blob())
            .then((blob) => {
                const fileURL = window.URL.createObjectURL(blob);
                const fileAnchor = document.createElement("a");
                fileAnchor.href = fileURL;
                fileAnchor.download = stream + "_transients.npz";
                fileAnchor.click();
            });
    };
</script>

<button on:click={downloadData}> Download Data </button>
