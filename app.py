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
                                  html.P("An artificial market will be populated by two kinds of traders: "
                                         + "Fundamentalist, that only buy the asset if it is above their valuation "
                                         + "and sell it if it is below and Chartists that buy or sell according to momentum. "
                                         + "All traders start with the same wealth of 10000.0 and may submit 30% of their wealth "
                                         + "in orders in each period (if their wealth goes to zero they cannot submit orders). "
                                         + "Fundamentalists submit Limit Orders and Chartists submit Market Orders. "
                                         + "The Valuations for Fundamentalists and the time windows for the momentum indicator "
                                         + "for Chartists are drawn from a normal distribution (set mean and variance below)."
                                         ),

                                  html.P('Configure Fundamentalists:'),
                                  html.Div(
                                      [
                                          dcc.Input(
                                              id="n_fund", type="number",
                                              debounce=True, placeholder="Number of Traders",
                                          ),
                                          dcc.Input(
                                              id="f_dist_mean", type="number",
                                              debounce=True, placeholder="Mean Value",
                                          ),
                                          dcc.Input(
                                              id="f_dist_var", type="number",
                                              debounce=True, placeholder="Variance of Values",
                                          ),
                                      ]
                                  ),
                                  html.P('Configure Chartists:'),
                                  html.Div(
                                      [
                                          dcc.Input(
                                              id="n_chart", type="number",
                                              debounce=True, placeholder="Number of Traders",
                                          ),
                                          dcc.Input(
                                              id="c_dist_mean", type="number",
                                              debounce=True, placeholder="Mean Window Length",
                                          ),
                                          dcc.Input(
                                              id="c_dist_var", type="number",
                                              debounce=True, placeholder="Variance of window",
                                          ),
                                      ]
                                  ),
                                  html.P('Set number of trading periods:'),
                                  html.Div(
                                      [
                                          dcc.Input(
                                              id="length", type="number",
                                              debounce=True, placeholder="length of simulation",
                                          ),
                                      ]
                                  ),
                                  html.Button('Simulate!', id='submit-val', n_clicks=0, style={'color': '675438'}),
                              ]
                              ),
                     html.Div(className='eight columns div-for-charts bg-grey',
                              children=[
                                  dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=True),
                                  dcc.Graph(id='bar', config={'displayModeBar': False}, animate=True)
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
    #global data

    print(n_fund)
    sim = Simulation(length,
                     n_fund,
                     n_chart,
                     (f_dist_mean, f_dist_var),
                     (c_dist_mean, c_dist_var)
                     )

    sim.start()
    data = sim.market_prices
    update_bar(data)



    layout = go.Layout(
        title="Simulated Prices",
        plot_bgcolor="#FFF",  # Sets background color to white
        xaxis=dict(
            title="Price Evolution",
            linecolor="#BCCCDC",  # Sets color of X-axis line
            showgrid=False  # Removes X-axis grid lines
        ),
        yaxis=dict(
            title="Prices",
            linecolor="#BCCCDC",  # Sets color of Y-axis line
            showgrid=False,  # Removes Y-axis grid lines
        )
    )

    figure = go.Figure(
        data=go.Scatter(x=[i for i in range(len(sim.market_prices))], y=sim.market_prices),
        layout=layout
    )

    return figure


#@app.callback(Output('bar', 'figure'),[Input('submit-val', "n_clicks")])
def update_bar(data):

    layout = go.Layout(
        title="Profits",
        plot_bgcolor="#FFF",  # Sets background color to white
        xaxis=dict(
            title="Traders",
            linecolor="#BCCCDC",  # Sets color of X-axis line
            showgrid=False  # Removes X-axis grid lines
        ),
        yaxis=dict(
            title="PnL",
            linecolor="#BCCCDC",  # Sets color of Y-axis line
            showgrid=False,  # Removes Y-axis grid lines
        )
    )

    figure = go.Figure(
        data=go.Scatter(x=[i for i in range(len(data))], y=data),
        layout=layout
    )

    return figure


# Run the app
if __name__ == '__main__':
    app.run_server(debug=False, dev_tools_ui=False, dev_tools_props_check=False)
