import dash
from dash import html, dcc

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.Div("Welcome to My Dashboard", className="my-custom-class"),
        dcc.Graph(
            id="example-graph",
            figure={
                "data": [
                    {"x": [1, 2, 3], "y": [4, 1, 2], "type": "bar", "name": "SF"},
                    {"x": [1, 2, 3], "y": [2, 4, 5], "type": "bar", "name": "NYC"},
                ],
                "layout": {"title": "Example Graph"},
            },
            className="dash-graph",
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
