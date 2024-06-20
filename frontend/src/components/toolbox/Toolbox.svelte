<script>
    import { createEventDispatcher } from "svelte";
    import { modeStore, brushedStore } from "../stores";

    import DownloadData from "./DownloadData.svelte";
    import LabelData from "./LabelData.svelte";
    import UnselectButton from "./UnselectButton.svelte";
    import FilterDropdown from "./FilterDropdown.svelte";

    const dispatch = createEventDispatcher();
</script>

<div id="tool-div">
    <FilterDropdown />

    <div>
        Tool:
        <select bind:value={$modeStore}>
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
            >
                Clear Brush Selection
            </button>
            <DownloadData />
        </div>
    {/if}
</div>

<style>
    #tool-div {
        height: 110px;
        border: 2px solid gray;
        border-radius: 10px;
        box-shadow: 3px 3px 4px #888;
        margin-bottom: 10px;
        padding-top: 10px;
        padding-bottom: 10px;
        padding-left: 5px;
        padding-right: 5px;
        background-color: white;
    }

    #tool-div div {
        padding-bottom: 5px;
    }
</style>
