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
    weekly_dash_figure = [] #empty list to populate weekly figures to pass to dash
    daily_dash_figure = [] #empty list to populate weekly figures to pass to dash
    monthly_total_consumption_figure = [] #empty list to populate with monthly consumption data
    # weekly_total_consumption_figure = [] #empty list to populate with weekly consumption data
    # daily_total_consumption_figure = [] #empty list to populate with daily consumption data
   
    ### SCRATCH ####
    test_df = Daily_Interval_Data[0] #split DF to a single one to make it easier to work with 
    names = list(test_df.columns) #get the names of the column 
    
    # for i in range(0, len(Weekly_Interval_Data)): #iterate through each month for weekly data
    #    weekly_dash_figure.append(Weekly_Interval_Data[i].iplot(kind = 'line', xTitle='Time', yTitle='kWh Consumption', title = 'Weekly Consumption', asFigure = True) ) #create a list of figures
    
    chosen_month = 0


    spreadsheet_under_consideration = 'THIS IS A PLACEHOLDER.xlsx'

    Months = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December') #list of the months to access things later

    #### STEP 1: Set up the figures #### 
    # in order for dash to plot the graph, we need to pass the dataframe object to the `figure = [xxx]` argument 
    



    ####################### DASH GOES HERE - NEED TO WORK OUT HOW TO MAKE THIS A FUNCTION IN ANOTHER PY FILE ####################### #th
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = html.Div([
        html.Img(src=app.get_asset_url('NEW_LOGO.jpg')), #display NEW LOGO
        html.P('Historical Energy Load Anaylsis Tool'), #quick graph
        dcc.Dropdown(id = 'Drop_Down_menu',
            options=[{'label':name, 'value':name} for name in names],
            value = names[0],
            multi=False #do not allow multiple 
            ), 
        dcc.Graph(id='daily_graph'), 
        dcc.Graph(id='weekly_graph'), 
    ])


    @app.callback(
        Output('daily_graph', 'figure'),
        [Input('Drop_Down_menu', 'value')])
    def update_figure(selected_name):
        #filter the names 
        chosen_site = character_removal(selected_name) #this sanitises the chosen input 

        ### DYNAMICALLY CREATE DATAFRAME TO SHOW ALL MONTHS ###
        dataframe_to_plot = dataframe_chooser(Daily_Interval_Data, chosen_site) #dynamically create dataframes to plot entire year of chosen 
        try: 
            fig = dataframe_to_plot.iplot(kind = 'line', xTitle='Site', yTitle='Consumption (kWh)', title = 'Consumption', asFigure = True) #create a list of figures
        except KeyError: #https://github.com/santosjorge/cufflinks/issues/180
            Mbox('PLOT ERROR', 'Dash has encountered an error. Please select another site, and try again', 1)

        return fig
    @app.callback(
        Output('weekly_graph', 'figure'),
        [Input('Drop_Down_menu', 'value')])
    def update_figure1(selected_name):
        #filter the names 
        chosen_site = character_removal(selected_name) #this sanitises the chosen input, which is gleaned from Dash Selection

        ### DYNAMICALLY CREATE DATAFRAME TO SHOW ALL MONTHS ###
        dataframe_to_plot = dataframe_chooser(Weekly_Interval_Data, chosen_site) #dynamically create dataframes to plot entire year of chosen 
        try: 
            fig = dataframe_to_plot.iplot(kind = 'line', xTitle='Site', yTitle='Consumption (kWh)', title = 'Consumption', asFigure = True) #create a list of figures
        except KeyError: #https://github.com/santosjorge/cufflinks/issues/180
            Mbox('PLOT ERROR', 'Dash has encountered an error. Please select another site, and try again', 1)

        return fig


    webbrowser.open('http://127.0.0.1:8888/')  # open the DASH app in default webbrowser
    print('Starting Dash Server')

    app.run_server(port=8888, debug = dev_tools_silence_routes_logging=) #start the server. 

    return #nothing 
