<script>
    import { eventIndexStore, eventStore } from "../stores";

    let learnName = "";
    const learnClicked = () => {
        if (learnName === "") {
            return;
        }

        const selectedEvent = $eventStore[$eventIndexStore];
        fetch(
            "api/learn?" +
                "&start_ts=" +
                selectedEvent.start_ts +
                "&end_ts=" +
                selectedEvent.end_ts +
                "&exemplar_name=" +
                learnName,
            {
                method: "PUT",
            },
        )
            .then((response) => response.json())
            .then((j) => {
                console.log(j);
            });
    };
</script>

<span class="learn-span">
    <input
        bind:value={learnName}
        type="text"
        class="form-control form-control-sm"
        placeholder="Load::State1->State2"
        disabled={$eventIndexStore == -1}
    />
    <button
        id="learn-btn"
        type="button"
        class="btn btn-secondary btn-sm"
        disabled={$eventIndexStore == -1}
        on:click={learnClicked}
    >
        Learn
    </button>
</span>

<style>
    .learn-span {
        position: absolute;
        right: 10px;
    }

    .learn-span input {
        width: auto;
        display: inline;
    }
</style>
