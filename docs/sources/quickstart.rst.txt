Quick Start
===========

.. contents:: Table of Contents
   :local:

Getting Started
---------------

To quickly get started with pyllplot, follow these steps:

1. Import the `SortedStream` class:

   .. code-block:: python

      from pyllplot import SortedStream

2. Create an instance of `SortedStream` with your data:

   .. code-block:: python

      # Your data dictionary or DataFrame
      data = {
          "x": [ ... ],
          "height": [ ... ],
          "label": [ ... ],
      }

      custom_plot = SortedStream(data=data, pad=0, centered=True, color_dict=None, smooth=True, interp_res=1000)

3. Show the plot:

   .. code-block:: python

      custom_plot.fig.show()
