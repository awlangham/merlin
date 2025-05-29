export const unclusteredColor = "#000000";

export const selectedColor = "orange";

export const colors = [
    "#5778a4",
    "#e49444",
    "#d1615d",
    "#85b6b2",
    "#6a9f58",
    "#e7ca60",
    "#a87c9f",
    "#f1a2a9",
    "#967662",
    "#b8b0ac",
];

export const powerFeatures = [
    "Total Steady-State P",
    "Total Steady-State Q",
    "A Steady-State P",
    "A Steady-State Q",
    "B Steady-State P",
    "B Steady-State Q",
    "C Steady-State P",
    "C Steady-State Q",
    "Total Peak P",
    "Total Peak Q",
];

export const labels = {
    "Total Steady-State P": "Total Steady-State Active Power (W)",
    "Total Steady-State Q": "Total Steady-State Reactive Power (Var)",
    "A Steady-State P": "A Steady-State Active Power (W)",
    "A Steady-State Q": "A Steady-State Reactive Power (Var)",
    "B Steady-State P": "B Steady-State Active Power (W)",
    "B Steady-State Q": "B Steady-State Reactive Power (Var)",
    "C Steady-State P": "C Steady-State Active Power (W)",
    "C Steady-State Q": "C Steady-State Reactive Power (Var)",
    "Total Peak P": "Total Peak Active Power (W)",
    "Total Peak Q": "Total Peak Reactive Power (Var)",
};

const baselineLength = 5;

export const getStartBaseline = (dataArray) => {
    if (dataArray.length <= baselineLength) {
        return 0;
    }

    return dataArray.slice(0, baselineLength).reduce((a, b) => a + b) / baselineLength;
};

export const getEndBaseline = (dataArray) => {
    if (dataArray.length <= baselineLength) {
        return 0;
    }

    return dataArray.slice(-baselineLength).reduce((a, b) => a + b) / baselineLength;
};