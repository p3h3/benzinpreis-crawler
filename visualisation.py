import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from plotly import subplots

from time import sleep
from datetime import datetime

from db_helper import DbHelper

from config import *

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H1('Benzinpreis Visualisation'),
        html.Div(id='update-price-text'),
        dcc.Graph(id='update-graph'),
        dcc.Interval(
            id='graph-interval-component',
            interval=2000,
            n_intervals=0
        ),
        dcc.Interval(
            id='text-interval-component',
            interval=500,
            n_intervals=0
        )
    ])
)


@app.callback(Output(component_id='update-graph', component_property='figure'),
              [Input(component_id='graph-interval-component', component_property='n_intervals')])
def update_graph_live(n):
    global db_helper

    # Create the graph with subplots
    fig = subplots.make_subplots(rows=3, cols=1, vertical_spacing=0.1)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    fig.update_layout(width=1800, height=700)
    #fig['layout']['legend'] = {'x': 0, 'y': 0, 'xanchor': 'left'}

    try:
        # Collect historic data
        data = list(reversed(db_helper.get_latest_historic_data(500)))

        times = [item[0] for item in data]
        prices = [float(item[1]) for item in data]


        # creating traces [::3] means only every third value
        fig.append_trace({
            'x': times[::3],
            'y': prices[::3],
            'name': 'Market price',
            'mode': 'lines+markers',
            'type': 'scatter'
        }, 1, 1)

    except KeyboardInterrupt:
        print("ERROR: while executing database select query")

    return fig


if __name__ == '__main__':
    # initialising database connection
    db_helper = DbHelper(db_user, db_password, db_hostname, db_name)

    try:
        while True:
            print("INFO: Starting webserver..")
            app.run_server(debug=True, port=8000, host='0.0.0.0')
            print("INFO: Stopped webserver!")

            sleep(1)
    except KeyboardInterrupt:
        print("INFO: Exiting program!")

        print("INFO: Closing database..")
        db_helper.close()
        print("INFO: Closed database!")