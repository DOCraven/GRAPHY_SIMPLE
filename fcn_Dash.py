### libraries

import pandas as pd
import datetime as dt
# import cufflinks as cf
import numpy as np
import os
import matplotlib.pyplot as plt
import datetime as dt
from calendar import day_name



## DASH ##

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output






def Dash_App(Weekly_Interval_Data, Daily_Interval_Data, Monthly_sum): 
    """ file to create the nice sidebar dash app thingo"""


    ########## VARS ###############
    weekly_dash_figure = [] #empty list to populate weekly figures to pass to dash
    daily_dash_figure = [] #empty list to populate weekly figures to pass to dash
    monthly_total_consumption_figure = [] #empty list to populate with monthly consumption data
    # weekly_total_consumption_figure = [] #empty list to populate with weekly consumption data
    # daily_total_consumption_figure = [] #empty list to populate with daily consumption data

    Months = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December') #list of the months to access things later

    #### STEP 1: Set up the figures #### 
    # in order for dash to plot the graph, we need to pass the dataframe object to the `figure = [xxx]` argument 
    for i in range(0, len(Weekly_Interval_Data)): #iterate through each month for weekly data
        weekly_dash_figure.append(Weekly_Interval_Data[i].iplot(kind = 'line', xTitle='Time', yTitle='kWh Consumption', title = 'Weekly Consumption', asFigure = True) ) #create a list of figures

    for i in range(0, len(Daily_Interval_Data)): #iterate through each month for daily data
        daily_dash_figure.append(Daily_Interval_Data[i].iplot(kind = 'line', xTitle='Time', yTitle='kWh Consumption', title = 'Daily Consumption',  asFigure = True)) #create a list of figures) 
    
    for i in range(0, len(Monthly_sum)): #iterate through each month for daily data
        monthly_total_consumption_figure.append(Monthly_sum[i].iplot(kind = 'bar', xTitle='NEW Site', yTitle='Total kWh Consumption', asFigure = True) ) #create a list of figures

    ####################### DASH GOES HERE - NEED TO WORK OUT HOW TO MAKE THIS A FUNCTION IN ANOTHER PY FILE #######################

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
                "An online webapp to visualize historical load data", className="lead"
            ),
            dbc.Nav(
                [
                    dbc.NavLink("January", href="/page-0", id="page-0-link"),
                    dbc.NavLink("February", href="/page-1", id="page-1-link"),
                    dbc.NavLink("March", href="/page-2", id="page-2-link"),
                    dbc.NavLink("April", href="/page-3", id="page-3-link"),
                    dbc.NavLink("May", href="/page-4", id="page-4-link"),
                    dbc.NavLink("June", href="/page-5", id="page-5-link"),
                    dbc.NavLink("July", href="/page-6", id="page-6-link"),
                    dbc.NavLink("August", href="/page-7", id="page-7-link"),
                    dbc.NavLink("September", href="/page-8", id="page-8-link"),
                    dbc.NavLink("October", href="/page-9", id="page-9-link"),
                    dbc.NavLink("November", href="/page-10", id="page-10-link"),
                    dbc.NavLink("December", href="/page-11", id="page-11-link"),
                    dbc.NavLink("About", href="/page-12", id="page-12-link"),
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
    @app.callback(
        [Output(f"page-{i}-link", "active") for i in range(0, 13)],
        [Input("url", "pathname")],
    )
    def toggle_active_links(pathname):
        if pathname == "/":
            # Treat page 1 as the homepage / index
            return True, False, False
        return [pathname == f"/page-{i}" for i in range(0, 13)]


    @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
    def render_page_content(pathname):
        if pathname in ["/", "/page-0"]:
            chosen_month = 0 #to choose different months in the list 

            return html.Div([ ## ALL COMPONENTS OF THE PAGE NEED TO BE INSIDE THIS
                ## PLOT THE WEEKLY CONSUMPTION
                dcc.Graph(id= Months[chosen_month] + 'Weekly Consumption' ,figure=weekly_dash_figure[chosen_month]),
                ## PLOT THE DAILY CONSUMPTION
                dcc.Graph(id=Months[chosen_month] + 'Daily Consumption' ,figure=daily_dash_figure[chosen_month]),
                ## PLOT THE TOTAL CONSUMPTION
                html.H3('\nTotal Summation'), 
                dcc.Graph(id= Months[chosen_month] + 'Total Monthly Consumption' , figure=monthly_total_consumption_figure[chosen_month]),
            ])
        elif pathname == "/page-1":
            chosen_month = 1 #to choose different months in the list 

            return html.Div([ ## ALL COMPONENTS OF THE PAGE NEED TO BE INSIDE THIS
                ## PLOT THE WEEKLY CONSUMPTION
                dcc.Graph(id= Months[chosen_month] + 'Weekly Consumption' ,figure=weekly_dash_figure[chosen_month]),
                ## PLOT THE DAILY CONSUMPTION
                dcc.Graph(id=Months[chosen_month] + 'Daily Consumption' ,figure=daily_dash_figure[chosen_month]),
                ## PLOT THE TOTAL CONSUMPTION
                html.H3('\nTotal Summation'), 
                dcc.Graph(id= Months[chosen_month] + 'Total Monthly Consumption' , figure=monthly_total_consumption_figure[chosen_month]),
            ])
        elif pathname == "/page-2":
            chosen_month = 2 #to choose different months in the list 

            return html.Div([ ## ALL COMPONENTS OF THE PAGE NEED TO BE INSIDE THIS
                ## PLOT THE WEEKLY CONSUMPTION
                dcc.Graph(id= Months[chosen_month] + 'Weekly Consumption' ,figure=weekly_dash_figure[chosen_month]),
                ## PLOT THE DAILY CONSUMPTION
                dcc.Graph(id=Months[chosen_month] + 'Daily Consumption' ,figure=daily_dash_figure[chosen_month]),
                ## PLOT THE TOTAL CONSUMPTION
                html.H3('\nTotal Summation'), 
                dcc.Graph(id= Months[chosen_month] + 'Total Monthly Consumption' , figure=monthly_total_consumption_figure[chosen_month]),
            ])
        elif pathname == "/page-3":
            chosen_month = 3 #to choose different months in the list 

            return html.Div([ ## ALL COMPONENTS OF THE PAGE NEED TO BE INSIDE THIS
                ## PLOT THE WEEKLY CONSUMPTION
                dcc.Graph(id= Months[chosen_month] + 'Weekly Consumption' ,figure=weekly_dash_figure[chosen_month]),
                ## PLOT THE DAILY CONSUMPTION
                dcc.Graph(id=Months[chosen_month] + 'Daily Consumption' ,figure=daily_dash_figure[chosen_month]),
                ## PLOT THE TOTAL CONSUMPTION
                html.H3('\nTotal Summation'), 
                dcc.Graph(id= Months[chosen_month] + 'Total Monthly Consumption' , figure=monthly_total_consumption_figure[chosen_month]),
            ])
        elif pathname == "/page-4":
            chosen_month = 4 #to choose different months in the list 

            return html.Div([ ## ALL COMPONENTS OF THE PAGE NEED TO BE INSIDE THIS
                ## PLOT THE WEEKLY CONSUMPTION
                dcc.Graph(id= Months[chosen_month] + 'Weekly Consumption' ,figure=weekly_dash_figure[chosen_month]),
                ## PLOT THE DAILY CONSUMPTION
                dcc.Graph(id=Months[chosen_month] + 'Daily Consumption' ,figure=daily_dash_figure[chosen_month]),
                ## PLOT THE TOTAL CONSUMPTION
                html.H3('\nTotal Summation'), 
                dcc.Graph(id= Months[chosen_month] + 'Total Monthly Consumption' , figure=monthly_total_consumption_figure[chosen_month]),
            ])
        elif pathname == "/page-5":
            chosen_month = 5 #to choose different months in the list 

            return html.Div([ ## ALL COMPONENTS OF THE PAGE NEED TO BE INSIDE THIS
                ## PLOT THE WEEKLY CONSUMPTION
                dcc.Graph(id= Months[chosen_month] + 'Weekly Consumption' ,figure=weekly_dash_figure[chosen_month]),
                ## PLOT THE DAILY CONSUMPTION
                dcc.Graph(id=Months[chosen_month] + 'Daily Consumption' ,figure=daily_dash_figure[chosen_month]),
                ## PLOT THE TOTAL CONSUMPTION
                html.H3('\nTotal Summation'), 
                dcc.Graph(id= Months[chosen_month] + 'Total Monthly Consumption' , figure=monthly_total_consumption_figure[chosen_month]),
            ])
        elif pathname == "/page-6":
            chosen_month = 6 #to choose different months in the list 

            return html.Div([ ## ALL COMPONENTS OF THE PAGE NEED TO BE INSIDE THIS
                ## PLOT THE WEEKLY CONSUMPTION
                dcc.Graph(id= Months[chosen_month] + 'Weekly Consumption' ,figure=weekly_dash_figure[chosen_month]),
                ## PLOT THE DAILY CONSUMPTION
                dcc.Graph(id=Months[chosen_month] + 'Daily Consumption' ,figure=daily_dash_figure[chosen_month]),
                ## PLOT THE TOTAL CONSUMPTION
                html.H3('\nTotal Summation'), 
                dcc.Graph(id= Months[chosen_month] + 'Total Monthly Consumption' , figure=monthly_total_consumption_figure[chosen_month]),
            ])
        elif pathname == "/page-7":
            chosen_month = 7 #to choose different months in the list 

            return html.Div([ ## ALL COMPONENTS OF THE PAGE NEED TO BE INSIDE THIS
                ## PLOT THE WEEKLY CONSUMPTION
                dcc.Graph(id= Months[chosen_month] + 'Weekly Consumption' ,figure=weekly_dash_figure[chosen_month]),
                ## PLOT THE DAILY CONSUMPTION
                dcc.Graph(id=Months[chosen_month] + 'Daily Consumption' ,figure=daily_dash_figure[chosen_month]),
                ## PLOT THE TOTAL CONSUMPTION
                html.H3('\nTotal Summation'), 
                dcc.Graph(id= Months[chosen_month] + 'Total Monthly Consumption' , figure=monthly_total_consumption_figure[chosen_month]),
            ])
        elif pathname == "/page-8":
            chosen_month = 8 #to choose different months in the list 

            return html.Div([ ## ALL COMPONENTS OF THE PAGE NEED TO BE INSIDE THIS
                ## PLOT THE WEEKLY CONSUMPTION
                dcc.Graph(id= Months[chosen_month] + 'Weekly Consumption' ,figure=weekly_dash_figure[chosen_month]),
                ## PLOT THE DAILY CONSUMPTION
                dcc.Graph(id=Months[chosen_month] + 'Daily Consumption' ,figure=daily_dash_figure[chosen_month]),
                ## PLOT THE TOTAL CONSUMPTION
                html.H3('\nTotal Summation'), 
                dcc.Graph(id= Months[chosen_month] + 'Total Monthly Consumption' , figure=monthly_total_consumption_figure[chosen_month]),
            ])
        elif pathname == "/page-9":
            chosen_month = 9 #to choose different months in the list 

            return html.Div([ ## ALL COMPONENTS OF THE PAGE NEED TO BE INSIDE THIS
                ## PLOT THE WEEKLY CONSUMPTION
                dcc.Graph(id= Months[chosen_month] + 'Weekly Consumption' ,figure=weekly_dash_figure[chosen_month]),
                ## PLOT THE DAILY CONSUMPTION
                dcc.Graph(id=Months[chosen_month] + 'Daily Consumption' ,figure=daily_dash_figure[chosen_month]),
                ## PLOT THE TOTAL CONSUMPTION
                html.H3('\nTotal Summation'), 
                dcc.Graph(id= Months[chosen_month] + 'Total Monthly Consumption' , figure=monthly_total_consumption_figure[chosen_month]),
            ])
        elif pathname == "/page-10":
            chosen_month = 10 #to choose different months in the list 

            return html.Div([ ## ALL COMPONENTS OF THE PAGE NEED TO BE INSIDE THIS
                ## PLOT THE WEEKLY CONSUMPTION
                dcc.Graph(id= Months[chosen_month] + 'Weekly Consumption' ,figure=weekly_dash_figure[chosen_month]),
                ## PLOT THE DAILY CONSUMPTION
                dcc.Graph(id=Months[chosen_month] + 'Daily Consumption' ,figure=daily_dash_figure[chosen_month]),
                ## PLOT THE TOTAL CONSUMPTION
                html.H3('\nTotal Summation'), 
                dcc.Graph(id= Months[chosen_month] + 'Total Monthly Consumption' , figure=monthly_total_consumption_figure[chosen_month]),
            ])
        elif pathname == "/page-11":
            chosen_month = 11 #to choose different months in the list 

            return html.Div([ ## ALL COMPONENTS OF THE PAGE NEED TO BE INSIDE THIS
                ## PLOT THE WEEKLY CONSUMPTION
                dcc.Graph(id= Months[chosen_month] + 'Weekly Consumption' ,figure=weekly_dash_figure[chosen_month]),
                ## PLOT THE DAILY CONSUMPTION
                dcc.Graph(id=Months[chosen_month] + 'Daily Consumption' ,figure=daily_dash_figure[chosen_month]),
                ## PLOT THE TOTAL CONSUMPTION
                html.H3('\nTotal Summation'), 
                dcc.Graph(id= Months[chosen_month] + 'Total Monthly Consumption' , figure=monthly_total_consumption_figure[chosen_month]),
            ])
        
        
        elif pathname == "/page-12":
            return html.P("About will go here later!")
        # If the user tries to reach a different page, return a 404 message
        return dbc.Jumbotron(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognised..."),
            ]
        )

    
    print('Starting Dash Server')
    app.run_server(port=8888)
        

    return #nothing 
