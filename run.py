
from myproject.app import app
from dash.dependencies import Input, Output #NEED TO ENSURE ONE CAN STORE DATA IN DCC.STORE


#DASH
import dash
import dash_html_components as html
import dash_core_components as dcc
#ANALYSIS ETC
import pandas as pd
import datetime as dt
import numpy as np
import os
import matplotlib.pyplot as plt
import datetime as dt
import webbrowser
from calendar import day_name
import ctypes 
import time
import PySimpleGUI as sg
import cufflinks as cf
#USER CREATED FUNCTIONS 
from fcn_UTILS import dataJoiner, xlsxReader_Monthly, Extension_Checker, intervalResampler, Data_Consistency_Checker, CopyCat, character_removal, dataframe_chooser, Mbox, dash_solar_plotter, load_shifter_average, solar_extractor_adder, dataframe_list_generator, dataframe_compactor, load_shifter_scratch, load_shifter_long_list
from fcn_Averages import DailyAverage, WeeklyAverage, MonthToDaySum, ConsumptionSummer
#IMPORT USER DEFINED GLOBAL VARIABLES 
import config





######### CALLBACKS FOR APP.PY FUNCTIONALITY GO HERE #########

## CALLBACK FOR DAILY GRAPH ###
@app.callback( 
    Output('daily_graph', 'figure'), 
    [Input('Drop_Down_menu', 'value')])
def update_daily_graph(selected_name):
    #filter the names 
    chosen_site = character_removal(selected_name) #this sanitises the chosen input into a standard string
    ### DYNAMICALLY CREATE DATAFRAME TO SHOW ALL MONTHS ###
    dataframe_to_plot = dataframe_chooser(config.Daily_Interval_Data, chosen_site) #dynamically create dataframes to plot 12x months on top of each other for the selected site
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
    dataframe_to_plot = dataframe_chooser(config.Weekly_Interval_Data, chosen_site) #dynamically create dataframes to plot entire year of chosen 
    try: #create the figure to send to dash to plot
        fig = dataframe_to_plot.iplot(kind = 'line', xTitle='Day and Time', yTitle='Consumption (kWh)', title = chosen_site, asFigure = True) 
    except KeyError: #https://github.com/santosjorge/cufflinks/issues/180 - although waiting 0.25s before calling this graph seems to avoid this
        Mbox('PLOT ERROR', 'Dash has encountered an error. Please select another site, and try again', 1)
    
    return fig

### CALLBACK FOR SLIDER ###
############# GRAPH UPDATES ON THIS SLIDER ACTION ##################
@app.callback(
    [
        dash.dependencies.Output('shifting_slider_display', 'figure'), #output graph
        dash.dependencies.Output('slider-output-container', 'children') #output selected value
        ], 
    [
        dash.dependencies.Input('shifting_slider', 'value'), #read the slider input 
        dash.dependencies.Input('memory_output', 'data')
        ]) #AND READ THE STORED VALUE AT 'memory_output' in layout[]
def update_output(value, data): #slider is value, dropdown menue is data
    ## VARS
    chosen_site = data #to narrow down the dataframe using previously existing data
    load_shift_number = value #%value to load shift selected site by - IT IS AN INT - need to convert it to % though

    ### STEP 1 - narrow down dataframe to chosen site 
    site_to_plot_raw = dataframe_chooser(config.Daily_Interval_Data, chosen_site) #dynamically create dataframes to plot 12x months on top of each other for the selected site
    #the above returns a 12x? dataframe. need to convert it to a list of dataframes 
    
    ### STEP 2 - Convert the dataframe for a list of dataframes 
    site_to_plot_list = dataframe_list_generator(non_list_dataframe = site_to_plot_raw) #converts the above into a list of 1x month per list entry 

    ### STEP 3 - extract solar from the original dataframe, and add it to each list 
    site_to_plot_solar_added = solar_extractor_adder(single_site = site_to_plot_list, all_sites = config.Daily_Interval_Data) #adds the respective monthly solar to the respective month (in the list)
    
    ### STEP 4 - do the load shift calculations, and return a single dataframe of each month 
    shifted_site = load_shifter_average(site_to_plot_solar_added, load_shift_number) #returns a list of shifted sites - IE, I PLOT THIS 
    

    ### STEP 5 - create a figure via cufflinks to ploit 
    plot_title = chosen_site + ': LOAD SHIFTED ' + str(load_shift_number) + '%'
    figure = shifted_site.iplot(kind = 'line', xTitle='Time', yTitle='Consumption (kWh)', title = plot_title, asFigure = True) #
    
    message = 'You have load shifted {}'.format(value) + '%'

    return figure, message

    ### CALLBACK FOR SHIFTED DAILY GRAPH DROPDOWN SELECTOR ###

@app.callback(Output('memory_output', 'data'),
            [Input('Shifted_Drop_Down_menu', 'value')]) #storing this
def filter_sites(value):
    return value #just return the value and store it in the location called "memory_output"
        
### CALLBACK FOR DROP DOWN MENU FOR EXPORTER ####
# @app.callback( 
#     Output('daily_graph', 'figure'), 
#     [Input('Drop_Down_menu_export', 'value')])
# def update_daily_graph(value):
#     #filter the names 
#     return value


if __name__ == '__main__':
    app.run_server()