# d3_package.py
from .template_manager import TemplateManager


class D3Plot:
    def __init__(self):
        self.template_manager = TemplateManager()

    def generate_html(self, data, template_name):
        template = self.template_manager.get_template(template_name)

        template.format_data(data)
        html_output = template.generate_html()

        return html_output
