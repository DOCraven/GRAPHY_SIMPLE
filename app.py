### libraries

import pandas as pd
import datetime as dt
import numpy as np
import os
import matplotlib.pyplot as plt
import datetime as dt
import webbrowser
from calendar import day_name
import ctypes  # An included library with Python install.
import time

## USER DEFINED FUNCTIONS ##
from fcn_UTILS import character_removal, dataframe_chooser, Mbox

## DASH ##

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

def dash_solar_plotter(df_to_plot): 
    """sum and plot the total solar consumption for each month"""
    ### VARS 
    chosen_site = 'Excess Solar Generation (Total)', #only plot the excess solar
    ### STEP 1 - Load the DF
    dataframe_to_plot = dataframe_chooser(df_to_plot, chosen_site), #dynamically create dataframes to plot 12x months on top of each other for the selected site 
    ## STEP 2 - SUM the dataframe 
    summed_dataframe = dataframe_to_plot[0].sum(axis = 0) #sum along rows
    try: #create the figure to send to dash to plot
        figure = summed_dataframe.iplot(kind = 'bar', xTitle='Month', yTitle='Total Consumption (kWh)', title = 'SOLAR TEST', asFigure = True),
    except KeyError: #https://github.com/santosjorge/cufflinks/issues/180 - although waiting 0.5s before calling the 2nd graph seems to aboid this
        Mbox('PLOT ERROR', 'Dash has encountered an error. Please select another site, and try again', 1)
    
    return figure[0] #it somehow makes itself a 1x1 list, and thus to return just the image one needs to index it. NFI why. 



def Dash_App(Daily_Interval_Data, Weekly_Interval_Data, Monthly_Sum, Solar_Exists = False): 
    """ file to create the nice sidebar dash app thingo"""


    ########## VARS ###############
    names = list(Daily_Interval_Data[0].columns) #get the names of the column, assuming every name is the same across each dataframe in the list
    
    if Solar_Exists: #only make this if the solar data has been uploaded
        solar_figure = dash_solar_plotter(Daily_Interval_Data) #make fancy figure 

    ####################### DASH GOES HERE ####################### 
    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

    # the style arguments for the sidebar. We use position:fixed and a fixed width
    SIDEBAR_STYLE = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "16rem",
        "padding": "2rem 1rem",
        "background-color": "#f8f9fa",
    }

    # the styles for the main content position it to the right of the sidebar and
    # add some padding.
    CONTENT_STYLE = {
        "margin-left": "18rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem",
    }

    sidebar = html.Div(
        [
            html.H2("NEW Graphy", className="display-4"),
            html.Hr(),
            html.P(
                "A historical load data analysis tool", className="lead"
                ),
            dbc.Nav(
                [
                    dbc.NavLink("Site Graphs", href="/page-1", id="page-1-link"),
                    dbc.NavLink("Load Shifting Site Graphs", href="/page-2", id="page-2-link"),
                    dbc.NavLink("Excess Solar Hours", href="/page-3", id="page-3-link"),
                    dbc.NavLink("About", href="/page-99", id="page-99-link"),
                ],
                vertical=True,
                pills=True,
                ),
            ],
        style=SIDEBAR_STYLE,
    )

    content = html.Div(id="page-content", style=CONTENT_STYLE)

    app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


    # this callback uses the current pathname to set the active state of the
    # corresponding nav link to true, allowing users to tell see page they are on

    #### CALLBACKS ####
    ## CALLBACK FOR CHANGING TABS ##
    @app.callback(
        [Output(f"page-{i}-link", "active") for i in range(1, 5)],
        [Input("url", "pathname")],
    )
    def toggle_active_links(pathname):
        if pathname == "/":
            # Treat page 1 as the homepage / index
            return True, False, False
        return [pathname == f"/page-{i}" for i in range(1, 5)]

    ### CALLBACK FOR TAB - ACTUAL LAYOUT IN TABS GOES HERE ###
    @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
    def render_page_content(pathname):
        if pathname in ["/", "/page-1"]: #solar graphs
            return html.Div([
                html.P('Historical Energy Load Anaylsis Tool'), #quick graph
                dcc.Dropdown(id = 'Drop_Down_menu', #make selection menu
                    options=[{'label':name, 'value':name} for name in names],
                    value = names[0],#initial default selection upon loading 
                    multi=False #do not allow multiple selections 
                    ), 
                dcc.Graph(id='daily_graph'), #display daily graph
                dcc.Graph(id='weekly_graph'), #display weekly graph

            ])

        elif pathname == "/page-2": #load shifting 
            return html.Div([
                dcc.Slider(
                    id='my-slider',
                    min=0,
                    max=50,
                    step=1,
                    value=0,
                ),
                html.Div(id='slider-output-container')
                ])

        elif pathname == "/page-3": #Solar Total Graphing
            if Solar_Exists: ## ie, user uploaded a solar file, so plot the nice and pretty graphs
                return html.Div([
                    html.P("Solar Data Uploaded"),
                    dcc.Graph(id='Daily Excess Summmed Solar', figure = solar_figure), #display sum of all solar graph

                ]) 
            else: 
                return html.P("No Solar Data Uploaded")


        elif pathname == "/page-99": #readme
            return html.Div([ #README goes here - manually copied from github `README.MD`
                dcc.Markdown('''
                    # RMIT CAPSTONE PROJECT 
                    ## NORTH EAST WATER

                    ## Context
                    A program to assist in analysing NEW's industrial energy consumption. Takes two  `xls` files of interval data and solar forecast data, and returns a number of different average load profiles. 

                    ## Scope

                    Contains a GUI program that will:

                    - Code to manipulate data into DataFrames.
                    - Code to create some time series average
                    - Code to plot the data nicely.

                    This program includes NE Water data from External Sites and within WWTP. 


                    ## VERSION 

                    Version 1.0 

                    Last Updated: 17AUG20


                    ## OVERVIEW
                    1. This program will generate a GUI to load interval data, and displays the results via `DASH` in the default webbrowser. 

                    1.  Using `DASH`, the daily and weekly average load profiles for WWTP and external NE Water loads are plotted. The user can select a specific site for anaylsis. 


                    ## How to use

                    1. Clone the `master` branch. 
                    1.   `git clone https://github.com/DOCraven/GRAPHY_SIMPLE`.
                    1. Install Dependencies (if required - `PIP INSTALL [library]`).
                    1. In Visual Studio Code, open the folder that `Graphy.py` is located in via `CTRL + K + O`.
                    1. Ensure the `xls` file is in the root folder (ie, same as `Graphy.py`).
                    1. Run `Graphy.py`. 
                    -  either within your IDE (in VS CODE, green triangle in Upper RH corner).
                    -  or via the terminal using  `python graphy.py`.
                    1. Use the included GUI landing page to select the various options.


                    ## Contributing 
                    1.  Clone the master branch via `git clone https://github.com/DOCraven/Graphy.git`.
                    1.  Create a new branch either via `git branch [branch-name]` or via the inbuilt GitLens extension (bottom LH corner).
                    1.  Contribute code.
                    1.  commit code as necessary via `git commit -m "Message"` or via GitLens Extension.
                    1.  Push code to new branch via `git push origin [your branch]` or via GitLens Extension (bottom LH Corner).
                    1.  Request code review (if necessary).
                    1.  Merge with master when approved.

                    ## Known Issues


                    - This repo does not place nice with Anaconda. Please use this with a vanilla Python 3.8.x installation.
                    - There is minimal error checking involved. 
                    - `WWTP` data is lacking, and thus plotting it will not yield as many results and `EXTERNAL` data. 
                    - No solar data appended to `WWTP` plotting. 
                    - Solar data is currently placeholder data, and not site specific data. 


                    ## Dependencies

                    A `requirements.txt` fill will accompany this repo. 

                    `pip install requirements.txt` will install all dependencies required for this program


                ''') 
            ])
        # If the user tries to reach a different page, return a 404 message
        return dbc.Jumbotron(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognised..."),
            ]
        )

    ### CALLBACK FOR DAILY GRAPH ###
    @app.callback( 
        Output('daily_graph', 'figure'), 
        [Input('Drop_Down_menu', 'value')])
    def update_daily_graph(selected_name):
        #filter the names 
        chosen_site = character_removal(selected_name) #this sanitises the chosen input into a standard string
        ### DYNAMICALLY CREATE DATAFRAME TO SHOW ALL MONTHS ###
        dataframe_to_plot = dataframe_chooser(Daily_Interval_Data, chosen_site) #dynamically create dataframes to plot 12x months on top of each other for the selected site
        try: #create the figure to send to dash to plot
            fig = dataframe_to_plot.iplot(kind = 'line', xTitle='Time', yTitle='Consumption (kWh)', title = chosen_site, asFigure = True) 
        except KeyError: #https://github.com/santosjorge/cufflinks/issues/180 - although waiting 0.5s before calling the 2nd graph seems to aboid this
            Mbox('PLOT ERROR', 'Dash has encountered an error. Please select another site, and try again', 1)

        return fig


    ### CALLBACK FOR WEEKLY GRAPH ###
    @app.callback(
        Output('weekly_graph', 'figure'),
        [Input('Drop_Down_menu', 'value')])
    def update_weekly_graph(selected_name):
        #filter the names 
        chosen_site = character_removal(selected_name) #this sanitises the chosen input into a standard string
        ### DYNAMICALLY CREATE DATAFRAME TO SHOW ALL MONTHS ###
        time.sleep(0.25) #mitigate an error where calling the plot function twice in a short amount of time means it does not plot the 2nd graph
        dataframe_to_plot = dataframe_chooser(Weekly_Interval_Data, chosen_site) #dynamically create dataframes to plot entire year of chosen 
        try: #create the figure to send to dash to plot
            fig = dataframe_to_plot.iplot(kind = 'line', xTitle='Day and Time', yTitle='Consumption (kWh)', title = chosen_site, asFigure = True) 
        except KeyError: #https://github.com/santosjorge/cufflinks/issues/180 - although waiting 0.25s before calling this graph seems to avoid this
            Mbox('PLOT ERROR', 'Dash has encountered an error. Please select another site, and try again', 1)

        return fig
    
    ### CALLBACK FOR SLIDER ###
    @app.callback(
    dash.dependencies.Output('slider-output-container', 'children'),
    [dash.dependencies.Input('my-slider', 'value')])
    def update_output(value):
        return 'You have selected "{}"'.format(value)

    webbrowser.open('http://127.0.0.1:8888/')  # open the DASH app in default webbrowser
    print('Starting Dash Server') #print to console, to for debugging/dev

    app.run_server(port=8888) #start the server. 

    return #nothing 
