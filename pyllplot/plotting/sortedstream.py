from scipy.interpolate import PchipInterpolator
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
from .base import BasePlot
import seaborn as sns
import pandas as pd
import numpy as np
import os


class SortedStream(BasePlot):
    def __init__(
        self,
        data,
        x_col="x",
        height_col="height",
        label_col="label",
        pad=0,
        centered=False,
        ascending=False,
    ):
        super().__init__(data)
        self.x = x_col
        self.height = height_col
        self.label = label_col
        self.pad = pad
        self.centered = centered
        self.ascending = ascending

    def _format_data(self):
        if not isinstance(self.data, pd.DataFrame):
            raise ValueError("`data` must be a pandas dataframe.")

        if self.data[self.height].min() < 0:
            raise ValueError("All height values must be non-negative.")

        # Rename columns
        self.data.rename(
            columns={self.x: "x", self.height: "height", self.label: "label"},
            inplace=True,
        )

        # Create dataframe of all (label, x) combinations
        x_vals = self.data["x"].unique()
        combo_df = pd.DataFrame(
            [(label, x) for label in self.data["label"].unique() for x in x_vals],
            columns=["label", "x"],
        )

        # Add all combinations of label and x to data
        self.data = combo_df.merge(self.data, how="left", on=["label", "x"])
        self.data["height"] = self.data["height"].fillna(0)

        # Add "order" column to data, indicating the vertical order in which to plot
        self._add_order()

        # Add lb and lb columns
        self.data["ub"] = (
            self.data.groupby(by="x")["height"].cumsum() + self.pad * self.data["order"]
        )
        self.data["lb"] = (
            self.data.groupby(by="x")["ub"].shift(periods=1, fill_value=-self.pad)
            + self.pad
        )

        # Vertically center, if required
        if self.centered:
            # Compute center of all height-values for each x-value
            ub_max_srs = self.data.groupby("x")["ub"].transform("max")
            lb_min_srs = self.data.groupby("x")["lb"].transform("min")
            y_center_srs = (ub_max_srs - lb_min_srs) / 2

            # Shift ub and lb to center
            self.data["ub"] = self.data["ub"] - y_center_srs
            self.data["lb"] = self.data["lb"] - y_center_srs

    def _add_order(self):
        self.data.sort_values(
            by=["x", "height"],
            ascending=[True, self.ascending],
            inplace=True,
            ignore_index=True,
        )

        # Resort labels when there are duplicates in height for a given x
        # to prevent switching label order when ties occur
        # (note that x-values won't be sorted).
        last_group = None
        sorted_gps = []
        for _, group_df in self.data.groupby(by="x"):
            duplicates = group_df.duplicated(subset="height", keep=False)

            # If y duplicates and not 1st group, sort labels by previous group
            if duplicates.any() and last_group is not None:
                # Extract rows with duplicates
                dup_df = group_df[duplicates].copy()

                # Get labels from duplicates and relevant labels from last group
                dup_labels = dup_df["label"].values
                last_labels = last_group.loc[
                    last_group["label"].isin(dup_labels), "label"
                ].values

                # Get the indices that would sort dup_labels and last_labels
                indices_sort_d = np.argsort(dup_labels)
                indices_sort_l = np.argsort(last_labels)

                # Sort indices of dup_df
                sorted_indices = indices_sort_d[indices_sort_l]
                dup_df_sorted = dup_df.iloc[sorted_indices].reset_index(drop=True)
                dup_df_sorted.index = dup_df.index
                group_df.loc[dup_df.index] = dup_df_sorted

            sorted_gps.append(group_df)
            last_group = group_df

        # Concatenate sorted dataframes
        self.data = pd.concat(sorted_gps)

        # Add order column
        self.data["order"] = self.data.groupby(by=["x"]).cumcount()

    def _make_plot(self, filepath=None, color_palette=None, title=None, figsize=None):
        # Determine number of labels and their unique values
        labels = self.data["label"].unique()
        num_labels = len(labels)

        # Use the specified color palette or the default color-blind-safe palette
        if color_palette is None:
            color_palette = sns.color_palette("colorblind", n_colors=num_labels)

        # Create a ListedColormap
        custom_cmap = ListedColormap(color_palette)

        # Plotting (one area plot per distinct label)
        fig, ax = plt.subplots(figsize=figsize)
        x_numeric_indices = None  # Placeholder
        x_labels = None  # Placeholder
        x_smooth_numeric_indices = None

        for i, label in enumerate(labels):
            subset = self.data[self.data["label"] == label]

            # Plot area if there are at least two distinct x values
            if len(subset["x"].unique()) >= 2:
                # Map 'x' to numbers using enumerate
                # (can create once since data is sorted and results won't change)
                if x_numeric_indices is None or x_smooth_numeric_indices is None:
                    x_mapping = {
                        value: idx for idx, value in enumerate(subset["x"].unique())
                    }
                    x_numeric_indices = subset["x"].map(x_mapping)

                    # Generate a range of numeric values for x indices
                    x_smooth_numeric_indices = np.linspace(
                        x_numeric_indices.min(), x_numeric_indices.max(), 100
                    )

                # Use PchipInterpolator for smooth, monotonic fit to original x values
                f_ub = PchipInterpolator(x_numeric_indices, subset["ub"])
                f_lb = PchipInterpolator(x_numeric_indices, subset["lb"])

                # Apply interpolator to additional values of x
                ub_smooth = f_ub(x_smooth_numeric_indices)
                lb_smooth = f_lb(x_smooth_numeric_indices)

                # Plot filled area with custom color
                ax.fill_between(
                    x_smooth_numeric_indices,
                    lb_smooth,
                    ub_smooth,
                    label=f"{label}",
                    color=custom_cmap(i),
                )

                # (Can create once since data is sorted and results won't change.)
                if x_labels is None:
                    x_labels = subset["x"]

        # Set x-axis ticks to the original values of 'x'
        ax.set_xticks(x_numeric_indices)
        ax.set_xticklabels(x_labels)

        # Customize the plot
        ax.set_xlabel(self.x)
        ax.set_ylabel(self.height)

        if title is not None:
            ax.set_title(title)

        ax.legend()

        # Adjust subplot parameters for a tight layout
        plt.tight_layout()

        # Create filepath if not provided
        if filepath is None:
            filepath = os.path.join(os.getcwd(), "sorted_stream.svg")

        # Save the plot as an SVG file
        plt.savefig(filepath, format="svg")

        # Show the plot
        plt.show()
