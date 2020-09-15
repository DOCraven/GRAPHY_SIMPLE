
from myproject.app import app
from dash.dependencies import Input, Output #NEED TO ENSURE ONE CAN STORE DATA IN DCC.STORE


#DASH
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_table
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
import base64
#USER CREATED FUNCTIONS 
from fcn_Averages import DailyAverage, WeeklyAverage, MonthToDaySum, ConsumptionSummer
from fcn_plotting import character_removal, dataframe_chooser, Mbox, dash_solar_plotter
from fcn_Importing import xlsxReader_Monthly, Extension_Checker, Data_Consistency_Checker, intervalResampler, Data_Analyser, parse_contents
from fcn_loadshifting import load_shifter_average, load_shifter_long_list, solar_extractor_adder
from fcn_UTILS import dataJoiner, CopyCat, dataframe_list_generator, dataframe_compactor
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
        dash.dependencies.Input('memory_output', 'data'), #read the stored site 
        dash.dependencies.Input('month_selection_output', 'children') #read the stored month 
        ]) #AND READ THE STORED VALUE AT 'memory_output' in layout[]
def update_output(value, data, children): #slider is value, dropdown menue is data, selected month is children 
    ## VARS
    chosen_site = data #to narrow down the dataframe using previously existing data
    load_shift_number = value #%value to load shift selected site by - IT IS AN INT - need to convert it to % though
    chosen_month = children #selected month
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
    plot_title = str(chosen_month) + ' - ' + chosen_site + ': LOAD SHIFTED ' + str(load_shift_number) + '%' #create title for graph depending on what is given to plot

    ### STEP 6 - Filter selected month
    month_filtered_site = shifted_site.loc[:, chosen_month] #return only selected months 

    figure = month_filtered_site.iplot(kind = 'line', xTitle='Time', yTitle='Consumption (kWh)', title = plot_title, asFigure = True) #plot the figure 
    
    message = 'You have load shifted {}'.format(value) + '%' #to display in DASH

    return figure, message

    ### CALLBACK FOR SHIFTED DAILY GRAPH DROPDOWN SELECTOR ###

@app.callback(Output('memory_output', 'data'),
            [Input('Shifted_Drop_Down_menu', 'value')]) #storing this
def filter_sites(value):
    return value #just return the value and store it in the location called "memory_output"
        
######### CALLBACK FOR MONTH DROP DOWN BOX ######
@app.callback(
    dash.dependencies.Output('month_selection_output', 'children'),
    [dash.dependencies.Input('month_selection', 'value')])
def update_output(value):
    return (value) #ie, what is selected via the drop down box 

######### CALLBACK FOR LOADING BUTTON ##########
@app.callback(
    dash.dependencies.Output('container-button-basic', 'children'),
    [dash.dependencies.Input('submit-val', 'n_clicks')],
    [dash.dependencies.State('input-on-submit', 'value')]
    )
def update_output(n_clicks, value):
    #open the load window on button click
    sg.theme('Light Blue 2')

    layout_landing = [[sg.Text('NEW Landing Page')], #layout
            [sg.Text('Please open your interval data (and if required, solar data) in XLS format')],
            [sg.Text('Interval Data', size=(10, 1)), sg.Input(), sg.FileBrowse()],
            [sg.Text('Solar Data', size=(10, 1)), sg.Input(), sg.FileBrowse()],
            [sg.Submit(), sg.Cancel()]]

    if n_clicks >= 1:  #open the LOADING window only after a click
        window = sg.Window('NEW Graphy (Simple)', layout_landing) #open the window 

        event, values = window.read()
        window.close()
        config.Data_Uploaded = True
        
        try: #so I dont have to comment this out when automatically loading test data 
            if event == 'Cancel': 
                exit() #close the app
        except NameError: 
            pass 

        #ensure someone has uploaded a file 
        if not values[0]: #nothing uploaded
            Mbox('UPLOAD ERROR', 'Please upload a CSV or XLSX file', 1) #spit out an error box 
            exit() #close the app

        Data_Analyser(values) #function to analyise all the data 

        return 'Data loaded:  "{}" '.format(
            values[0]
        )


######### CALLBACK FOR DASH LOADING ##########
@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates): #literal magic - I have no idea how it works, 
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


if __name__ == '__main__':
    app.run_server()