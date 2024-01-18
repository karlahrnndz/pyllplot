import pytest

# from pyllplot.plotting.base_plot import D3Plot


@pytest.fixture
def example_data():
    # Define some example data for testing
    return {"example": [1, 2, 3]}


def test_generate_output(tmp_path, example_data):
    # Create a temporary directory for testing
    tmp_dir = tmp_path / "output_test"
    tmp_dir.mkdir()

    # # Instantiate D3Plot with example data and generate output
    # d3_plot = D3Plot(example_data, kind="stackorder")
    # output_html = d3_plot.generate_output()

    # Perform assertions on the output HTML or check if it exists
    assert tmp_dir.joinpath("stackorder_output.html").exists()
    # Add more assertions as needed
