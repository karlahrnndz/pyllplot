from pyllplot import SortedStream
import plotly.io as pio
import pandas as pd

# Example where the values in x are datetime objects
data_dict = {
    "x": [
        "2022-01-01",
        "2022-01-02",
        "2022-01-03",
        "2022-01-01",
        "2022-01-02",
        "2022-01-03",
    ],
    "height": [1, 1, 1, 3, 2, 3],
    "label": ["lab_1", "lab_1", "lab_1", "lab_2", "lab_2", "lab_2"],
}
data_dict["x"] = pd.to_datetime(data_dict["x"])

custom_plot = SortedStream(
    data=data_dict, pad=0, centered=True, color_dict=None, smooth=True, interp_res=1000
)

# custom_plot.fig is a plotly.graph_objects object containing the final visualization
# you can work with it like you would a normal plotly.graph_objects object:
custom_plot.fig.show()
pio.write_image(custom_plot.fig, file="sorted_stream.svg")
