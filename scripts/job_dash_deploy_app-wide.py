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

from scrape_swiss_jobs import JobPosting

################ INITIALIZE ###############
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']#[dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#app = dash.Dash()

########
from numpy import percentile, float64 as f64
from itertools import compress

percentiles = percentile(scores, range(0, 100, 25), interpolation = 'midpoint')

bound1 = len(list(compress(scores,list(compress(scores < percentiles[1], scores >= percentiles[0])))))
bound2 = len(list(compress(scores,list(compress(scores < percentiles[2], scores >= percentiles[1])))))
bound3 = len(list(compress(scores,list(compress(scores <= percentiles[3], scores >= percentiles[2])))))

#'annotations':f"Total # of jobs: {len(jobs)}"

init_plot = dcc.Graph(
        id='plot',
        figure=go.Figure({
            'data': [
                {'x': ["Lower", "Mid", "Upper"], 'y': [bound1, bound2, bound3], 'type': 'bar', 'name': 'Percentile job scores'},
                {'x': ["Lower", "Mid", "Upper"], 'y': [
                    sum(scores < f64(0)),
                    sum(list(compress((scores > f64(-10)),(scores < f64(1))))),
                    sum(scores >= f64(1))
                    ],
                    'type': 'bar', 'name': 'Extremes'},
            ],
            'layout': {
                'title': 'Percentiles of scoring'
            }#,
            #'edits': {
            #    'annotationText':f"Total # of jobs: {len(jobs)}"
           # }
        })
    )

##########################################################################
### ADD DATA CACHING
from flask_caching import Cache

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})
TIMEOUT = 60

##########################################################
### TOGGLE - sort dropdown by score or not
dd_sort_toggle = daq.BooleanSwitch(
        id='toggle_dropdown_sort',
        on=True,
        color="#9B51E0",
        label="Sort",
        labelPosition="bottom"
    )
    
job_names = [(jobs[job].title, job) for job in range(len(jobs)-1) if jobs[job].language == "en"]

#scores = [jobs[job].score for job in range(len(jobs)-1) if jobs[job].language == "en"]
unsorted_jobs = list(reversed(sorted(jobs, key = lambda x:x.id)))
unsorted_job_names = [(unsorted_jobs[job].title, job) for job in range(len(unsorted_jobs)-1) if unsorted_jobs[job].language == "en"]
unsorted_scores = [unsorted_jobs[job].score for job in range(len(unsorted_jobs)-1) if unsorted_jobs[job].language == "en"]

sorted_dd = [{'label': f"{x[1]+1}. "+x[0], 'value': x[1]} for x in job_names]
unsorted_dd = [{'label': f"{x[1]+1}. "+x[0], 'value': x[1]} for x in unsorted_job_names]

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
        options=[{'label': f"{x[1]+1}. "+x[0], 'value': x[1]} for x in job_names],
        value=None,
        multi=False, ##TODO: make multi-selectable
        optionHeight=60
    )],
    #style={"width":"50%"}
    )

# job_desc_area =  dcc.Textarea(

#         id='job_desc_area',
#         value='Textarea content initialized\nwith multiple lines of text',
#         style={'width': '100%', 'height': 300},
#     )

#job_desc_output = html.Div(id='job_desc_output', style={'whiteSpace': 'pre-line'})
job_desc_output = dcc.Markdown(id='job_desc_output', style={'whiteSpace': 'pre-line'})

#job_title = html.H2(id='job_title')
job_title = html.H3(id="job_title")
#job_keywords = html.H5(id='job_keywords', style={
job_keywords = dcc.Markdown(id='job_keywords', style={
    "display": "inline-block",
    "verticalAlign": "center",
    "width":"50%",
    #"box-sizing":"border-box",
    "margin-left": "40px"
    }
    )
#job_url = html.Link(id='job_url')


############
html.Div()

dropdown_bar = dbc.Row(
    [
        dbc.Col(job_dropdown, style={"width":"94%", "display":"inline-block", "padding":"0px", "clear":"both", "verticalAlign": "center"}),
        dbc.Col(html.Div(dd_sort_toggle, style = {"color":"white", "padding":"0px"}), style={"width":"5%", "display":"inline-block", "padding":"0px", "clear":"both","margin-left":"25px","verticalAlign": "center"})
    ],
    no_gutters = True,
    className = "ml-auto flex-nowrap mt-3 mt-md-0",
    align = "right",
    style={"width":"100%"}
)

app.layout = html.Div(children=[
    dbc.Navbar(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.H2(children='Swiss Jobs', style = {"color":"white"}), style={"width":"auto", "display":"inline-block", "box-sizing":"border-box", "clear":"both", "margin-right":"25px"}#, align="left"
                    ),
                dbc.Col(dbc.Collapse(dropdown_bar, navbar = True), style={"width":"79%", "display":"inline-block", "box-sizing":"border-box", "clear":"both", "verticalAlign": "center", "margin-right":"-2px"}),
                # dbc.Col(
                #     job_dropdown, width = {"size":8, "order":1}
                #     ),
                # dbc.Col(
                #     html.Div(dd_sort_toggle, style = {"color":"white"}), width = "auto"
                #     )
            ],
            no_gutters = True,
            align = "center",
            #style = {"display":"inline-block"}
        ),
        
    ],
    sticky="top",
    style = {"backgroundColor":"#4B0082"}
),
dbc.Row(
    [
        job_title,
        html.Div(children=[dcc.Link(dbc.Button(children=[
            html.Img(
                src='https://cdn.iconscout.com/icon/free/png-256/linkedin-42-151143.png',
                style={'height':'80%', "verticalAlign":"top", "margin-left":"-25px", "margin-right":"5px", "margin-top":"2px"}
            ),
            "Go to LinkedIn page"
            ],
            color="primary",
            className="mr-1",
            id="button",
            style={"display":"none", "backgroundColor":"#0072b1", "color":"white"}
            ),
            id='job_url',
            href = "javascript:void(0);"),
            job_keywords
            ],
            style={
                "display": "inline-block",
                "width": "50%",
                "margin-right": "20px",
                "verticalAlign": "top"
                }
            )
        ],
        style = {"position": "sticky", 'backgroundColor':'#E6E6FA', 'top':0, 'height':'100%', "paddingTop":"10px","paddingBottom":"10px"},
        no_gutters = True
        ),#, "top": 0}),
        html.Div(id="plot_div", children = init_plot),
        job_desc_output
        ]
        )



@app.callback([
    dash.dependencies.Output('job_desc_output', 'children'),
    dash.dependencies.Output('job_title', 'children'),
    dash.dependencies.Output('job_keywords', 'children'),
    dash.dependencies.Output('job_url', 'href'),
    dash.dependencies.Output('button', 'style'),
    dash.dependencies.Output('plot_div', 'children')
    #dash.dependencies.Output('job_url', 'children')
    ],
[dash.dependencies.Input('job_dropdown', 'value')],
[dash.dependencies.State('toggle_dropdown_sort', 'on')])
#[dash.dependencies.Input('toggle_dropdown_sort', 'on')])
@cache.memoize(timeout=TIMEOUT) #make a separate data query function
def update_output(id, sort_toggle):
    if id is None:
        #return init_plot
        return [""]*4 + [dict(display="none"), init_plot]
        raise PreventUpdate

    #title = html.Label([f"{jobs[id].title}", html.A(href=f"{jobs[id].url}")])
    if sort_toggle is False:
        return [
            #"***\n"+ \
            unsorted_jobs[id].description,
            unsorted_jobs[id].title,
            f"##### **Score:** {round(unsorted_jobs[id].score,1)}",
            unsorted_jobs[id].url,
            dict(backgroundColor="#0072b1", color="white"),
            ""
            ]
    elif sort_toggle is True:
        return [
            #"***\n"+ \
            jobs[id].description,
            jobs[id].title,
            f"##### **Score:** {round(jobs[id].score,1)}",
            jobs[id].url,
            dict(backgroundColor="#0072b1", color="white"),
            ""
            ]
    #return name_to_figure(fig_name)

app.run_server(debug=False)