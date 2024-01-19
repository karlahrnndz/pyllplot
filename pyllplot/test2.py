import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import PchipInterpolator
import numpy as np

# Your DataFrame
data = pd.DataFrame(
    {
        "label": ["a", "a", "a", "a", "b", "b", "b", "b"],
        "x": pd.to_datetime(
            [
                "2022-01-01 12:00:00",
                "2022-01-01 14:30:00",
                "2022-01-03 16:45:00",
                "2022-01-04 18:20:00",
                "2022-01-01 12:00:00",
                "2022-01-01 14:30:00",
                "2022-01-03 16:45:00",
                "2022-01-04 18:20:00",
            ]
        ),
        "y": [3, 3, 3, 3, 2, 2, 2, 2],
        "order": [1, 1, 1, 1, 2, 2, 2, 2],
        "ub": [3.00, 3, 3.00, 3, 5, 5, 5, 5],
        "lb": [0.00, 0, 0.00, 0, 3, 3, 3, 3],
    }
)

# Separate data for each label
labels = data["label"].unique()

# Plotting
fig, ax = plt.subplots()


x_labels = None
x_numeric_indices = None

for label in labels:
    subset = data[data["label"] == label]

    if x_labels is None:
        x_labels = subset["x"]

    if x_numeric_indices is None:
        # Create a mapping between unique values in 'x' and their indices
        x_mapping = {value: idx for idx, value in enumerate(subset["x"].unique())}

        # Map 'x' to numeric indices
        x_numeric_indices = subset["x"].map(x_mapping)

    if len(subset["x"].unique()) >= 2:
        # Use PchipInterpolator for smooth, monotonic fit on numeric indices
        f_ub = PchipInterpolator(x_numeric_indices, subset["ub"])
        f_lb = PchipInterpolator(x_numeric_indices, subset["lb"])

        # Generate a range of numeric values for x indices
        x_smooth_numeric_indices = np.linspace(
            x_numeric_indices.min(), x_numeric_indices.max(), 100
        )

        # Use interpolation functions to obtain y values for the numeric index range
        ub_smooth = f_ub(x_smooth_numeric_indices)
        lb_smooth = f_lb(x_smooth_numeric_indices)

        # Plot filled area with custom color
        ax.fill_between(
            x_smooth_numeric_indices, lb_smooth, ub_smooth, label=f"{label} Area"
        )


# Set x-axis ticks to the original values of 'x' corresponding to x_numeric_indices
ax.set_xticks(x_numeric_indices)
ax.set_xticklabels(x_labels)

# Customize the plot
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Monotonic Area Plot with Timestamps (Original Dates as Tick Labels)")
ax.legend()
plt.show()
