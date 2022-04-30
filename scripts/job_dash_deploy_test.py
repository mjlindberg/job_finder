###############################################################################
# TODO: set valid/hide dropdown options based on some criteria/selection
# TODO: dropdown styling? https://community.plotly.com/t/how-to-colorize-dropdown-field-in-dash/5648/12

# TODO: button for rescoring based on some input
# TODO: make sure wordcloud has German stopwords filtered out (and maybe degree words - e.g. 'highly')


###############################################################################
# dash & plotly dashboard of jobs from scraping

import dash

import dash_table
import pandas as pd

import dash_core_components as dcc
import dash_html_components as html

import dash_daq as daq

from dash.exceptions import PreventUpdate
######
import dash_bootstrap_components as dbc
#####

import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

##############
from flask_caching import Cache
#import functools32
from tqdm.auto import tqdm
##############
import sys; sys.path.insert(1, "classes")
from JobPosting_classes import JobPostingCollection

##########
# temp
###
import pickle, csv, json

filtered = True

#######################
#### UPLOAD DATA ######
###### upload own data

# upload_button = dcc.Upload(
#     dbc.Button(
#         children=['Upload JSON'],
#         id='upload_button',
#         n_clicks=0,
#         color="secondary",
#         className="mr-1"),
#         id = "upload_file"
#         )

upload_button = dcc.Upload(
    html.Button(
        children=['Upload JSON'],
        id='upload_button',
        style={
            'font-size': '14px',
            'width': '110px',
            'display': 'inline-block',
            #'margin-bottom': '10px',
            'margin-left': '5px',
            'height':'37px', 'margin-top': '4px'
            }
        ),
        id = "upload_file",
        style = {'width': '140px',
            'display': 'inline-block',
            #'margin-bottom': '10px', 
            'margin-left': '15px',
            'height':'37px', 'margin-top': '4px'}
        )

################ INITIALIZE ###############

app = dash.Dash(
    __name__,
    #external_stylesheets=external_stylesheets,
    assets_folder="assets",
    #external_stylesheets=[dbc.themes.BOOTSTRAP], #
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}, #scales for mobile devices
    ],
    #prevent_initial_callbacks=True
    )
#app = dash.Dash()

### ADD DATA CACHING

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})
TIMEOUT = 60

##########
 ## navbar components

dropdown_bar = html.Div([
    dcc.Dropdown(
        id='job_dropdown',
        options=[{'label':'', 'value':''}],#[{'label': f"{str(int(x[1]))}. "+x[0], 'value': x[1]} for x in job_names],
        #options=[{'label': f"{str(int(x[1])+1)}. "+x[0], 'value': x[1]} for x in job_names], #why +1 to id val?
        value=None,
        multi=False, ##TODO: make multi-selectable
        optionHeight=60,
        placeholder = "Please upload data first."#Select a job posting from the list."
    )],
    style={"white-space":"nowrap", "text-overflow": "ellipsis", "margin-right":"5px"}
    )

#####################################
## NAVIGATION BAR
navbar = dbc.Navbar(
    [
        dbc.Row(
            [
                dbc.Col( #set H2 display to 'flex' to separate
                    html.H2(children='SWISS JOBS', id = "swiss_jobs_logo", style = {"color":"white", "fontStyle":"italic","fontWeight":800, "width":"100%"}),
                    style={"min_width":"13em", "display":"inline-block", "box-sizing":"border-box", "clear":"both",
                    "margin-left":"25px", "position":"relative", "right":"5px", "bottom":"6px", "max_width":"13em", "width":"13em"}
                    
                    ),
                dbc.Col(dbc.Collapse(dropdown_bar, navbar = True, style = {"width":"100%"}),
                style={"max-width":"calc(85% - 14em)", "display":"inline-flex", "clear":"both","padding":"0px",
                "position":"absolute","left":"15em","margin-top":"10px","transform-origin":"right", "width":"85%", #see if this works or need to move style to dropdown bar directly
                "flex-grow":3, "flex-shrink":1, "flex-basis":"1%", "flex-direction":"row"}),
                # dbc.Col(
                #     job_dropdown, width = {"size":8, "order":1}
                #     ),
                # dbc.Col(
                #     html.Div(dd_sort_toggle, style = {"color":"white"}), width = "auto"
                #     )
            ],
            no_gutters = True,
            align = "center",
            style = {"margin":"0", "width":"100%","clear":"both"}
        ),
        
    ],
    sticky="top",
    style = {"backgroundColor":"#4B0082", "width":"100%", "display":"flex"}
)
#####################################


#####################################
## STICKY HEADER ROW - WITH JOB TITLE
sticky_header_row = dbc.Row(
    [
    upload_button
    ],
        style = {"position": "sticky", 'backgroundColor':'#E6E6FA', 'top':"-1px", 'height':'100%', "paddingTop":"0px","paddingBottom":"10px", "margin-top":"-15px"},
        no_gutters = True
        )
#####################################
## NEXT JOB BUTTON
next_button = html.Button(#color="info",  #dbc.Button didn't work with callback???
id='next_button', children=["NEXT"], n_clicks=2) #can't add it to a tab?


#dd_value_store = dcc.Store(id='dd_value', storage_type = "session")
######################################
## Experiment w/ using intervals to grab stdout from console
stdout_interval = dcc.Interval(id = 'interval1', interval = 1*1000)
stdout_interval_out = dcc.Interval(id = 'interval2', interval = 1*1000)
stdout_iframe = html.Iframe(id='console-out',srcDoc='',style={'width': 
'100%','height':50})
#####################################
## COMPOSE ALL COMPONENTS INTO THE LAYOUT

app.layout = html.Div(
    children=[
        stdout_interval,
        stdout_interval_out,
        dcc.Store(id = 'uploaded_datastore'),
        navbar,
        sticky_header_row,
        stdout_iframe,
        dash_table.DataTable(id='df_table', fill_width = True),
        html.Div(id='stdout_div'),
        html.Div(id='test'),
        dcc.Graph(id = 'plot_div'),
        ],
        style={"margin":0}
    )


#app.server.logger.addHandler(handler) #moved

####### Interval call back #####

import sys

# @app.callback([
#     dash.dependencies.Output('stdout_div', 'children'),
#     ],
# #[dash.dependencies.Input('job_dropdown', 'value')],
# [dash.dependencies.Input('interval1', 'n_intervals')
# ]
# )
# #[dash.dependencies.Input('toggle_dropdown_sort', 'on')])
# @cache.memoize(timeout=TIMEOUT) #make a separate data query function
# def update_interval(n):
#     stdout_orig = sys.stdout
#     f = open('out.txt', 'w+')
#     sys.stdout = f
#     #print('Intervals Passed: ' + str(n))
#     sys.stdout = stdout_orig
#     f.close()
#     return ['Intervals Passed: ' + str(n)]

@app.callback(dash.dependencies.Output('console-out', 
'srcDoc'),
    [dash.dependencies.Input('interval2', 'n_intervals')])
def update_output(n):
    file = open('dash_app.log', 'r')
    data=''
    lines = file.readlines()
    if lines.__len__()<=2:
        last_lines=lines
    else:
        last_lines = lines[-2:]
    for line in last_lines:
        data=data+line + '<BR>'
    file.close()
    return data

###############################

@app.callback([
    dash.dependencies.Output('uploaded_datastore', 'data')
    ],
#[dash.dependencies.Input('job_dropdown', 'value')],
[dash.dependencies.Input('upload_file', 'contents')
]
)
#[dash.dependencies.Input('toggle_dropdown_sort', 'on')])

@cache.memoize(timeout=TIMEOUT) #make a separate data query function
def process_upload(file):
    ######## UPLOAD DATA #########
    #print(json.loads(file.decode('utf8')))
    if not file:
        app.logger.warning("Awaiting file for upload...")
        raise PreventUpdate
    try:
        import base64
        import io
        #out = json.loads(file)
        app.logger.info("Uploading...")
        content_type, content_string = file.split(',')
        decoded = base64.b64decode(content_string)
        #file_string = file_bytes.decode('utf8')
        #file_string = io.StringIO(file_bytes.decode('utf-8'))
        #json_file = json.load(file_string)
        json_string = decoded.decode('utf8')
        json_file = json.loads(json_string)
        #return [json_file]
        return[json.loads(json_file)] # My old files are double encoded for some reason
    except Exception as e:
        app.logger.debug(e)
    else:
        "Complete."

########################################
## add dcc.Store for df

@app.callback([
    dash.dependencies.Output('df_table', 'data'),
    dash.dependencies.Output('df_table', 'columns'),
    dash.dependencies.Output('df_table', 'style_cell'),
    #dash.dependencies.Output('df_table', 'style_cell_conditional'),
    dash.dependencies.Output('df_table', 'style_table'),
    # dash.dependencies.Output('df_table', 'fixed_columns')
    ],
#[dash.dependencies.Input('job_dropdown', 'value')],
[dash.dependencies.Input('uploaded_datastore', 'data')
]
)
#[dash.dependencies.Input('toggle_dropdown_sort', 'on')])

@cache.memoize(timeout=TIMEOUT) #make a separate data query function
def add_table(data):
    if not data:
        raise PreventUpdate
    app.logger.info("Adding table...")
    #print(data.keys())
    out = data[list(data.keys())[0]]#data['2022-04-29']
    df = pd.DataFrame(out).T[['title', 'score']].applymap(lambda x:x.strip() if type(x) == str else x)
    df['score'] = round(df['score'])
    return [
        df.sort_values('score', ascending = False).to_dict('records'),
        [{"name":i, "id": i} for i in df.columns],
        {'text-align':'left'},
        # [{'if': {'column_id': 'title'},
        #  'width': '100%'},
        # {'if': {'column_id': 'score'},
        #  'width': '100%'}],
        {'height': '150px', #'minWidth':'100%','width':'100%','maxWidth':'100%',
        'overflowY': 'auto', 'textOverflow':'ellipsis'},
        # {'headers':True, 'data':2}
         ]

#####################################
@app.callback([
    dash.dependencies.Output('job_dropdown', 'options'),
    ],
#[dash.dependencies.Input('job_dropdown', 'value')],
[dash.dependencies.Input('uploaded_datastore', 'data')
]
)
#[dash.dependencies.Input('toggle_dropdown_sort', 'on')])
@cache.memoize(timeout=TIMEOUT) #make a separate data query function
def populate_dropdown(data):
    if not data:
        raise PreventUpdate
    app.logger.info("Updating dropdown menu...")
    #print(data.keys())
    out = data[list(data.keys())[0]]#data['2022-04-29']
    out = [{"label":f"{k}. {v['title']}", "value":k} for k,v in out.items()]
    #df = pd.DataFrame(out).T[['title', 'score']].applymap(lambda x:x.strip() if type(x) == str else x)
    return [out]  

#############################################################################

# @app.callback([
#     dash.dependencies.Output('test', 'children')
#     ],
# #[dash.dependencies.Input('job_dropdown', 'value')],
# dash.dependencies.Input('job_dropdown', 'value'),
# dash.dependencies.State('uploaded_datastore', 'data')
# )
# #[dash.dependencies.Input('toggle_dropdown_sort', 'on')])

# @cache.memoize(timeout=TIMEOUT) #make a separate data query function
# def add_test_data(dd_value, data):
#     if not dd_value:
#         raise PreventUpdate
#     print("Adding data...")
#     out = data[list(data.keys())[0]]#data['2022-04-29']['1']
#     out = out[dd_value]
#     return [[f"{k}:{v}" for k,v in out.items()]]

#####################################

@app.callback([
    dash.dependencies.Output('plot_div', 'figure'),
    ],
[dash.dependencies.Input('uploaded_datastore', 'data')
]
)

@cache.memoize(timeout=TIMEOUT) #make a separate data query function
def add_plot(data):
    if not data:
        raise PreventUpdate
    app.logger.info("Adding plot...")
    #print(data.keys())
    out = data[list(data.keys())[0]]#data['2022-04-29']
    df = pd.DataFrame(out).T[['title', 'score']].applymap(lambda x:x.strip() if type(x) == str else x)
    fig = px.histogram(x=df['score'], labels = {'x':'score','y':'count'})
    return [fig]

########## CHANGE-AWARE CALLBACKS (NON-UPLOAD) ##########

@app.callback([
    dash.dependencies.Output('test', 'children')
    ],
[
    # dash.dependencies.Input('df_table', 'selected_rows'),
    # dash.dependencies.Input('df_table', 'selected_row_ids')
    dash.dependencies.Input('df_table', 'active_cell'), #returns {'row':0, 'column':0,'column_id':'title'}
   # dash.dependencies.Input('df_table', 'selected_row_ids')
    ],
    dash.dependencies.State('uploaded_datastore', 'data')
)
@cache.memoize(timeout=TIMEOUT) #make a separate data query function
def update_by_table_selection(selected_cell, data):#(rows, row_ids, data):
    if not data or not selected_cell:#row_ids:
        #print(selected_cell)
        raise PreventUpdate

    try:
        row_id = selected_cell['row']
        #column = selected_cell['column'']
        #column_id = selected_cell['column_id'']
        
        out = data[list(data.keys())[0]]#data['2022-04-29']
        df = pd.DataFrame(out).T.applymap(lambda x:x.strip() if type(x) == str else x).sort_values('score', ascending = False)

        app.logger.info(f"|{df.iloc[row_id]['title'][:15]}...| data selected in table...")
        app.logger.info(df.iloc[row_id]['description'][:15])
        return [
            df.iloc[row_id]['description']
            ]
    except Exception as e:
        app.logger.debug(e)

#####################################
## LAUNCH SERVER
if __name__ == "__main__":
### logging ###
    import logging
    from logging.handlers import RotatingFileHandler

    logger = logging.getLogger('my_logger')
    handler = RotatingFileHandler('dash_app.log', maxBytes=10000, backupCount=1, mode='w')
    handler.setLevel(logging.DEBUG)

    #logger.addHandler(handler)
    app.logger.addHandler(handler) #only one that worked
    #app.server.logger.addHandler(handler)

    app.run_server(debug=True)#, use_reloader=False)
#####################################