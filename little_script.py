import pandas as pd
import numpy as np

num_rows = 10

data = {
    "label": ["class1"] * num_rows,
    "t": range(10),
    "w": np.random.rand(num_rows) * 10,  # Random values for 'w'
}

df = pd.DataFrame(data)

# Convert DataFrame to JSON
json_data = df.to_json(orient="records")

# Print or use 'json_data' in your D3.js script
print(json_data)

print("hi")
