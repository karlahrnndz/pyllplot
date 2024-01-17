# template_manager.py
import importlib
import os


class TemplateManager:
    def __init__(self):
        self.templates = {}

    def register_templates_from_directory(self, directory):
        for file_name in os.listdir(directory):
            if file_name.endswith(".py") and file_name != "__init__.py":
                template_name = os.path.splitext(file_name)[0]
                module_name = f"your_package.templates.{template_name}"
                template_class = self.load_template_class(module_name)
                self.templates[template_name] = template_class()

    @staticmethod
    def load_template_class(self, module_name):
        module = importlib.import_module(module_name)
        template_class = getattr(module, module_name.split(".")[-1])
        return template_class

    def get_template(self, template_name):
        return self.templates.get(template_name)
