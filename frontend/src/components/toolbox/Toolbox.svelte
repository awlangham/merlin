<script>
    import { createEventDispatcher } from "svelte";
    import { modeStore, brushedStore } from "../stores";

    import DownloadData from "./DownloadData.svelte";
    import LabelData from "./LabelData.svelte";
    import UnselectButton from "./UnselectButton.svelte";
    import FilterDropdown from "./FilterDropdown.svelte";

    const dispatch = createEventDispatcher();
</script>

<div id="tool-div" class="h-100">
    <FilterDropdown />

    <div>
        Tool:
        <select class="form-select form-select-sm" bind:value={$modeStore}>
            <option value="explore">Explore 🔦</option>
            <option value="crossbrush">CrossBrush 🖌️</option>
            <option value="mds">MDS 🔍</option>
        </select>

        <UnselectButton />
    </div>

    {#if $brushedStore}
        <LabelData />
        <div>
            <button
                on:click={() => {
                    dispatch("clear");
                }}
                type="button"
                class="btn btn-secondary btn-sm"
            >
                Clear Brush Selection
            </button>
            <DownloadData />
        </div>
    {/if}
</div>

<style>
    #tool-div {
        border: 2px solid gray;
        border-radius: 10px;
        box-shadow: 3px 3px 4px #888;
        padding: 10px;
        margin-bottom: 10px;
        background-color: white;
    }

    .form-select {
        display: inline;
        width: auto;
    }
</style>
