<script>
    import { eventStore } from "./stores";

    import Logo from "./Logo.svelte";
    import TopBar from "./topbar/TopBar.svelte";
    import Toolbox from "./toolbox/Toolbox.svelte";
    import Transients from "./transients/Transients.svelte";
    import Features from "./features/Features.svelte";
    import TransientPlot from "./transients/TransientPlot.svelte";

    import "bootstrap/dist/css/bootstrap.min.css";
    // import 'bootstrap/dist/js/bootstrap.min.js';

    let featurePlots;

    $: if ($eventStore && featurePlots) {
        featurePlots.clearBrushedSelection();
    }
</script>

<div class="main container vh-100">
    <div class="row pb-2" id="top-row">
        <div class="col-3">
            <Logo />
        </div>
        <div class="col-9">
            <TopBar />
        </div>
    </div>
    <div class="row" id="bottom-row">
        <div class="col-4">
            <div class="row h-100">
                <div class="col">
                    <div class="row h-50 pb-2">
                        <div class="col">
                            <TransientPlot />
                        </div>
                    </div>
                    <div class="row h-50">
                        <div class="col">
                            <Transients></Transients>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <Features bind:this={featurePlots} />
    </div>
    <div class="row pt-2">
        <div class="col-12">
            <Toolbox on:clear={featurePlots.clearBrushedSelection} />
        </div>
    </div>
</div>

<style>
    .main {
        display: flex;
        flex-direction: column;
        max-width: 100%;
        padding-top: 10px;
        padding-bottom: 10px;
        background-color: #f2f2f2;
    }

    #bottom-row {
        flex: 1 1 100%;
    }

    .row {
        --bs-gutter-x: 0.7rem;
    }
</style>
