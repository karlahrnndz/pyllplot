from .base_template import BaseTemplate
import pandas as pd
import numpy as np


class StackOrder(BaseTemplate):
    def __init__(
        self,
        template_name,
        data,
        x_col="x",
        y_col="y",
        label_col="label",
        time_series=True,
        pad=0,
        ascending=False,
        centered=False,
    ):
        super().__init__(template_name)
        self.x_col = x_col
        self.y_col = y_col
        self.label_col = label_col
        self.time_series = time_series
        self.pad = pad
        self.ascending = ascending
        self.centered = centered
        self.json_data = self.format_data(data)

    def format_data(self, data):
        if not isinstance(data, pd.DataFrame):
            raise ValueError("`data` must be a pandas dataframe.")

        # Create dataframe of all (label, x) combinations
        x_vals = data[self.x_col].unique()
        combo_df = pd.DataFrame(
            [(label, x) for label in data[self.label_col].unique() for x in x_vals],
            columns=[self.label_col, self.x_col],
        )

        # Add all combinations of label and x to data
        data = combo_df.merge(data, how="left", on=[self.label_col, self.x_col])
        data[self.y_col] = data[self.y_col].fillna(0)

        # Add "order" column to data, indicating the vertical order in which to plot
        data = self.add_order(data)

        # Add lb and ub columns
        data["ub"] = data.groupby(by=self.x_col).cumsum() + self.pad * data["order"]
        data["lb"] = data["ub"].shift(periods=1, fill_value=-self.pad) + self.pad

        # Vertically center, if required
        if self.centered:
            # Compute center of all y-values for each x-value
            data["y_center"] = data.groupby(by=self.x_col).transform(
                lambda x: x["ub"].max() - x["lb"].min()
            )

            # Shift ub and lb to center
            data["ub"] = data["ub"] - data["y_center"]
            data["lb"] = data["lb"] - data["y_center"]

            # Drop unnecessary column
            data.drop(columns=["y_center"], inplace=True)

        json_string = data.to_json(orient="records")

        return json_string

    def add_order(self, data):
        if self.time_series:
            # Sort data by x and y (to add final order)
            data.sort_values(
                by=[self.x_col, self.y_col],
                ascending=[True, self.ascending],
                inplace=True,
                ignore_index=True,
            )

            # Add order column
            data["order"] = data.groupby(by=[self.x_col]).cumcount()

        else:
            # Sort data by label and x (for calculating area under curve)
            data.sort_values(
                by=[self.label_col, self.x_col],
                inplace=True,
                ascending=True,
                ignore_index=True,
            )

            # Define a function to calculate the area under the curve using np.trapz
            def calculate_area_under_curve(x_values, y_values):
                return np.trapz(y_values, x_values)

            # Group by label and calculate area under the curve for each group
            data["area_under_curve"] = data.groupby(by=self.label_col).apply(
                lambda group: calculate_area_under_curve(group["x"], group["y"])
            )

            # Sort data (to add final order)
            data.sort_values(
                by=[self.x_col, "area_under_curve"],
                ascending=[True, self.ascending],
                inplace=True,
                ignore_index=True,
            )

            # Add order column and drop unnecessary column
            data["order"] = data.groupby(by=[self.x_col]).cumcount()
            data.drop(columns=["area_under_curve"], inplace=True)

        return data
