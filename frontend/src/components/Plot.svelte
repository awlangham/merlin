<script>
    import Plotly from "plotly.js-dist-min";
    import { onMount, createEventDispatcher } from "svelte";

    export let data, layout, config;

    let plotDiv;

    const dispatch = createEventDispatcher();
    const onClick = (d) => dispatch("click", d);
    const onSelected = (d) => dispatch("selected", d);

    onMount(() => {
        Plotly.newPlot(plotDiv, []);
        plotDiv.on("plotly_click", onClick);
        // TO DO: allow the user to choose click or hover
        // plotDiv.on("plotly_hover", onClick);
        plotDiv.on("plotly_selected", onSelected);
    });

    $: if (plotDiv) {
        Plotly.react(plotDiv, data, {}, config);
        Plotly.relayout(plotDiv, layout);
    }
</script>

<div class="plot-div" bind:this={plotDiv}></div>

<style>
    .plot-div {
        width: 100%;
        height: 100%;
    }
</style>
