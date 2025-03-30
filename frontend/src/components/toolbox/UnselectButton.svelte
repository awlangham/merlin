<script>
    import { eventIndexStore } from "../stores";

    const unselectPoint = () => {
        $eventIndexStore = -1;
    };
</script>

<button
    type="button"
    class="btn btn-secondary btn-sm"
    class:visible={$eventIndexStore != -1}
    id="unselect-btn"
    on:click={unselectPoint}
>
    Unselect Point ⭕️
</button>

<style>
    #unselect-btn {
        visibility: hidden;
        margin-left: auto;
    }

    #unselect-btn.visible {
        visibility: visible;
    }
</style>
