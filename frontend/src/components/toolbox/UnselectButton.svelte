<script>
    import { eventIndexStore } from "../stores";

    const unselectPoint = () => {
        $eventIndexStore = -1;
    };
</script>

<button
    type="button"
    class="btn btn-secondary btn-sm"
    disabled={$eventIndexStore === -1}
    id="unselect-btn"
    on:click={unselectPoint}
>
    Unselect Point
</button>

<style>
    #unselect-btn {
        margin-right: 10px;
    }

    /* #unselect-btn.visible {
        visibility: visible;
    } */
</style>
