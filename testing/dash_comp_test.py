# Barebones script for testing functionality of
# individual dash/bootstrap/etc. compoonents
# without having to load a full app.

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
#########################

test_component_2 = html.Div(
    [
        dbc.Input(id="input", placeholder="Type something...", type="text"),
        html.Br(),
        html.P(id="output"),
    ]
)

select = dcc.Dropdown(#dbc.Select(#
    id="select",
    multi=True,
    options=[
        {"label": "Option 1", "value": "1"},
    ],
)
button = dbc.Button(
        children=['Add to list'],
        id='next_button',
        n_clicks=2)

test_component_1 = html.H3("TESTING")

test_components_list = \
    [
    test_component_1,
    test_component_2,
    button,
    select,
    dcc.Store(id='store_list', data = [])
    ]

##########################################

test_components = [html.Div(test_component) for test_component in test_components_list]

##########################################
app = dash.Dash(
    __name__,
    assets_folder="assets",
    meta_tags=[
        {"name": "viewport",
        "content": "width=device-width, initial-scale=1"}
    ]
    )
##########################################
################ CALLBACKS ###############
# has to come before layout!!!

@app.callback(
    [Output("store_list", "data")],
    [Input("input", "value"),
    Input("select", "value")],
    [State("store_list", "data")])
def store_text(value, last_value, data):
    print(f"Data: {data}; Value: {value}; Last: {last_value}")
    if value is not None and len(value) > 0:
        out = data + [value]
        if last_value is not None and data is not None:
            #last_value = [int(i) for i in last_value]
            if len(data) < len(last_value):
                out = [out[int(i)] for i in last_value]
        return [out]

# @app.callback(
#     [Output("select", "options"),
#     Output("select", "values"),
#     Output("select", "value")],
#     [Input("store_list", "data")],
#     [State("select", "options"),
#     State("next_button", "n_clicks")]
#     )
@app.callback(
    [Output("select", "options"),
    Output("select", "values"),
    Output("select", "value"),
    Output("input", "value")],
    [Input("next_button", "n_clicks")],
    [State("store_list", "data"),
    State("select", "value")]
    )
def output_text(button, data, last_val):
    #out = [(value, ind) for ind, value in enumerate(values)]
    data = list(set(data))
    ind = list(range(len(data)))
    #print(data, ind)
    #return [data]
    ###########FIX###########
    if last_val is not None:
        #last_val = [int(i) for i in last_val]
        if len(last_val) > 0 and len(last_val) < len(ind):
            ind = [ind[int(i)] for i in last_val]
    ########################
    out = [{"label": data[i], "value": i} for i in ind]
    return out, ind, ind, ""
    #return [data]
    #return [*out]

# @app.callback(
#     [Output("select", "options"),
#     Output("select", "values"),
#     Output("select", "value")],
#     [Input("select", "value")],
#     [State("select", "options"),
#     State("select", "values")]
#     )
# def update_dd(val, options, values):
#     #out = [(value, ind) for ind, value in enumerate(values)]
#     return [{"label": options[i], "value": i} for i in val]
##########################################
app.layout = html.Div(test_components)
app.run_server(debug=True)

