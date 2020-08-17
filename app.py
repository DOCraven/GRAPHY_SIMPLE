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


def Dash_App(Daily_Interval_Data, Weekly_Interval_Data, Monthly_Sum): 
    """ file to create the nice sidebar dash app thingo"""


    ########## VARS ###############
    names = list(Daily_Interval_Data[0].columns) #get the names of the column, assuming every name is the same across each dataframe in the list
    
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
                    dbc.NavLink("Excess Solar Hours", href="/page-2", id="page-2-link"),
                    dbc.NavLink("About", href="/page-3", id="page-3-link"),
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
    @app.callback(
        [Output(f"page-{i}-link", "active") for i in range(1, 4)],
        [Input("url", "pathname")],
    )
    def toggle_active_links(pathname):
        if pathname == "/":
            # Treat page 1 as the homepage / index
            return True, False, False
        return [pathname == f"/page-{i}" for i in range(1, 4)]

    ### CALLBACK FOR TAB - ACTUAL LAYOUT GOES HERE ###
    @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
    def render_page_content(pathname):
        if pathname in ["/", "/page-1"]:
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
        elif pathname == "/page-2":
            return html.P("Excess Solar Generation hours")
        elif pathname == "/page-3":
            return html.P("README.MD goes here")
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


    webbrowser.open('http://127.0.0.1:8888/')  # open the DASH app in default webbrowser
    print('Starting Dash Server') #print to console, to for debugging/dev

    app.run_server(port=8888) #start the server. 

    return #nothing 
