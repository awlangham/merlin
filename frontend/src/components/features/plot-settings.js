export const mdsConfig = {
    showTips: false,
    modeBarButtonsToRemove: ["zoom2d", "pan2d", "select2d", "lasso2d"],
    displaylogo: false,
    scrollZoom: true,
    responsive: true,
};

export const makeSelectionShape = (x, y) => {
    const selectedRadius = 16;

    return [
        {
            type: "circle",
            xsizemode: "pixel",
            ysizemode: "pixel",
            fillcolor: "#1f77b4",
            xanchor: x,
            yanchor: y,

            x0: -selectedRadius / 2,
            x1: selectedRadius / 2,
            y0: -selectedRadius / 2,
            y1: selectedRadius / 2,

            line: { color: "black", width: 4 },
        },
        {
            // Workaround for what I think is a bug in PlotlyJS:
            // The previous shape uses "pixel" as the x and y sizemodes,
            // which causes the lasso select to use the wrong coordinates.
            // This sets the last shape to use "scaled" sizemodes which seems to fix it.
            type: "path",
            path: "",
            xsizemode: "scaled",
            ysizemode: "scaled",
        },
    ]
}