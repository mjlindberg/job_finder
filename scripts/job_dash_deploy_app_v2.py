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
##external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']#[dbc.themes.BOOTSTRAP]
##local_stylesheets = ['assets/bWLwgP.css'] #manually edited body margins; needs to be in an "assets" folder in same dir; loaded automatically...?

app = dash.Dash(
    __name__,
    #external_stylesheets=external_stylesheets,
    assets_folder="assets",
    #external_stylesheets=[dbc.themes.BOOTSTRAP], #
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}, #scales for mobile devices
    ]
    )
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
        labelPosition="right",
        disabled = False if len(scores) > 0 else True
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
    "display": "inline-block",
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
        dbc.Col(job_dropdown, style={"width":"94%", "display":"inline-block", "padding":"0px", "clear":"both", "verticalAlign": "center", "margin-left":"10px", "margin-top":"25px"}),
        dbc.Col(html.Div(dd_sort_toggle, style = {"color":"white", "padding":"0px"}), style={"width":"5%", "display":"inline-block", "padding":"0px", "clear":"both","margin-left":"25px","margin-right":"-45px", "verticalAlign": "top","margin-top":"25px"})
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
    color="success", id="total_jobs_badge", disabled=False, style = {"verticalAlign":"top", "margin":0, "margin-left":"40px", "margin-top":"5px"}
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
                    html.H2(children='SWISS JOBS', style = {"color":"white", "fontStyle":"italic","fontWeight":800, "position":"relative","bottom":"5px"}),
                    style={"width":"auto", "display":"inline-block", "box-sizing":"border-box", "clear":"both", "margin-left":"25px", "margin-right":"35px"}#, align="left"
                    ),
                dbc.Col(dbc.Collapse(dropdown_bar, navbar = True),
                style={"width":"69%", "display":"inline-block", "box-sizing":"border-box", "clear":"both", "verticalAlign": "center", "margin-right":"-5px", "padding":"0px"}),
                # dbc.Col(
                #     job_dropdown, width = {"size":8, "order":1}
                #     ),
                # dbc.Col(
                #     html.Div(dd_sort_toggle, style = {"color":"white"}), width = "auto"
                #     )
            ],
            no_gutters = True,
            align = "center",
            style = {"margin":"0", "width":"100%"}
        ),
        
    ],
    sticky="top",
    style = {"backgroundColor":"#4B0082"}
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
## COMPOSE ALL COMPONENTS INTO THE LAYOUT
app.layout = html.Div(
    children=[
        navbar,
        sticky_header_row,
        plot_div,
        job_desc_output
        ],
        style={"margin":0, "margin-top":"-5px"}
    )

#####################################
#####################################
## CALLBACKS

@app.callback([
    dash.dependencies.Output('job_desc_output', 'children'),
    dash.dependencies.Output('job_title', 'children'),
    dash.dependencies.Output('job_keywords', 'children'),
    dash.dependencies.Output('job_url', 'href'),
    dash.dependencies.Output('linkedin_logo', 'style'),
    dash.dependencies.Output('plot_div', 'children'),
    dash.dependencies.Output('total_jobs_badge', 'style'),
    dash.dependencies.Output("loading_output", "children")
    ],
[dash.dependencies.Input('job_dropdown', 'value')],
[dash.dependencies.State('toggle_dropdown_sort', 'on'),
dash.dependencies.State('linkedin_logo', 'style'),
dash.dependencies.State('total_jobs_badge', 'style')])
#[dash.dependencies.Input('toggle_dropdown_sort', 'on')])
#####################################
@cache.memoize(timeout=TIMEOUT) #make a separate data query function
def update_output(id, sort_toggle, logo_dict, total_jobs_badge):
    spinner_text = ""

    if id is None:
        #return init_plot
        logo_dict |= dict(display="none")
        total_jobs_badge |= dict(display="initial")
        return [""]*4 + [logo_dict, init_plot, total_jobs_badge, spinner_text]
        raise PreventUpdate

    logo_dict |= dict(display="inline-block")
    total_jobs_badge |= dict(display="none")

    #title = html.Label([f"{jobs[id].title}", html.A(href=f"{jobs[id].url}")])
    if sort_toggle is False:
        return [
            #"***\n"+ \
            unsorted_jobs[id].description,
            unsorted_jobs[id].title,
            f"##### **Score:** {round(unsorted_jobs[id].score,1)}",
            unsorted_jobs[id].url,
            logo_dict,
            "",
            total_jobs_badge,
            spinner_text
            ]
    elif sort_toggle is True:
        return [
            #"***\n"+ \
            jobs[id].description,
            jobs[id].title,
            f"##### **Score:** {round(jobs[id].score,1)}",
            jobs[id].url,
            logo_dict,
            "",
            total_jobs_badge,
            spinner_text
            ]
    #return name_to_figure(fig_name)

#####################################
## Load extras (e.g. CSS)

# Loading screen CSS
#app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"})
#####################################
## LAUNCH SERVER
app.run_server(debug=False)

#####################################