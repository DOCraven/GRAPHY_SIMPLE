### This script will read 30 minutely interval data (supplied via xls) and generate useful outputs. 
# outputs include daily and monthly average, daily Sum, and more to come
# also uses some libraries to make nice interactive graphs for manipulation and interpretation

# THIS PROGRAM REQUIRES ADDITIONAL .py FILES
# - GUI_fcn.py
# - UTILS_fcn.py



### USEFUL STACK EXHANGE AND PANDAS DOCUMENTATION ###

    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.resample.html
    # https://pandas.pydata.org/pandas-docs/stable/reference/resampling.html
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/visualization.html#visualization-scatter-matrix
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases%3E - frequency alias
    

    # https://pandas-docs.github.io/pandas-docs-travis/user_guide/groupby.html # GROUPYBY DATA FOR DOING STUFF ON MULTINDEX STUFF

    # https://stackoverflow.com/a/17001474/13181119
    # https://stackoverflow.com/a/36684166/13181119


    # https://gist.github.com/phobson/8d853ddf23d1d692fe4d#file-sac-regression-ipynb - I THINK THIS IS VERY USEFUL FOR LATER 
    # https://plotly.com/python/cufflinks/ - makes plotting nice and pretty
        # https://github.com/santosjorge/cufflinks



### INPUTS ###
# Plant Load interval data in 30 minute intervals as an .XLS files 
# Solar predictions from PVSyst (resolution TBA) as an .XLS file

### OUTPUTS ###
# interval data split into monthly dataframes
# Pretty graphs 
    # Average Daily Load Profiles for each NEW industrial load
    # Summed daily consumption as a % of max consumption


### libraries

import pandas as pd
import datetime as dt
# import cufflinks as cf
import numpy as np
import os
import matplotlib.pyplot as plt
import datetime as dt
from calendar import day_name
import PySimpleGUI as sg


## DASH ##

import dash
import dash_html_components as html
import dash_core_components as dcc

from dash.dependencies import Input, Output




#external explicit function files
from fcn_GUI import GRAPH_GUI, GUI_Solar
from fcn_UTILS import dataJoiner, xlsxReader, intervalResampler, Extension_Checker, Data_Consistency_Checker, CopyCat
from fcn_Solar_Calculator import DaySummation, SolarSlicer 
from fcn_Averages import DailyAverage, WeeklyAverage, MonthToDaySum, ConsumptionSummer


def main():
    """ Main fcn"""
    
    ### VARS ###
    Solar_Exists = False
    weekly_dash_figure = [] #empty list to populate weekly figures to pass to dash
    daily_dash_figure = [] #empty list to populate weekly figures to pass to dash
    monthly_total_consumption_figure = [] #empty list to populate with monthly consumption data
    weekly_total_consumption_figure = [] #empty list to populate with weekly consumption data
    daily_total_consumption_figure = [] #empty list to populate with daily consumption data
    
    plt.close('all') #ensure all windows are closed
    
    ## Create the MAIN GUI LANDING PAGE ##
    sg.theme('Light Blue 2')

    layout_landing = [[sg.Text('NEW Landing Page')],
            [sg.Text('Please open your interval data (and if required, solar data) in either XLS or CSV format')],
            [sg.Text('Interval Data', size=(10, 1)), sg.Input(), sg.FileBrowse()],
            [sg.Text('Solar Data', size=(10, 1)), sg.Input(), sg.FileBrowse()],
            [sg.Submit(), sg.Cancel()]]

    window = sg.Window('NEW Graphy (Simple)', layout_landing)

    event, values = window.read()
    window.close()

    # ProgressBar() #placeholder for progress/update bar while the fcn Data_Analysis is occuring

    ## STEP 1: read files, check extensions are valid, and import as dataframes
    try: #read the inverval load data
        Interval_Data = Extension_Checker(values[0]) #check to see if the interval load data is input is valid (ie, xlsx only)
    except UnboundLocalError: 
        pass
    try: #read the solar data
        if values[1]: #only read if solar data is input
            Solar_Exists = True #for data handling later on. 
            Solar_Data = Extension_Checker(values[1]) #check to see if Solar_data input is valid (ie, xlsx only)
    except UnboundLocalError: 
        pass
    
    ## STEP 1A: join the solar data to the dataframe (if necessary)
    if Solar_Exists: #combine Solar data to back of the interval load data if it exists
        Full_Interval_Data = dataJoiner(Interval_Data, Solar_Data)

    else: #does not combine the solar data to the back of the interval load data
        Full_Interval_Data = Interval_Data

    
    ## STEP 2: Check for consistency, and interpolate if requried
    Checked_Interval_Data_0 = Data_Consistency_Checker(Full_Interval_Data)
        
    ## STEP 3: Copy dataframe (to get around an error of the dataframe being modifed by WeeklyAverage(), will fix properly later)
    Checked_Interval_Data_1 = CopyCat(Checked_Interval_Data_0)
    
    ## STEP 4: Calculate Weekly averages
    Weekly_Interval_Data = WeeklyAverage(Checked_Interval_Data_0)
        
    ## STEP 5: Calculate Daily Averages
  
    Daily_Interval_Data = DailyAverage(Checked_Interval_Data_1)

    ## STEP 6: Calculate summation of energy used (Yearly, monthly, weekly, daily)

    Monthly_sum = ConsumptionSummer(Checked_Interval_Data_1) #total average month (x12 months)
   
    weekly_sum = ConsumptionSummer(Weekly_Interval_Data) #total average week in a month (x12 months)
    
    daily_sum = ConsumptionSummer(Daily_Interval_Data) #total average day in a month (x12 months)

    ####################### DASH GOES HERE - NEED TO WORK OUT HOW TO MAKE THIS A FUNCTION IN ANOTHER PY FILE #######################

    #### STEP 1: Set up the figures ####
    for i in range(0, len(Weekly_Interval_Data)): #iterate through each month for weekly data
        weekly_dash_figure.append(Weekly_Interval_Data[i].iplot(kind = 'line', xTitle='Time', yTitle='kWh Consumption', asFigure = True) ) #create a list of figures

    for i in range(0, len(Daily_Interval_Data)): #iterate through each month for daily data
        daily_dash_figure.append(Daily_Interval_Data[i].iplot(kind = 'line', xTitle='Time', yTitle='kWh Consumption', asFigure = True)) #create a list of figures) 
    
    for i in range(0, len(Monthly_sum)): #iterate through each month for daily data
        monthly_total_consumption_figure.append(Weekly_Interval_Data[i].iplot(kind = 'bar', xTitle='NEW Site', yTitle='Total kWh Consumption', asFigure = True) ) #create a list of figures

    
    

    
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = html.Div([
        ### SET THE TABS UP ###
        dcc.Tabs(id='tabs-example', value='tab-1', children=[
            dcc.Tab(label='January', value='tab-1'),
            dcc.Tab(label='February', value='tab-2'),
            dcc.Tab(label='March', value='tab-3'),
            dcc.Tab(label='April', value='tab-4'),
            dcc.Tab(label='May', value='tab-5'),
            dcc.Tab(label='June', value='tab-6'),
            dcc.Tab(label='July', value='tab-7'),
            dcc.Tab(label='August', value='tab-8'),
            dcc.Tab(label='September', value='tab-9'),
            dcc.Tab(label='October', value='tab-10'),
            dcc.Tab(label='November', value='tab-11'),
            dcc.Tab(label='December', value='tab-12'),
        ]),
        html.Div(id='tabs-example-content')
    ])

    @app.callback(Output('tabs-example-content', 'children'),
                [Input('tabs-example', 'value')])

    ### DO STUFF WITH THE TABS ###
    def render_content(tab):
        if tab == 'tab-1':
            return html.Div([
                html.H3('Weekly'),
                dcc.Graph(id='January Weekly Consumption',figure=weekly_dash_figure[0]),

                html.H3('Daily'),
                dcc.Graph(id='January Daily Consumption',figure=daily_dash_figure[0]),
                html.H3('Total Summation')
            ])
        elif tab == 'tab-2':
            return html.Div([
                html.H3('Weekly'),
                dcc.Graph(id='February Weekly Consumption',figure=weekly_dash_figure[1]),

                html.H3('Daily'),
                dcc.Graph(id='February Daily Consumption',figure=daily_dash_figure[1]),
                html.H3('Total Summation')
            ])
        elif tab == 'tab-3':
            return html.Div([
                html.H3('Weekly'),
                dcc.Graph(id='March Weekly Consumption',figure=weekly_dash_figure[2]),

                html.H3('Daily'),
                dcc.Graph(id='March Daily Consumption',figure=daily_dash_figure[2]),
                html.H3('Total Summation')
            ])
        elif tab == 'tab-4':
            return html.Div([
                html.H3('Weekly'),
                dcc.Graph(id='April Weekly Consumption',figure=weekly_dash_figure[3]),

                html.H3('Daily'),
                dcc.Graph(id='April Daily Consumption',figure=daily_dash_figure[3]),
                html.H3('Total Summation')
            ])
        elif tab == 'tab-5':
            return html.Div([
                html.H3('Weekly'),
                dcc.Graph(id='May Weekly Consumption',figure=weekly_dash_figure[4]),

                html.H3('Daily'),
                dcc.Graph(id='May Daily Consumption',figure=daily_dash_figure[4]),
                html.H3('Total Summation')
            ])
        elif tab == 'tab-6':
            return html.Div([
                html.H3('Weekly'),
                dcc.Graph(id='June Weekly Consumption',figure=weekly_dash_figure[5]),

                html.H3('Daily'),
                dcc.Graph(id='June Daily Consumption',figure=daily_dash_figure[5]),
                html.H3('Total Summation')
            ])
        elif tab == 'tab-7':
            return html.Div([
                html.H3('Weekly'),
                dcc.Graph(id='July Weekly Consumption',figure=weekly_dash_figure[6]),

                html.H3('Daily'),
                dcc.Graph(id='July Daily Consumption',figure=daily_dash_figure[6]),
                html.H3('Total Summation')
            ])
        elif tab == 'tab-8':
            return html.Div([
                html.H3('Weekly'),
                dcc.Graph(id='August Weekly Consumption',figure=weekly_dash_figure[7]),

                html.H3('Daily'),
                dcc.Graph(id='August Daily Consumption',figure=daily_dash_figure[7]),
                html.H3('Total Summation')
            ])
        elif tab == 'tab-9':
            return html.Div([
                html.H3('Weekly'),
                dcc.Graph(id='September Weekly Consumption',figure=weekly_dash_figure[8]),

                html.H3('Daily'),
                dcc.Graph(id='September Daily Consumption',figure=daily_dash_figure[8]),
                html.H3('Total Summation')
            ])
        elif tab == 'tab-10':
            return html.Div([
                html.H3('Weekly'),
                dcc.Graph(id='October Weekly Consumption',figure=weekly_dash_figure[9]),

                html.H3('Daily'),
                dcc.Graph(id='October Daily Consumption',figure=daily_dash_figure[9]),
                html.H3('Total Summation')
            ])
        elif tab == 'tab-11':
            return html.Div([
                html.H3('Weekly'),
                dcc.Graph(id='November Weekly Consumption',figure=weekly_dash_figure[10]),

                html.H3('Daily'),
                dcc.Graph(id='November Daily Consumption',figure=daily_dash_figure[10]),
                html.H3('Total Summation')
            ])
        elif tab == 'tab-12':
            return html.Div([
                html.H3('Weekly'),
                dcc.Graph(id='December Weekly Consumption',figure=weekly_dash_figure[11]),

                html.H3('Daily'),
                dcc.Graph(id='December Daily Consumption',figure=daily_dash_figure[11]),
                html.H3('Total Summation')
            ])


    if __name__ == '__main__': ## actually run the dash app
        print('Starting Dash Server')
        app.run_server(debug=True)

    ####################### DASH GOES HERE - NEED TO WORK OUT HOW TO MAKE THIS A FUNCTION IN ANOTHER PY FILE #######################

    # GRAPH_GUI(Weekly_Mean = Weekly_Interval_Data, Daily_Mean = Daily_Interval_Data)


   
    return #nothing main



### MAIN ###

main()



print('\nCODE \n C\n  O\n   M\n    P\n     L\n      E\n       T\n        E\n         D\n')


