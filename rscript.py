# main_script.py
from quickd3 import D3Plot

# Create an instance of D3Package
d3_plot = D3Plot()

# Sample data (replace with your actual data)
data = [
    {"category": "A", "value": 10},
    {"category": "B", "value": 20},
    {"category": "C", "value": 15},
]

# Specify the template name (replace with the desired template)
template_name = "bar_template"

# Generate HTML file
html_output = D3Plot.generate_html(data, "bar")

# Save or display the HTML output as needed
with open("output.html", "w") as f:
    f.write(html_output)
