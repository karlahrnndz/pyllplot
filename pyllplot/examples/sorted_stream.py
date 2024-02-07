from pyllplot import SortedStream

# Example using a dictionary
data_dict = {
    "x": [3, 1, 2, 1, 2, 3],
    "height": [1, 1, 1, 3, 2, 3],
    "label": ["lab_1", "lab_1", "lab_1", "lab_2", "lab_2", "lab_2"],
}
# data_dict = {
#     'x': ['a', 'b', 'c', 'a', 'b', 'c',],
#     'height': [1, 1, 1, 3, 2, 3],
#     'label': ['lab_1', 'lab_1', 'lab_1', 'lab_2', 'lab_2', 'lab_2']
# }

# data_dict = {
#     'x': ['2022-01-01 12:34:56', '2022-01-02 12:34:56', '2022-02-01 12:36:00',
#           '2022-01-01 12:34:56', '2022-01-02 12:34:56', '2022-02-01 12:36:00'],
#     'height': [1, 1, 1, 3, 2, 3],
#     'label': ['lab_1', 'lab_1', 'lab_1', 'lab_2', 'lab_2', 'lab_2']
# }
# data_dict['x'] = pd.to_datetime(data_dict['x'])

# data_dict = {
#     'x': ['2022-01-01', '2022-01-02', '2022-01-03',
#           '2022-01-01', '2022-01-02', '2022-01-03',],
#     'height': [1, 1, 1, 3, 2, 3],
#     'label': ['lab_1', 'lab_1', 'lab_1', 'lab_2', 'lab_2', 'lab_2']
# }
# data_dict['x'] = pd.to_datetime(data_dict['x'])

custom_plot = SortedStream(
    data=data_dict, pad=0, centered=True, color_dict=None, smooth=True, interp_res=10000
)
custom_plot.fig.show()

# print('hi')
