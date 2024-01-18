from .base import BaseD3Plot
import pandas as pd
import numpy as np
import os
from jinja2 import Environment, FileSystemLoader


class SortedStreamD3Plot(BaseD3Plot):
    def __init__(
        self,
        data,
        x_col="x",
        y_col="y",
        label_col="label",
        pad=0,
        centered=False,
        time_series=True,
        ascending=False,
    ):
        super().__init__(data)
        self.x = x_col
        self.y = y_col
        self.label = label_col
        self.pad = pad
        self.centered = centered
        self.time_series = time_series
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
        if self.time_series:  # TODO – check this section
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

        else:  # TODO – check this section
            # Sort data by label and x (for calculating area under curve)
            self.data.sort_values(
                by=["label", "x"],
                inplace=True,
                ascending=True,
                ignore_index=True,
            )

            # Define a function to calculate the area under the curve using np.trapz
            def calculate_area_under_curve(x_values, y_values):
                return np.trapz(y_values, x_values)

            # Group by label and calculate area under the curve for each group
            self.data["area_under_curve"] = self.data.groupby(by="label").apply(
                lambda group: calculate_area_under_curve(group["x"], group["y"])
            )

            # Sort data (to add final order) and drop unnecessary column
            self.data.sort_values(
                by=["x", "area_under_curve"],
                ascending=[True, self.ascending],
                inplace=True,
                ignore_index=True,
            )
            self.data.drop(columns=["area_under_curve"], inplace=True)

        # Add order column
        self.data["order"] = self.data.groupby(by=["x"]).cumcount()

    def get_template_kind(self):
        return "sortedstream"

    def render_template(self, json_filename, kind):
        env = Environment(loader=FileSystemLoader(os.path.join("templates")))
        template = env.get_template(f"{kind}_template.html")
        return template.render(json_path=json_filename)
