from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from jinja2 import Template


class BaseTemplate(ABC):  # Inherit from ABC to define abstract methods
    def __init__(self, template_name):
        self.template_name = template_name
        self.html_start = None
        self.html_middle = None
        self.html_end = None
        self.html = None
        self.json_data = None
        # self.jinja_path = self.

    @abstractmethod
    def format_data(self, *args, **kwargs):
        pass

    def generate_html(self, output_file):
        # Read the template from the HTML file
        with open("template.html", "r") as file:  # TODO change file
            template_content = file.read()

        # Create a Jinja2 template
        template = Template(template_content)

        # Define data to be injected into the template
        data = {
            "json_data": self.json_data,
        }

        # Render the template with the data
        rendered_content = template.render(data)

        # Print or use the rendered content as needed
        print(rendered_content)

    def prettify_and_save_html(self, output_file):
        # Parse the HTML string using html5lib
        soup = BeautifulSoup(self.html, features="html5lib")

        # Prettify the HTML content
        prettified_html = soup.prettify()

        # Save the prettified HTML to a file
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(str(prettified_html))
