from abc import ABC, abstractmethod
import os
import json


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
    def render_template(self, json_path, kind):
        pass

    def plot(self, output_dir=None, file_name=None):
        formatted_data = self.format_data()
        json_path = self.save_json(formatted_data, output_dir, file_name)
        rendered_html = self.render_template(json_path, self.get_template_kind())
        output_path = self.save_html(rendered_html, output_dir, file_name)
        return output_path

    def save_json(self, data, output_dir, file_name):
        if not output_dir:
            output_dir = os.getcwd()

        if not file_name:
            file_name = f"{self.get_template_kind()}_data.json"

        json_path = os.path.join(output_dir, file_name)

        with open(json_path, "w") as json_file:
            json.dump(data, json_file)

        return json_path

    def save_html(self, html_content, output_dir, file_name):
        if not output_dir:
            output_dir = os.getcwd()

        if not file_name:
            file_name = f"{self.get_template_kind()}_output.html"

        output_path = os.path.join(output_dir, file_name)

        with open(output_path, "w") as output_file:
            output_file.write(html_content)

        return output_path
