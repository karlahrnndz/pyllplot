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
        y_col="y",
        label_col="label",
        pad=0,
        centered=False,
        ascending=False,
    ):
        super().__init__(data)
        self.x = x_col
        self.y = y_col
        self.label = label_col
        self.pad = pad
        self.centered = centered
        self.ascending = ascending

    def format_data(self):
        if not isinstance(self.data, pd.DataFrame):
            raise ValueError("`data` must be a pandas dataframe.")

        # Rename columns
        self.data.rename(
            columns={self.x: "x", self.y: "y", self.label: "label"}, inplace=True
        )

        # Create dataframe of all (label, x) combinations
        x_vals = self.data["x"].unique()
        combo_df = pd.DataFrame(
            [(label, x) for label in self.data["label"].unique() for x in x_vals],
            columns=["label", "x"],
        )

        # Add all combinations of label and x to data
        self.data = combo_df.merge(self.data, how="left", on=["label", "x"])
        self.data["y"] = self.data["y"].fillna(0)

        # Add "order" column to data, indicating the vertical order in which to plot
        self.add_order()

        # Add lb and lb columns
        self.data["ub"] = (
            self.data.groupby(by="x")["y"].cumsum() + self.pad * self.data["order"]
        )
        self.data["lb"] = (
            self.data.groupby(by="x")["ub"].shift(periods=1, fill_value=-self.pad)
            + self.pad
        )

        # Vertically center, if required
        if self.centered:  # TODO – check
            # Compute center of all y-values for each x-value
            self.data["y_center"] = self.data.groupby(by="x").transform(
                lambda group: group["ub"].max() - group["lb"].min()
            )

            # Shift ub and lb to center
            self.data["ub"] = self.data["ub"] - self.data["y_center"]
            self.data["lb"] = self.data["lb"] - self.data["y_center"]

            # Drop unnecessary column
            self.data.drop(columns=["y_center"], inplace=True)

    def add_order(self):
        self.data.sort_values(
            by=["x", "y"],
            ascending=[True, self.ascending],
            inplace=True,
            ignore_index=True,
        )

        last_group = None
        sorted_gps = []
        for _, group_df in self.data.groupby(by="x"):
            duplicates = group_df.duplicated(subset="y", keep=False)
            if duplicates.any() and last_group is not None:
                dup_df = group_df[duplicates].copy()
                dup_labels = dup_df["label"].unique()
                sorted_indices = np.argsort(
                    last_group.loc[last_group["label"].isin(dup_labels), "label"]
                )
                dup_df_sorted = dup_df.iloc[sorted_indices].reset_index(drop=True)
                dup_df_sorted.index = dup_df.index
                group_df.loc[dup_df.index] = dup_df_sorted

            sorted_gps.append(group_df)
            last_group = group_df

        # Concatenate sorted dataframes
        self.data = pd.concat(sorted_gps)

        # Add order column
        self.data["order"] = self.data.groupby(by=["x"]).cumcount()

    def make_plot(self, filepath=None, color_palette=None):

        # Determine the number of distinct labels
        num_labels = len(self.data['label'].unique())

        # Use the specified color palette or the default color-blind-safe palette
        if color_palette is None:
            color_palette = sns.color_palette("colorblind", n_colors=num_labels)

        # Create a ListedColormap
        custom_cmap = ListedColormap(color_palette)

        # Separate data for each label
        labels = self.data['label'].unique()

        # Plotting
        fig, ax = plt.subplots()

        for i, label in enumerate(labels):
            subset = self.data[self.data['label'] == label]

            if len(subset['x'].unique()) >= 2:
                # Use PchipInterpolator for smooth, monotonic fit
                f_ub = PchipInterpolator(subset['x'], subset['ub'])
                f_lb = PchipInterpolator(subset['x'], subset['lb'])

                x_smooth = np.linspace(subset['x'].min(), subset['x'].max(), 100)
                ub_smooth = f_ub(x_smooth)
                lb_smooth = f_lb(x_smooth)

                # Plot filled area with custom color
                ax.fill_between(x_smooth, lb_smooth, ub_smooth, label=f'{label}', color=custom_cmap(i))

        # Customize the plot
        ax.set_xlabel(self.x)
        ax.set_ylabel(self.y)
        ax.legend()

        # Create filepath if not provided
        if filepath is None:
            filepath = os.path.join(os.getcwd(), 'sorted_stream.svg')

        # Save the plot as an SVG file
        plt.savefig(filepath, format='svg')

        # Show the plot
        plt.show()
