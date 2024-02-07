
***********
Quick Start
***********

Currently `pyllplot` only allows you to create one kind of graph: a `plotly` based sorted stream graph (additional data visualization will be added over time).


Sorted Stream Graph
================

1. Import the ``SortedStream`` class:

   .. code-block:: python

      from pyllplot import SortedStream

2. Create a dataset. Your dataset can be a dictionary or a pandas DataFrame, but must contain the following columns/keys: ``['x', 'height', 'label']``:

    .. code-block:: python

        import pandas as pd

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
          "label": ["lab_1", "lab_1", "lab_1", "lab_2", "lab_2", "lab_2"]}

        data = data_dict
        data = pd.DataFrame(data_dict)

5. Create a sorted stream graph based on your data and show the plot:

    .. code-block:: python

        import plotly.io as pio
        custom_plot = SortedStream(data)
        custom_plot.fig.show()

5. ``custom_plot.fig`` is an object of type `plotly.graph_objects` containing the final visualization (you can work with it like you would a normal `plotly.graph_objects` object):

   .. code-block:: python

      custom_plot.fig.show()
      pio.write_image(custom_plot.fig, file="sorted_stream.svg")

6. The values for 'x' must be strings, numeric, categorical, boolean, or datetime. The values for 'height' must be non-negative.

Examples
================

    .. code-block:: python

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

