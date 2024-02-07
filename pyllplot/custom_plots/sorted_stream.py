from scipy.interpolate import PchipInterpolator
import plotly.graph_objects as go
import colorlover as cl
import pandas as pd
import numpy as np
import math


class SortedStream:
    def __init__(
        self,
        data=None,
        pad=0,
        centered=True,
        color_dict=None,
        smooth=True,
        interp_res=None,
    ):
        if data is not None:
            if isinstance(data, dict):
                self.data = pd.DataFrame(data)
            elif isinstance(data, pd.DataFrame):
                self.data = data
            else:
                raise ValueError(
                    "Invalid data format. Provide data as a dictionary "
                    "or as a Pandas DataFrame."
                )
        else:
            raise ValueError(
                "Missing required data. Provide a dictionary or a Pandas DataFrame."
            )

        if pad < 0:
            raise ValueError("Padding must be greater or equal to zero.")

        if smooth:
            if interp_res is not None:
                if len(self.data["x"].unique()) > math.ceil(interp_res):
                    raise ValueError(
                        "Interpolation resolution must be None or a numeric that is "
                        "greater or equal to the number distinct x-values."
                    )
                else:
                    interp_res = math.ceil(interp_res)
            else:
                min_res = 1000
                interp_res = max(len(self.data["x"].unique()) * 1.2, min_res)

        self.smooth = smooth
        self.interp_res = interp_res
        self.pad = pad
        self.centered = centered
        self.fig = go.Figure()

        # Check if color_dict is provided and contains all labels
        if color_dict and set(data["label"].unique()) != set(color_dict.keys()):
            raise ValueError(
                "color_dict must contain colors for all unique labels in the data."
            )

        # If color_dict is not provided, use a colorblind-friendly palette
        if not color_dict:
            self.color_dict = self._generate_color_dict()

        # Preprocess data and create plot object upon instantiation
        self._preprocess_data()
        self._create_plot()

    def _generate_color_dict(self):
        unique_labels = self.data["label"].unique()

        # Generate a color-blind friendly color scale with the required number of colors
        color_palette = cl.scales["10"]["qual"]["Paired"][: len(unique_labels)]

        # Create a dictionary with labels as keys and colors as values
        return dict(zip(unique_labels, color_palette))

    def _preprocess_data(self):
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

        # Remove cases where height is zero (only used to add order via cumcount)
        self.data = self.data.query("height > 0")

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

    @staticmethod
    def _convert_series_to_numbers(series):
        if pd.api.types.is_numeric_dtype(series.dtype):
            # If series is numeric (integers or floats), return list itself
            return series.tolist()
        elif pd.api.types.is_datetime64_any_dtype(series):
            # If series is of datetime objects, calculate timedelta from  first element
            timedelta_values = (series - series.iloc[0]).dt.total_seconds()
            return timedelta_values.tolist()
        elif (
            isinstance(series.dtype, pd.CategoricalDtype)
            or pd.api.types.is_string_dtype(series)
            or pd.api.types.is_bool_dtype(series)
        ):
            # If series is of categorical, string, or boolean objects,
            # map to simple sequential list
            return list(range(len(series)))
        else:
            # For other types, return a list with incremental numbers
            return ValueError("x must be numeric, datetime, categorical, or boolean.")

    def _add_order(self):
        self.data.sort_values(
            by=["x", "height"],
            ascending=[True, True],
            inplace=True,
            ignore_index=True,
        )

        # Re-sort labels when there are duplicates in height for a given x
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
                dup_labels = dup_df["label"].to_list()
                last_labels = last_group.loc[
                    last_group["label"].isin(dup_labels), "label"
                ].to_list()

                # Get the indices that would sort dup_labels and last_labels
                indices_sort_d = np.argsort(dup_labels)
                indices_sort_l = np.argsort(last_labels)

                # Sort indices of dup_df
                sorted_indices = indices_sort_d[indices_sort_l]
                dup_df_sorted = dup_df.iloc[sorted_indices]
                dup_df_sorted.index = dup_df.index
                group_df.loc[dup_df.index] = dup_df_sorted

            sorted_gps.append(group_df)
            last_group = group_df

        # Concatenate sorted dataframes
        self.data = pd.concat(sorted_gps)

        # Add order column
        self.data["order"] = self.data.groupby(by=["x"]).cumcount()

    def _generate_area(self, label, x_map, color):
        label_data = self.data[self.data["label"] == label]
        x_num = label_data["x"].apply(lambda x: x_map[x])

        # Skip if there's only one valid row (can't create an area)
        if len(label_data) <= 1:
            return

        upper_bound = label_data["ub"].to_list()
        lower_bound = label_data["lb"].to_list()

        if self.smooth:
            # Interpolate using PchipInterpolator
            interp_x = np.linspace(min(x_num), max(x_num), num=self.interp_res)
            interp_upper = PchipInterpolator(x_num, upper_bound)(interp_x)
            interp_lower = PchipInterpolator(x_num, lower_bound)(interp_x)

        else:
            interp_x = x_num
            interp_upper = upper_bound
            interp_lower = lower_bound

        # Add a single trace for upper and lower bounds with filled area
        self.fig.add_trace(
            go.Scatter(
                x=np.concatenate([interp_x, interp_x[::-1]]),
                y=np.concatenate([interp_upper, interp_lower[::-1]]),
                fill="toself",
                fillcolor=color,
                line=dict(color=color),
                name=f"{label}",
            )
        )

    def _create_plot(self):
        # Get x-axis labels and numeric values
        unique_labels = self.data["label"].unique()
        unique_x = pd.Series(self.data["x"].unique())
        unique_x_num = self._convert_series_to_numbers(unique_x)

        x_map = {unique_x[idx]: unique_x_num[idx] for idx in range(len(unique_x))}

        # Generate area plots for each unique label with the color palette
        for _, label in enumerate(unique_labels):
            color = self.color_dict[label]  # Use a color from the palette
            self._generate_area(label, x_map, color)

        # Customize layout if needed
        self.fig.update_layout(yaxis=dict(showticklabels=False), showlegend=True)

        # If unique_x is datetime, format it as string for adding labels to plot
        if pd.api.types.is_datetime64_any_dtype(unique_x):
            # Format
            mask = (
                (unique_x.dt.hour == 0)
                & (unique_x.dt.minute == 0)
                & (unique_x.dt.second == 0)
            )

            # Format the datetime objects
            unique_x = np.where(
                mask,
                unique_x.dt.strftime("%Y-%m-%d"),
                unique_x.dt.strftime("%Y-%m-%d") + unique_x.dt.strftime(" %H:%M:%S"),
            )

        # Set x-axis labels to original x values (after formatting datetime to string)
        self.fig.update_layout(
            xaxis=dict(
                tickvals=unique_x_num,
                ticktext=[val for val in unique_x],
                showgrid=True,  # Show the grid lines
            ),
            yaxis=dict(showgrid=True),
        )

    # def show(self):
    #     self._generate_area()
    #     self.fig.show()
