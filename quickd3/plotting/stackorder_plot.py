from .base_plot import BaseD3Plot
import pandas as pd
import numpy as np
import os
from jinja2 import Environment, FileSystemLoader


class StackOrderD3Plot(BaseD3Plot):
    def __init__(
        self,
        data,
        x_col="x",
        y_col="y",
        label_col="label",
        pad=0,
        centered=False,
        time_series=True,
        ascending=True,
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
        self.data.renamme(
            columns={self.x: "x", self.y: "y", self.label: "label"}, inplace=True
        )

        # Create dataframe of all (label, x) combinations
        x_vals = self.data[self.x].unique()
        combo_df = pd.DataFrame(
            [(label, x) for label in self.data[self.label].unique() for x in x_vals],
            columns=[self.label, self.x],
        )

        # Add all combinations of label and x to data
        self.data = combo_df.merge(self.data, how="left", on=[self.label, self.x])
        self.data[self.y] = self.data[self.y].fillna(0)

        # Add "order" column to data, indicating the vertical order in which to plot
        self.add_order()  # TODO implement

        # Add lb and ub columns
        self.data["ub"] = (
            self.data.groupby(by=self.x).cumsum() + self.pad * self.data["order"]
        )
        self.data["lb"] = (
            self.data["ub"].shift(periods=1, fill_value=-self.pad) + self.pad
        )

        # Vertically center, if required
        if self.centered:
            # Compute center of all y-values for each x-value
            self.data["y_center"] = self.data.groupby(by=self.x).transform(
                lambda group: group["ub"].max() - group["lb"].min()
            )

            # Shift ub and lb to center
            self.data["ub"] = self.data["ub"] - self.data["y_center"]
            self.data["lb"] = self.data["lb"] - self.data["y_center"]

            # Drop unnecessary column
            self.data.drop(columns=["y_center"], inplace=True)

        formatted_data = self.data.to_json(orient="records")

        return formatted_data

    def add_order(self):
        if self.time_series:
            # Sort data by x and y (to add final order)
            self.data.sort_values(
                by=[self.x, self.y],
                ascending=[True, self.ascending],
                inplace=True,
                ignore_index=True,
            )

            # Add order column
            self.data["order"] = self.data.groupby(by=[self.x]).cumcount()

        else:
            # Sort data by label and x (for calculating area under curve)
            self.data.sort_values(
                by=[self.label, self.x],
                inplace=True,
                ascending=True,
                ignore_index=True,
            )

            # Define a function to calculate the area under the curve using np.trapz
            def calculate_area_under_curve(x_values, y_values):
                return np.trapz(y_values, x_values)

            # Group by label and calculate area under the curve for each group
            self.data["area_under_curve"] = self.data.groupby(by=self.label).apply(
                lambda group: calculate_area_under_curve(group["x"], group["y"])
            )

            # Sort data (to add final order)
            self.data.sort_values(
                by=[self.x, "area_under_curve"],
                ascending=[True, self.ascending],
                inplace=True,
                ignore_index=True,
            )

            # Add order column and drop unnecessary column
            self.data["order"] = self.data.groupby(by=[self.x]).cumcount()
            self.data.drop(columns=["area_under_curve"], inplace=True)

    def get_template_kind(self):
        return "stackorder"

    def render_template(self, json_path, kind):
        env = Environment(loader=FileSystemLoader(os.path.join("quickd3", "templates")))
        template = env.get_template(f"{kind}_template.html")
        return template.render(json_path=json_path)
