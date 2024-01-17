from .base_plot import BaseD3Plot


class StackOrderD3Plot(BaseD3Plot):
    def format_data(self):
        # Implement specific data formatting logic for 'stackorder' template
        return self.data

    def get_template_kind(self):
        return "stackorder"
