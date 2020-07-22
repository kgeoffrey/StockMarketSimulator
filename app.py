from market_sim.simulation import *
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output, State
import pandas as pd

# Initialise the app
app = dash.Dash(__name__)

server = app.server

# Define the app
app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[
                     html.Div(className='four columns div-user-controls',
                              children=[
                                  html.H2('Stock Market Simulator'),
                                  html.P('Visualising time series with Plotly - Dash.'),
                                  html.P('Pick one or more stocks from the dropdown below.'),
                                  html.Div(
                                      [
                                          dcc.Input(
                                              id="length", type="number",
                                              debounce=True, placeholder="length of simulation",
                                          ),
                                          dcc.Input(
                                              id="n_fund", type="number",
                                              debounce=True, placeholder="Number of Fundamentalists",
                                          ),
                                          dcc.Input(
                                              id="n_chart", type="number",
                                              debounce=True, placeholder="Number of Chartists",
                                          ),
                                          dcc.Input(
                                              id="f_dist_mean", type="number",
                                              debounce=True, placeholder="Distribution of fundamentalists",
                                          ),
                                          dcc.Input(
                                              id="f_dist_var", type="number",
                                              debounce=True, placeholder="Distribution of fundamentalists",
                                          ),

                                          dcc.Input(
                                              id="c_dist_mean", type="number",
                                              debounce=True, placeholder="Distribution of chartists",
                                          ),
                                          dcc.Input(
                                              id="c_dist_var", type="number",
                                              debounce=True, placeholder="Distribution of chartists",
                                          ),
                                          # html.Hr(),
                                          html.Div(id="number-out"),
                                      ]
                                  ),
                                  html.P('Run Simulation below!'),
                                  html.Button('Simulate!', id='submit-val', n_clicks=0, style={'color': '675438'}),
                              ]
                              ),
                     html.Div(className='eight columns div-for-charts bg-grey',
                              children=[
                                  dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=True)
                              ]
                              ),
                 ]
                 )
    ]
)


@app.callback(
    Output("number-out", "children"),
    [Input("length", "value"), Input("f_dist_mean", "value"), Input("c_dist_var", "value")],
)
def number_render(fval, tval, rangeval):
    return "dfalse: {}, dtrue: {}, range: {}".format(fval, tval, rangeval)


@app.callback(Output('timeseries', 'figure'),
              [Input('submit-val', "n_clicks")],
              [State('length', 'value'),
               State('n_fund', 'value'),
               State('n_chart', 'value'),
               State('f_dist_mean', 'value'),
               State('f_dist_var', 'value'),
               State('c_dist_mean', 'value'),
               State('c_dist_var', 'value'),
               ]
              )
def update_graph(val, length, n_fund, n_chart, f_dist_mean, f_dist_var, c_dist_mean, c_dist_var):
    print(n_fund)
    sim = Simulation(length,
                     n_fund,
                     n_chart,
                     (f_dist_mean, f_dist_var),
                     (c_dist_mean, c_dist_var)
                     )

    sim.start()
    sim.market_prices

    layout = go.Layout(
        title="Historic Prices",
        plot_bgcolor="#FFF",  # Sets background color to white
        xaxis=dict(
            title="time",
            linecolor="#BCCCDC",  # Sets color of X-axis line
            showgrid=False  # Removes X-axis grid lines
        ),
        yaxis=dict(
            title="price",
            linecolor="#BCCCDC",  # Sets color of Y-axis line
            showgrid=False,  # Removes Y-axis grid lines
        )
    )

    figure = go.Figure(
        data=go.Scatter(x=[i for i in range(len(sim.market_prices))], y=sim.market_prices),
        layout=layout
    )

    return figure

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False,dev_tools_ui=False,dev_tools_props_check=False)
