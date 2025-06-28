<script>
    const fetchConfig = async () => {
        const response = await fetch("api/config");
        return await response.json();
    };

    let configPromise = $state(fetchConfig());

    const getConfig = () => {
        configPromise = fetchConfig();
    };

    const downloadConfig = (data) => {
        const blob = new Blob([JSON.stringify(data, null, 4)], {
            type: "text/plain",
        });
        const fileURL = window.URL.createObjectURL(blob);
        const fileAnchor = document.createElement("a");
        fileAnchor.href = fileURL;
        fileAnchor.download =
            data.stream_name.replace(" ", "_").replace("/", "") +
            "_config.json";
        fileAnchor.click();
    };
</script>

<div
    id="configModal"
    class="modal fade"
    data-bs-backdrop="static"
    tabindex="-1"
>
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Configuration</h5>
                <button
                    type="button"
                    class="btn-close"
                    data-bs-dismiss="modal"
                    aria-label="Close"
                ></button>
            </div>
            <div class="modal-body">
                {#await configPromise}
                    Loading configuration...
                {:then data}
                    <p>
                        <strong>Input:</strong>
                        {data.stream_name}/transients
                    </p>
                    <p>
                        <strong>Output:</strong>
                        {data.stream_name}/events
                    </p>

                    <div class="fw-bold">Exemplars:</div>
                    <ul class="list-group list-group-flush">
                        {#each data.exemplars as exemplar}
                            <li class="list-group-item">
                                <div>
                                    [{exemplar.start_ts}, {exemplar.end_ts}]
                                </div>
                                <ul>
                                    {#each exemplar.transitions as transition}
                                        <li>
                                            {transition[0]}::{transition[1]}&rarr;{transition[2]}
                                        </li>
                                    {/each}
                                </ul>
                            </li>
                        {/each}
                    </ul>

                    <div class="fw-bold">Loads:</div>
                    <ul class="list-group list-group-flush">
                        {#each Object.entries(data.loads) as [loadName, loadInfo]}
                            <li class="list-group-item">
                                <div>{loadName}</div>
                                <ul>
                                    {#each Object.entries(loadInfo.states) as [stateName, stateInfo]}
                                        <li>
                                            {stateName}: [{stateInfo.map((x) =>
                                                x.toFixed(1),
                                            )}] W
                                        </li>
                                    {/each}
                                </ul>
                            </li>
                        {/each}
                    </ul>
                {:catch}
                    Connection error
                {/await}
            </div>
            <div class="modal-footer">
                {#await configPromise then data}
                    <button
                        type="button"
                        class="btn btn-primary"
                        onclick={() => downloadConfig(data)}
                    >
                        Download
                    </button>
                {/await}
            </div>
        </div>
    </div>
</div>

<button
    type="button"
    class="btn btn-secondary btn-sm"
    data-bs-toggle="modal"
    data-bs-target="#configModal"
    onclick={getConfig}
>
    Configuration
</button>
