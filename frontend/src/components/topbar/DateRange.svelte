<script>
    import { getEvents } from "../api-calls";
    import {
        rangeStartStore,
        rangeEndStore,
        rangeModeStore,
        datasetStore,
    } from "../stores";

    let interval;
    $: if ($rangeModeStore === "live") {
        interval = setInterval(() => {
            getEvents();
        }, 5000);
    } else {
        clearInterval(interval);
    }

    let selectedMode;

    const goButtonClicked = () => {
        $rangeModeStore = selectedMode;
        getEvents();
    };
</script>

<span id="date-range-span">
    <select
        disabled={$datasetStore == ""}
        id="mode-select"
        class="form-select form-select-sm"
        bind:value={selectedMode}
    >
        <option value="start">Start</option>
        <option value="end">End</option>
        <option value="live">Live</option>
    </select>

    <input
        type="date"
        class="form-control form-control-sm"
        bind:value={$rangeStartStore}
        disabled={selectedMode != "start" || $datasetStore == ""}
    />
    to
    <input
        type="date"
        class="form-control form-control-sm"
        bind:value={$rangeEndStore}
        disabled={selectedMode != "end" || $datasetStore == ""}
    />
    <button
        disabled={$datasetStore == ""}
        type="button"
        class="btn btn-secondary btn-sm"
        id="set-daterange-btn"
        on:click={goButtonClicked}>Go</button
    >
</span>

<style>
    #mode-select {
        width: auto;
        display: inline;
    }

    #date-range-span {
        margin-left: auto;
        /* margin-right: auto; */
        /* align-self: flex-end; */
    }

    .form-control {
        display: inline;
        width: auto;
    }
</style>
