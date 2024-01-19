from abc import ABC, abstractmethod


class BasePlot(ABC):
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def _format_data(self):
        pass

    @abstractmethod
    def _make_plot(self, filepath=None, color_palette=None, title=None, figsize=None):
        pass

    def plot(self, filepath=None, color_palette=None, title=None, figsize=None):
        self._format_data()
        self._make_plot(filepath, color_palette, title, figsize)
