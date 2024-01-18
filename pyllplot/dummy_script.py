from pyllplot import SortedStream
import pandas as pd
import os

FILEPATH = os.path.join("..", "output", "text.svg")


data = pd.DataFrame(
    {
        "my_x": [1, 2, 3, 4, 1, 2, 3, 4],
        "my_y": [3, 3, 1, 3, 2, 2, 2, 2],
        "my_label": ["a", "a", "a", "a", "b", "b", "b", "b"],
    }
)

stackorder_plot = SortedStream(
    data,
    x_col="my_x",
    y_col="my_y",
    label_col="my_label",
    pad=0,
    centered=False,
    ascending=False,
)
stackorder_plot.plot()
