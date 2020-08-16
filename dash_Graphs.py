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


from fcn_UTILS import character_removal, dataframe_chooser, Mbox

## DASH ##

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from functools import lru_cache
...
@lru_cache(maxsize=32)
def get_config_file(*args):
    ...




def Dash_App(Daily_Interval_Data, Weekly_Interval_Data, Monthly_Sum): 
    """ file to create the nice sidebar dash app thingo"""


    ########## VARS ###############
    names = list(Daily_Interval_Data.columns) #get the names of the column 
    
    
    # # for i in range(0, len(Weekly_Interval_Data)): #iterate through each month for weekly data
    # #    weekly_dash_figure.append(Weekly_Interval_Data[i].iplot(kind = 'line', xTitle='Time', yTitle='kWh Consumption', title = 'Weekly Consumption', asFigure = True) ) #create a list of figures
    
    # chosen_month = 0


    # spreadsheet_under_consideration = 'THIS IS A PLACEHOLDER.xlsx'

    # Months = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December') #list of the months to access things later

    #### STEP 1: Set up the figures #### 
    # in order for dash to plot the graph, we need to pass the dataframe object to the `figure = [xxx]` argument 
    



    ####################### DASH GOES HERE - NEED TO WORK OUT HOW TO MAKE THIS A FUNCTION IN ANOTHER PY FILE ####################### #th
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] #styling sheets
    
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = html.Div([ #create the simple layout
        html.Img(src=app.get_asset_url('NEW_LOGO.jpg')), #display NEW LOGO
        html.P('Historical Energy Load Anaylsis Tool'), #quick graph
        dcc.Dropdown(id = 'Drop_Down_menu', #make selection menu
            options=[{'label':name, 'value':name} for name in names],
            value = names[0],#initial default selection upon loading 
            multi=False #do not allow multiple selections 
            ), 
        dcc.Graph(id='daily_graph'), #display daily graph
        dcc.Graph(id='weekly_graph'), #display weekly graph
    ])

    #callbacks to get user input - not going to lis this is magic and I don't truly understand how it works. But it does. 
    ## CALLBACK for daily graph ##
    @app.callback( 
        Output('daily_graph', 'figure'), 
        [Input('Drop_Down_menu', 'value')])
    def update_figure(selected_name):
        #filter the names 
        chosen_site = character_removal(selected_name) #this sanitises the chosen input into a standard string
        ### DYNAMICALLY CREATE DATAFRAME TO SHOW ALL MONTHS ###
        dataframe_to_plot = dataframe_chooser(Daily_Interval_Data, chosen_site) #dynamically create dataframes to plot 12x months on top of each other for the selected site
        try: 
            #create the figure to send to dash to plot
            fig = dataframe_to_plot.iplot(kind = 'line', xTitle='Time', yTitle='Consumption (kWh)', title = chosen_site, asFigure = True) 
        except KeyError: #https://github.com/santosjorge/cufflinks/issues/180 - although waiting 0.5s before calling the 2nd graph seems to aboid this
            Mbox('PLOT ERROR', 'Dash has encountered an error. Please select another site, and try again', 1)

        return fig
    ## CALLBACK for weekly graph ##
    @app.callback(
        Output('weekly_graph', 'figure'),
        [Input('Drop_Down_menu', 'value')])
    def update_figure1(selected_name):
        #filter the names 
        chosen_site = character_removal(selected_name) #this sanitises the chosen input into a standard string
        ### DYNAMICALLY CREATE DATAFRAME TO SHOW ALL MONTHS ###
        time.sleep(0.25) #mitigate an error where calling the plot function twice in a short amount of time means it does not plot the 2nd graph
        dataframe_to_plot = dataframe_chooser(Weekly_Interval_Data, chosen_site) #dynamically create dataframes to plot entire year of chosen 
        try: 
             #create the figure to send to dash to plot
            fig = dataframe_to_plot.iplot(kind = 'line', xTitle='Day and Time', yTitle='Consumption (kWh)', title = chosen_site, asFigure = True) 
        except KeyError: #https://github.com/santosjorge/cufflinks/issues/180 - although waiting 0.5s before calling this graph seems to avoid this
            Mbox('PLOT ERROR', 'Dash has encountered an error. Please select another site, and try again', 1)

        return fig


    webbrowser.open('http://127.0.0.1:8888/')  # open the DASH app in default webbrowser
    print('Starting Dash Server') #print to console, to for debugging/dev

    app.run_server(port=8888) #start the server. 

    return #nothing 
