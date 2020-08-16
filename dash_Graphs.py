### libraries

import pandas as pd
import datetime as dt
import numpy as np
import os
import matplotlib.pyplot as plt
import datetime as dt
import webbrowser
from calendar import day_name




## DASH ##

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


def character_removal(string_to_filter): 
    chars_to_remove = ['[', ']', '\'']
    filtered_list = []
    #determine if it is a list 
    if isinstance(string_to_filter, list): #if it is a list 
        for x in range(0, len(string_to_filter)): #iterate through lenghth of list
            for char in chars_to_remove: #filter through characters to remove
                string_to_filter[x] = string_to_filter[x].replace(char, '') #remove each character
            filtered_list.append(string_to_filter[x]) #append each filtered word to a new
        return filtered_list #return it 
        
    else: #not a list
        for char in chars_to_remove: #filter through chars to remove
            string_to_filter = string_to_filter.replace(char, '') #remove the char by replacing it with nothing
    return string_to_filter #return it 

def dataframe_chooser(Daily_Interval_Data, chosen_site): 
    """function to dynamically slice and create a new dataframe from given dataframes"""
    Months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'] #list of the months to access things later
    dynamically_created_dataframe = pd.concat([Daily_Interval_Data[0].loc[:, chosen_site], Daily_Interval_Data[1].loc[:, chosen_site],Daily_Interval_Data[2].loc[:, chosen_site],
                            Daily_Interval_Data[3].loc[:, chosen_site],Daily_Interval_Data[4].loc[:, chosen_site],Daily_Interval_Data[5].loc[:, chosen_site],
                            Daily_Interval_Data[6].loc[:, chosen_site],Daily_Interval_Data[7].loc[:, chosen_site],Daily_Interval_Data[8].loc[:, chosen_site],
                            Daily_Interval_Data[9].loc[:, chosen_site],Daily_Interval_Data[10].loc[:, chosen_site],Daily_Interval_Data[11].loc[:, chosen_site]], axis = 1) # append all DF's into a single dataframe YES THIS IS JANNKY I WILL FIX IT LATER 
    dynamically_created_dataframe.columns = Months #make the column names line up 

    return dynamically_created_dataframe




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
        html.P('Some words go here'),
        dcc.Dropdown(id = 'Drop_Down_menu',
            options=[{'label':name, 'value':name} for name in names],
            value = names[0],
            multi=False #do not allow multiple 
            ), 
        dcc.Graph(id='graph-with-slider')
    ])


    @app.callback(
        Output('graph-with-slider', 'figure'),
        [Input('Drop_Down_menu', 'value')])
    def update_figure(selected_name):
        #filter the names 
        chosen_site = character_removal(selected_name) #this sanitises the chosen input 

        ### DYNAMICALLY CREATE DATAFRAME TO SHOW ALL MONTHS ###
        dataframe_to_plot = dataframe_chooser(Daily_Interval_Data, chosen_site) #dynamically create dataframes to plot entire year of chosen 
        
        fig = dataframe_to_plot.iplot(kind = 'line', xTitle='Site', yTitle='Consumption (kWh)', title = 'Consumption', asFigure = True) #create a list of figures 

        return fig


    webbrowser.open('http://127.0.0.1:8888/')  # open the DASH app in default webbrowser
    print('Starting Dash Server')

    app.run_server(port=8888) #start the server. 

    return #nothing 
