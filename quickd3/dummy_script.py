import pandas as pd

from quickd3 import StackOrderD3Plot

data = pd.DataFrame(
    {
        "my_x": [1, 2, 3, 1, 2, 3],
        "my_y": [3, 2, 1, 1, 2, 1],
        "my_label": ["a", "a", "a", "b", "b", "b"],
    }
)

stackorder_plot = StackOrderD3Plot(
    data, x_col="my_x", y_col="my_y", label_col="my_label"
)
stackorder_output = stackorder_plot.plot()
print(f"StackOrder Output: {stackorder_output}")
