from quickd3 import SortedStreamD3Plot
import pandas as pd
import os

OUTPUT_DIR = os.path.join("..", "output")


data = pd.DataFrame(
    {
        "my_x": [1, 2, 3, 4, 1, 2, 3, 4],
        "my_y": [3, 3, 1, 3, 2, 2, 2, 2],
        "my_label": ["a", "a", "a", "a", "b", "b", "b", "b"],
    }
)

stackorder_plot = SortedStreamD3Plot(
    data,
    x_col="my_x",
    y_col="my_y",
    label_col="my_label",
    pad=0.05,
)
output_path = stackorder_plot.plot(output_dir=OUTPUT_DIR)
print(f"\nSortedStream output location: {output_path}")
