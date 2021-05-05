###############################################################################
# TODO: set valid/hide dropdown options based on some criteria/selection
# TODO: dropdown styling? https://community.plotly.com/t/how-to-colorize-dropdown-field-in-dash/5648/12

# TODO: button for rescoring based on some input
# TODO: make sure wordcloud has German stopwords filtered out (and maybe degree words - e.g. 'highly')


###############################################################################
# dash & plotly dashboard of jobs from scraping

import dash
import dash_core_components as dcc
import dash_html_components as html

import dash_daq as daq

from dash.exceptions import PreventUpdate
######
import dash_bootstrap_components as dbc
#####

import plotly.graph_objs as go
import pandas as pd

##############
from flask_caching import Cache
#import functools32
from tqdm.auto import tqdm
##############

from JobPosting_classes import JobPostingCollection

##########
# temp
###
import pickle, csv, json

filtered = True

#######################

if filtered is True:
    json_filepath = "all_jobs_filtered.json"
else:
    json_filepath = "all_jobs.json"
#read data
with open(json_filepath, "r") as f:
    all_jobs = json.loads(json.load(f))

jobs = [v for k,v in dict(all_jobs).items()][0]

## SORT JOBS

#jobs = dict(sorted(jobs.items(), key=lambda item: item[1]['score'], reverse = True)) #not working
########################### #changed range(1, len(jobs)) to jobs.keys() for filtered. but why?

unsorted_job_names = [(jobs[str(job)]['title'], job) for job in jobs.keys() if jobs[str(job)]['language'] == "en"]
#####
#temp
unsorted_scores = [jobs[str(job)]['score'] for job in jobs.keys() if jobs[str(job)]['language'] == "en"]
############
job_names = [x for y, x in sorted(zip(unsorted_scores, unsorted_job_names), reverse=True)]
scores = [y for y, x in sorted(zip(unsorted_scores, unsorted_job_names), reverse=True)]
#############

for job in jobs:
    jobs[str(job)]['description'] = "\n".join([f"#### **{d}**" if len(d.split(' ')) <= 4 and len(max(d.split(' '), key = len).strip()) >= 1 else d for d in jobs[str(job)]['description'].split("\n")])
#****
################ INITIALIZE ###############
##external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']#[dbc.themes.BOOTSTRAP]
##local_stylesheets = ['assets/bWLwgP.css'] #manually edited body margins; needs to be in an "assets" folder in same dir; loaded automatically...?

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

########
from numpy import percentile, float64 as f64
from itertools import compress

percentiles = percentile(scores, range(0, 100, 25), interpolation = 'midpoint')

bound1 = len(list(compress(scores,list(compress(scores < percentiles[1], scores >= percentiles[0])))))
bound2 = len(list(compress(scores,list(compress(scores < percentiles[2], scores >= percentiles[1])))))
bound3 = len(list(compress(scores,list(compress(scores <= percentiles[3], scores >= percentiles[2])))))

#'annotations':f"Total # of jobs: {len(jobs)}"

import plotly.express as px
# fig = px.scatter(x="sepal_width", y="sepal_length")
# init_plot = dcc.Graph(figure=fig)

####################################
#job_names = [(jobs[str(job)]['title'], job) for job in range(1, len(jobs))]

fig = px.histogram(x=scores, labels = {'x':'score','y':'count'})
init_plot = dcc.Graph(figure=fig)

##### NOT YET IMPLEMENTED PROPERLY:
#### weird frankenstein of JSON and JobPostingCollection obj; need to support BOTH.

from io import BytesIO
import base64

wordcloud = html.Div([html.Img(id="image_wc")],
style={'textAlign': 'center', 'opacity':'0.9', 'verticalAlign':'center'})
#jpcollection = pickle.load(open("jobs_collection_latest.pickle", "rb")) #NOT FILTERED
jpcollection = pickle.load(open("jobs_collection_latest.pickle", "rb")).generate_wordcloud().to_image()

# def plot_wordcloud(jbc_obj:JobPostingCollection):
#     return jbc_obj.generate_wordcloud().to_image()

@app.callback(dash.dependencies.Output('image_wc', 'src'), [dash.dependencies.Input('image_wc', 'id')])
def make_image(b):
    img = BytesIO()
    jpcollection.save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

####################################

# init_plot = dcc.Graph(
#         id='plot',
#         figure=go.Figure({
#             'data': [
#                 {'x': ["Lower", "Mid", "Upper"], 'y': [bound1, bound2, bound3], 'type': 'bar', 'name': 'Percentile job scores'},
#                 {'x': ["Lower", "Mid", "Upper"], 'y': [
#                     sum(scores < f64(0)),
#                     sum(list(compress((scores > f64(-10)),(scores < f64(1))))),
#                     sum(scores >= f64(1))
#                     ],
#                     'type': 'bar', 'name': 'Extremes'},
#             ],
#             'layout': {
#                 'title': 'Percentiles of scoring'
#             }#,
#             #'edits': {
#             #    'annotationText':f"Total # of jobs: {len(jobs)}"
#            # }
#         })
#     )

##########################################################
### TOGGLE - sort dropdown by score or not
dd_sort_toggle = daq.BooleanSwitch(
        id='toggle_dropdown_sort',
        on=True,
        color="#9B51E0",
        label="Sort",
        labelPosition="right",
        disabled = False if len(scores) > 0 else True
    )
    
#job_names = [(jobs[str(job)]['title'], job) for job in range(1, len(jobs)) if jobs[str(job)]['language'] == "en"]
#scores = [jobs[job]['score'] for job in range(1, len(jobs)) if jobs[str(job)]['language'] == "en"]
sorted_dd = [{'label': f"{str(int(x[1])+1)}. "+x[0], 'value': x[1]} for x in job_names]
unsorted_dd = [{'label': f"{str(int(x[1])+1)}. "+x[0], 'value': x[1]} for x in unsorted_job_names]

### FIX?
dd_options = {"unsorted": unsorted_dd, "sorted":sorted_dd}
###

@app.callback(
    dash.dependencies.Output('job_dropdown', 'value'), #reset dropdown on toggle
    dash.dependencies.Output('job_dropdown', 'options'),
    [dash.dependencies.Input('toggle_dropdown_sort', 'on')])
    #[dash.dependencies.State('job_dropdown', 'options')])
#@cache.memoize(timeout=TIMEOUT)
def update_dd(on):
    #global dd_options #necessary?
    sort = "sorted" if on is True else "unsorted"
    return None, dd_options[sort]
########################################
job_dropdown = html.Div([
    dcc.Dropdown(
        id='job_dropdown',
        options=[{'label': f"{str(int(x[1])+1)}. "+x[0], 'value': x[1]} for x in job_names],
        value=None,
        multi=False, ##TODO: make multi-selectable
        optionHeight=60,
        placeholder = "Select a job posting from the list."
    )],
    style={"white-space":"nowrap", "text-overflow": "ellipsis", "margin-right":"5px"}
    )

# job_desc_area =  dcc.Textarea(

#         id='job_desc_area',
#         value='Textarea content initialized\nwith multiple lines of text',
#         style={'width': '100%', 'height': 300},
#     )

#job_desc_output = html.Div(id='job_desc_output', style={'whiteSpace': 'pre-line'})
job_desc_output = dcc.Markdown(id='job_desc_output', style={'whiteSpace': 'pre-line', "margin-left":"50px", "margin-right":"50px", "padding-top":"30px"})

#job_title = html.H2(id='job_title')
job_title = html.H3(id="job_title", style = {"margin-left":"25px", "margin-bottom":0, "display": "inline-block"})
#job_keywords = html.H5(id='job_keywords', style={
job_keywords = dcc.Markdown(id='job_keywords', style={
    "verticalAlign": "center",
    "width":"50%",
    "display": "inline-block",
    #"box-sizing":"border-box",
    "margin-left": "40px",
    "margin-right": "-155px",
    }
    )
#job_url = html.Link(id='job_url')


############
# TODO: set bodystyle margin to 0 (margin-top to -5) and then...
# TODO: move all text to the right a bit (set margin-left to 25px)
# TODO: H2 text - "position":"relative", "bottom":"5px"
# TODO: margin-bottom: 5px; margin-top: -5-10px for job title H3 tag; don't know if that fixes gap
# TODO - margin-bottom: 5px for row w/ linkedin button
# TODO - jobtitle fontsize: clamp(16px, 4vw, 30px)


#######
#html.Div()


#####################################
## DROPDOWN MENU

dropdown_bar = dbc.Row(
    [
        dbc.Col(job_dropdown, style={"width":"84%", "display":"inline-block", "padding":"0px", "clear":"both", "verticalAlign": "center", "margin-left":"10px", "margin-top":"25px", "transform-origin":"right", "position":"relative", "left":0}),
        dbc.Col(html.Div(dd_sort_toggle, style = {"color":"white", "padding":"0px"}), style={"width":"8%", "display":"inline-flex", "padding":"0px", "clear":"both","verticalAlign": "top","margin-top":"25px"})
    ],
    no_gutters = True,
    className = "ml-auto flex-nowrap mt-3 mt-md-0",
    align = "right",
    style={"width":"100%"}
)

####################################
## INDICATOR OF TOTAL JOBS FOUND
total_jobs_badge = dbc.Button(
    ["Jobs found: ", dbc.Badge(f"{len(jobs)}", color="light", className="ml-1")],
    color="success", id="total_jobs_badge", disabled=False, style = {"verticalAlign":"top", "margin":0, "margin-left":"40px", "margin-top":"20px"}
)
############################################
## HOVER TEXT - LINKEDIN
popover_children = [
    dbc.PopoverHeader(""),
    dbc.PopoverBody("Go to LinkedIn page with job posting.", id = "linkedin_popover_text"),
]

popover_linkedin = dbc.Popover(popover_children, id="linkedin_popover",trigger = "hover", target = "linkedin_logo", placement="right-start auto-end")
#####################################

#####################################
## NAVIGATION BAR
navbar = dbc.Navbar(
    [
        dbc.Row(
            [
                dbc.Col( #set H2 display to 'flex' to separate
                    html.H2(children='SWISS JOBS', style = {"color":"white", "fontStyle":"italic","fontWeight":800, "width":"100%"}),
                    style={"min_width":"13em", "display":"inline-block", "box-sizing":"border-box", "clear":"both",
                    "margin-left":"25px", "position":"relative", "right":"5px", "bottom":"6px", "max_width":"13em", "width":"13em"}
                    ),
                dbc.Col(dbc.Collapse(dropdown_bar, navbar = True, style = {"width":"100%"}),
                style={"max-width":"calc(85% - 14em)", "display":"inline-flex", "clear":"both","padding":"0px",
                "position":"absolute","left":"15em","margin-top":"-5px","transform-origin":"right", "width":"85%", #see if this works or need to move style to dropdown bar directly
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
## LINKEDIN LOGO + URL
linkedin_logo_component = html.Div(children=[job_title,
        dcc.Link(
            html.Img(
                src='https://cdn.iconscout.com/icon/free/png-256/linkedin-42-151143.png',
                style={'height':'45px', "verticalAlign":"top", "margin-left":"10px", "margin-right":"30px", "margin-top":"9px", "display": "none"},
                id="linkedin_logo"
            ),
            id='job_url',
            target = "_blank", #open in new tab/window
            href = "javascript:void(0);"),
            popover_linkedin
            ],
            style={
                "display": "inline-block",
                "margin-right": "20px",
                "verticalAlign": "top",
                "margin-left": "5px"
                }
            )

#####################################
## PAGE BODY - PLOT DIV
plot_div = html.Div(id="plot_div", children = [init_plot])
#####################################
## LOADING CONTENT INDICATOR
loading_spinner = html.Div([
    dbc.Spinner(
        html.Div(id="loading_output"),color="primary", spinner_style={"width": "1rem", "height": "1rem", "clear":"both", "margin":0, "padding":0})
        ], id = "spinner",
        style = {"margin":0, "padding":0, "clear":"both"}
        )

#####################################
## STICKY HEADER ROW - WITH JOB TITLE
sticky_header_row = dbc.Row(
    [total_jobs_badge,
    loading_spinner,
    linkedin_logo_component,
    job_keywords
    ],
        style = {"position": "sticky", 'backgroundColor':'#E6E6FA', 'top':"-1px", 'height':'100%', "paddingTop":"0px","paddingBottom":"10px", "margin-top":"-15px"},
        no_gutters = True
        )
#####################################
## NEXT JOB BUTTON
next_button = html.Button(#color="info",  #dbc.Button didn't work with callback???
id='next_button', children=["NEXT"], n_clicks=2) #can't add it to a tab?

#####################################
## TABS

# WON'T WORK WITH DUPLICATE ELEMENTS; need unique ids
# tabs = html.Div([
#     dcc.Tabs(id="tabs", value='tab-1', children=[
#         dcc.Tab(label='Tab one', value='tab-1', children=[navbar, sticky_header_row, plot_div]),
#         dcc.Tab(label='Tab two', value='tab-2', children=[navbar, sticky_header_row, job_desc_output]),
#     ]),
#     html.Div(id='tabs-content')
# ])


# job_tabs = [
#     dcc.Tab(label='Job description', value='job-tab-1'),
#     dcc.Tab(label='Other info', value='job-tab-2')
#     ]

# plot_tabs = [
#     dcc.Tab(label='Word Cloud', value='plot-tab-1'),
#     dcc.Tab(label='Statistics', value='plot-tab-2')
#     ]

tabs_group = [
    dcc.Tab(label='Word Cloud', value='tab-1', id = 'tab-1'),
    dcc.Tab(label='Statistics', value='tab-2', id = 'tab-2')
    ]

tabs_container = dcc.Tabs(children = tabs_group, id="tabs", value='tab-1')
selected_tabs = [tabs_container,html.Div(id='tabs-content')]

current_tabs = html.Div(children = selected_tabs, id = "current_tabs")

# @app.callback(
#     [dash.dependencies.Output('tab-1', 'label'),
#     dash.dependencies.Output('tab-2', 'label')],
#     dash.dependencies.Input('job_dropdown', 'value'))
# def set_tabs(value):
#     print(value)
#     if value is None:
#         return ['Word Cloud', 'Statistics']
#     else:
#         print("CHANGE")
#         return ['Job description', 'Extra info']

@cache.memoize(timeout=TIMEOUT)
@app.callback(
    [dash.dependencies.Output('tabs-content', 'children')],
    [dash.dependencies.Input('tabs', 'value'),
    dash.dependencies.Input('tab-1', 'label')],
    dash.dependencies.State('tabs', 'children'))
def render_content(tab, unused, elem):
    if tab == 'tab-1':
        if elem[0]['props']['label'] == 'Word Cloud':
            return [html.Div([
            wordcloud
        ])]
        else:
            return [html.Div([
                job_desc_output
            ])]
    elif tab == 'tab-2':
        if elem[1]['props']['label'] == 'Statistics':
            return [html.Div([
            plot_div
        ])]
        else:
            return [html.Div([
                "TEST"
            ])]

####################################
## JOB POSTING RECENCY

import requests
from bs4 import BeautifulSoup as bs

def check_job_status(job_url):
    r = requests.get(job_url)
    soup = bs(r.content, 'html.parser')
    times_ago = soup.find_all("span", {"class": "topcard__flavor--metadata posted-time-ago__text"})
    if len(times_ago) > 0:
        time_ago = times_ago[0].text
        by, freq, period = time_ago.split(" ")
        if by.isnumeric():
            by, freq, period = freq, period, by
            tkey = {'h':'hour', 'd':'day', 'w':"week",'m':'month'}
        else:
            tkey = {'h':'Stund', 'd':'Tag', 'w':"Woche",'m':'Monat'}
        del by

        if period.startswith(tkey['h']) or period.startswith(tkey['d']):
            recency = 'recent'
        elif period.startswith(tkey['w']):
            recency = "semi-recent"
        elif period.startswith(tkey['m']):
            recency = "old" if int(freq) != 1 else "semi-recent"
    else:
        return None
    closed = soup.find_all("figcaption", {"class":"closed-job__flavor--closed topcard__flavor--closed"})
    if len(closed) > 0:
        return [recency, "JOB CLOSED"]
    else:
        return recency

# recency_badges = html.Span(
#     [
#         dbc.Badge("Recent", pill=True, color="success", className="mr-1", id='recency_recent', style={'visibility':'hidden'}),
#         dbc.Badge("Semi-recent", pill=True, color="warning", className="mr-1", id='recency_semi-recent', style={'visibility':'hidden'}),
#         dbc.Badge("Old", pill=True, color="danger", className="mr-1", id='recency_old', style={'visibility':'hidden'}),
#     ]
# )

recency_badge_span = html.Span(id='recency_span')

recency_badges = {
    'recent':dbc.Badge("Recent", pill=True, color="success", className="mr-1", id='recency_recent'),
    'semi-recent':dbc.Badge("Semi-recent", pill=True, color="warning", className="mr-1", id='recency_semi-recent'),
    'old':dbc.Badge("Old", pill=True, color="danger", className="mr-1", id='recency_old')
    }


def update_recency(job_url):
    recency = check_job_status(job_url)
    if recency is None:
        return None
    else:
        return recency
print("Pre-caching data...")
recency_statuses = {job['url']:update_recency(job['url']) for job in tqdm(jobs.values())}
# this might be unnecessary since all jobs won't be of interest
# and takes ~5 minutes to run

####################################
## VALUE CACHING/STORING
# needed for button thing above & needs to be in layout

# dcc.Store(id='session', storage_type='session')
# dcc.Store(id='memory')
# dcc.Store(id='local', storage_type='local')

dd_value_store = dcc.Store(id='dd_value', storage_type = "session")

# dd_value_store = dcc.Store(id='dd_value', storage_type = "session")

# @app.callback( #NEEDS TO BE AFTER TABS?
#     dash.dependencies.Output("dd_value", 'data'),
#     [dash.dependencies.Input('next_button', 'n_clicks')],
#     [dash.dependencies.State('job_dropdown', 'value')]
#     )
# def next_job_on_click(n_clicks, value):
#     changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
#     if 'btn-nclicks-1' in changed_id:
#         return(n_clicks)
#     else:
#         raise PreventUpdate        

#####################################
## COMPOSE ALL COMPONENTS INTO THE LAYOUT

app.layout = html.Div(
    children=[
        navbar,
        sticky_header_row,
        recency_badge_span,
        current_tabs,
        next_button,
        dd_value_store
        ],
        style={"margin":0}
    )

# app.layout = html.Div(
#     children=[
#         navbar,
#         sticky_header_row,
#         plot_div,
#         job_desc_output
#         ],
#         style={"margin":0}
#     )


#####################################
#####################################
## CALLBACKS

@app.callback(
    [dash.dependencies.Output('tab-1', 'label'),
    dash.dependencies.Output('tab-2', 'label'),
    dash.dependencies.Output('dd_value', 'data')],
    dash.dependencies.Input('job_dropdown', 'value'))
def set_tabs(value):
    if value is None:
        return ['Word Cloud', 'Statistics', value]
    else:
        return ['Job description', 'Extra info', value]
###############################

@app.callback([
    #dash.dependencies.Output('current_tabs', 'children'), ##TODO: tabs need more work to integrate
    dash.dependencies.Output('job_desc_output', 'children'),
    dash.dependencies.Output('job_title', 'children'),
    dash.dependencies.Output('job_keywords', 'children'),
    dash.dependencies.Output('job_url', 'href'),
    dash.dependencies.Output('linkedin_logo', 'style'),
    #dash.dependencies.Output('plot_div', 'children'),
    dash.dependencies.Output('total_jobs_badge', 'style'),
    dash.dependencies.Output("loading_output", "children"),
    dash.dependencies.Output("recency_span", 'children')
    ],
#[dash.dependencies.Input('job_dropdown', 'value')],
[dash.dependencies.Input('dd_value', 'data')],
[dash.dependencies.State('toggle_dropdown_sort', 'on'),
dash.dependencies.State('linkedin_logo', 'style'),
dash.dependencies.State('total_jobs_badge', 'style'),
dash.dependencies.State("job_dropdown", 'value')
]
)
#[dash.dependencies.Input('toggle_dropdown_sort', 'on')])
#####################################
@cache.memoize(timeout=TIMEOUT) #make a separate data query function
def update_output(dd_value, sort_toggle, logo_dict, total_jobs_badge, id):
    spinner_text = ""
    # if id is None: #doesn't work
    #     job_id = id
    # else:
    #     job_id = id + dd_value
    job_id = str(id) if id is not None else None
    if job_id is None:
        #return init_plot
        logo_dict |= dict(display="none")
        total_jobs_badge |= dict(display="initial")
        return [""]*4 + [logo_dict, total_jobs_badge, spinner_text, None]
        #raise PreventUpdate

    logo_dict |= dict(display="inline-block")
    total_jobs_badge |= dict(display="none")

    recency_status = recency_statuses[jobs[job_id]['url']]
    closed_msg = ""
    if type(recency_status) is list:
        recency_badge_id, closed_msg = recency_status
    else:
        recency_badge_id = recency_status
    recency_badge = [recency_badges.get(recency_badge_id), closed_msg]

    #title = html.Label([f"{jobs[id]['title']}", html.A(href=f"{jobs[id]['url']}")])

    return [
            #"***\n"+ \
            jobs[job_id]['description'],
            jobs[job_id]['title'],
            f"##### **Score:** {round(jobs[job_id]['score'],1)}",
            jobs[job_id]['url'],
            logo_dict,
            total_jobs_badge,
            spinner_text,
            recency_badge
            ]

########################################
    #return name_to_figure(fig_name)

# @app.callback([
#     dash.dependencies.Output(dd_value_store.data, 'style'),
#     ],
# [dash.dependencies.Input("dd_value", 'data')]
# #[dash.dependencies.State('job_url', 'href')],
# )
# def set_badge(data):
#     return dict(visible='block')

#####################################
## Load extras (e.g. CSS)

# Loading screen CSS
#app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"})
#####################################
## LAUNCH SERVER
import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger('my_logger')
handler = RotatingFileHandler('ttt.log', maxBytes=10000, backupCount=1)
logger.addHandler(handler)

app.server.logger.addHandler(handler)
app.run_server(debug=True)#, use_reloader=False)
#####################################