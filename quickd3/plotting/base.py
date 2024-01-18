from abc import ABC, abstractmethod
import os


class BaseD3Plot(ABC):
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def format_data(self):
        pass

    @abstractmethod
    def get_template_kind(self):
        pass

    @abstractmethod
    def render_template(self, json_filename, kind):
        pass

    def plot(self, output_dir=None, base_filename=None):
        self.format_data()
        json_filename = self.save_json(output_dir, base_filename)
        rendered_html = self.render_template(json_filename, self.get_template_kind())
        output_path = self.save_html(rendered_html, output_dir, base_filename)
        return output_path

    def save_json(self, output_dir, base_filename):
        if not output_dir:
            output_dir = os.getcwd()

        if not base_filename:
            json_filename = f"{self.get_template_kind()}_data.json"

        else:
            json_filename = f"{base_filename}_data.json"

        json_path = os.path.join(output_dir, json_filename)

        self.data.to_json(json_path, orient="records")

        return json_filename

    def save_html(self, html_content, output_dir, base_filename):
        if not output_dir:
            output_dir = os.getcwd()

        if not base_filename:
            base_filename = f"{self.get_template_kind()}_viz.html"

        else:
            base_filename = f"{base_filename}_viz.html"

        output_path = os.path.join(output_dir, base_filename)

        with open(output_path, "w") as output_file:
            output_file.write(html_content)

        return output_path
