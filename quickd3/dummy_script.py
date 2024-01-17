from quickd3 import StackOrderD3Plot

data = {"example": [1, 2, 3]}

stackorder_plot = StackOrderD3Plot(data)
stackorder_output = stackorder_plot.generate_output()
print(f"StackOrder Output: {stackorder_output}")
