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
                                  html.H1('Stock Market Simulator'),
                                  html.P("An artificial market will be populated by two kinds of traders: "
                                         + "Fundamentalist, that only buy the asset if it is above their valuation "
                                         + "and sell it if it is below and Chartists that buy or sell according to momentum. "
                                         + "All traders start with the same wealth of (10000 Cash and 100 Stocks) and may submit 30% of their total wealth "
                                         + "in orders in each period (if their wealth goes to zero they cannot submit orders). "
                                         + "Fundamentalists submit Limit Orders and Chartists submit Market Orders. "
                                         + "The Valuations for Fundamentalists and the time windows for the momentum indicator "
                                         + "for Chartists are drawn from a normal distribution (set mean and variance below)."
                                         ),

                                  html.H2('Configure Fundamentalists:'),
                                  html.Div(
                                      [
                                          dcc.Input(
                                              id="n_fund", type="number",
                                              debounce=True, placeholder="Number of Traders",
                                          ),
                                          dcc.Input(
                                              id="f_dist_mean", type="number",
                                              debounce=True, placeholder="Mean Value (try: 100)",
                                          ),
                                          dcc.Input(
                                              id="f_dist_var", type="number",
                                              debounce=True, placeholder="Variance of Values",
                                          ),
                                      ]
                                  ),
                                  html.H2('Configure Chartists:'),
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
                                  html.H2('Set Number of Trading Periods:'),
                                  html.Div(
                                      [
                                          dcc.Input(
                                              id="length", type="number",
                                              debounce=True, placeholder="Length of Simulation",
                                          ),
                                      ]
                                  ),
                                  html.H2(''),
                                  html.H2(''),
                                  html.Button('Simulate!', id='submit-val', n_clicks=0, style={'color': 'DarkOrange'}),
                                  html.H2(''),
                                  html.H2(''),
                                  html.A('Find the Source Code here', href='https://github.com/kgeoffrey'),
                                  html.H2('© Geoffrey Kasenbacher 2020'),
                              ]
                              ),
                     html.Div(className='eight columns div-for-charts bg-grey',
                              children=[
                                  dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=False),
                                  dcc.Graph(id='bar',
                                            config={'displayModeBar': False},
                                            animate=False,
                                            style={'height': '40%'},
                                            )
                              ]
                              ),
                     html.Div(id="data_timeseries", style={"display": "none"}),
                     html.Div(id="data_bar", style={"display": "none"})
                 ]
                 )
    ]
)


@app.callback(
    [Output("data_timeseries", "children"),
     Output("data_bar", "children")],
    [Input("submit-val", "n_clicks")],
    [State('length', 'value'),
     State('n_fund', 'value'),
     State('n_chart', 'value'),
     State('f_dist_mean', 'value'),
     State('f_dist_var', 'value'),
     State('c_dist_mean', 'value'),
     State('c_dist_var', 'value'),
     ]
)
def simulate_data(val, length, n_fund, n_chart, f_dist_mean, f_dist_var, c_dist_mean, c_dist_var):
    sim = Simulation(length,
                     n_fund,
                     n_chart,
                     (f_dist_mean, f_dist_var),
                     (c_dist_mean, c_dist_var)
                     )
    sim.start()

    sim.pnl_df["PNL"] = sim.pnl_df["PNL"] - 100 * f_dist_mean

    return sim.market_prices_df.to_json(), sim.pnl_df.to_json()


@app.callback(
    Output('timeseries', 'figure'),
    [Input('data_timeseries', "children")],
)
def update_graph(data):
    data = list((pd.read_json(data))[0])
    # print(data)

    layout = go.Layout(
        title="Simulated Prices",
        plot_bgcolor="#FFF",
        xaxis=dict(
            title="Price Evolution",
            linecolor="#BCCCDC",
            showgrid=False
        ),
        yaxis=dict(
            title="Prices",
            linecolor="#BCCCDC",
            showgrid=False,
        )
    )

    figure = go.Figure(
        data=go.Scatter(x=[i for i in range(len(data))], y=data, marker_color="dodgerblue", opacity=0.8),
        layout=layout
    )

    return figure


@app.callback(Output('bar', 'figure'),
              [Input('data_bar', "children")],
              )
def update_bar(data):
    data = pd.read_json(data)

    print(data)
    fundamentalists = data[data['Trader'].str.contains("fundamentalist")]
    chartists = data[data['Trader'].str.contains("chartist")]
    xs = ["Fundamentalists", "Chartists"]

    layout = go.Layout(
        title="Total Profits (Unrealized + Realized)",
        plot_bgcolor="#FFF",
        xaxis=dict(
            title="Traders",
            #linecolor="#BCCCDC",  # Sets color of X-axis line
            showgrid=False, # Removes X-axis grid lines
            showticklabels=False
        ),
        yaxis=dict(
            title="PnL",
            # linecolor="#BCCCDC",  # Sets color of Y-axis line
            showgrid=False,  # Removes Y-axis grid lines
        )
    )

    bars = [
        go.Bar(name = "Fundamentalists", x=list(fundamentalists["Trader"]), y=list(fundamentalists["PNL"]),
               text=list(fundamentalists["PNL"]), marker_color="mediumseagreen",opacity=0.8),
        go.Bar(name = "Chartist", x=list(chartists["Trader"]), y=list(chartists["PNL"]),
               text=list(chartists["PNL"]), marker_color="steelblue", opacity=0.8)
    ]

    figure = go.Figure(
        data=bars,
        layout=layout
    )

    return figure


# Run the app
if __name__ == '__main__':
    app.run_server(debug=False, dev_tools_ui=False, dev_tools_props_check=False)
