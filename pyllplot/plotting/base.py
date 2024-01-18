from abc import ABC, abstractmethod


class BasePlot(ABC):
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def format_data(self):
        pass

    @abstractmethod
    def make_plot(self, filepath=None, color_palette=None):
        pass

    def plot(self, filepath=None, color_palette=None):
        self.format_data()
        self.make_plot(filepath, color_palette)
