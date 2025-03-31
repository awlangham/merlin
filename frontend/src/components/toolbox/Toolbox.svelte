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

    Tool:
    <select
        id="select-tool"
        class="form-select form-select-sm"
        bind:value={$modeStore}
    >
        <option value="explore">Explore 🔦</option>
        <option value="crossbrush">CrossBrush 🖌️</option>
        <option value="mds">MDS 🔍</option>
    </select>

    <span id="span-right">
        <UnselectButton />
        <LabelData />
        <button
            id="button-clear"
            disabled={$brushedStore.length === 0}
            on:click={() => {
                dispatch("clear");
            }}
            type="button"
            class="btn btn-secondary btn-sm"
        >
            Clear Brush Selection
        </button>
        <DownloadData />
    </span>
</div>

<style>
    #select-tool {
        margin-left: 10px;
    }

    #tool-div {
        border: 2px solid gray;
        border-radius: 10px;
        box-shadow: 3px 3px 4px #888;
        padding: 10px;
        background-color: white;
        display: flex;
        align-items: center;
    }

    .form-select {
        display: inline;
        width: auto;
    }

    #span-right {
        margin-left: auto;
        display: flex;
    }

    #button-clear {
        margin-right: 10px;
    }
</style>
