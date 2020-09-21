
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
import cufflinks as cf
import base64
import flask
#USER CREATED FUNCTIONS 
from fcn_Averages import DailyAverage, WeeklyAverage, MonthToDaySum, ConsumptionSummer
from fcn_plotting import character_removal, dataframe_chooser, dash_solar_plotter
from fcn_Importing import xlsxReader_Monthly, Extension_Checker, Data_Consistency_Checker, intervalResampler, Data_Analyser, parse_contents
from fcn_loadshifting import load_shifter_average, load_shifter_long_list, solar_extractor_adder
from fcn_UTILS import dataJoiner, CopyCat, dataframe_list_generator, dataframe_compactor
#IMPORT USER DEFINED GLOBAL VARIABLES 
import config

####################################################
#
# HEROKU DEPLOYMENT NOTES (relative to local development machine)
# open CMD in heroku foler
# master branch is the deployed branch
# code
#
# PROCFILE NOTES
#   web: gunicorn app:server
#
#   app refers to app.py (however, note that it needs to be relative (ie, if it is in a folder it is myfolder.myapp))
#      https://stackoverflow.com/a/61480963/13181119
#   server refers to the variable server INSIDE app.py
#
# #make sure local dir has the most recent version of the master
#   git pull 
# 
# push the code change to heroku
#   git push heroku HEAD:master
#
# start a dyno 
#   heroku ps:scale web=1
####################################################




######## CALLBACKS FOR APP.PY FUNCTIONALITY GO HERE #########

## CALLBACK FOR DAILY GRAPH ###
@app.callback( 
    dash.dependencies.Output('daily_graph', 'figure'), 
    [
    dash.dependencies.Input('Drop_Down_menu', 'value'), #site selection 
    dash.dependencies.Input('tab1_month_selection_output', 'children')#read the stored month )
        ] 
        
        )
def update_daily_graph(selected_name, children):
    #filter the names 
    chosen_month = children #selected month 
    chosen_site = character_removal(selected_name) #this sanitises the chosen input into a standard string
    ### DYNAMICALLY CREATE DATAFRAME TO SHOW ALL MONTHS ###
    dataframe_to_plot = dataframe_chooser(config.Daily_Interval_Data, chosen_site) #dynamically create dataframes to plot 12x months on top of each other for the selected site
    #Dynamically slice dataframe to only show the month 
    shifted_dataframe_to_plot = dataframe_to_plot.loc[:, chosen_month] #return only selected months 
    
    try: #create the figure to send to dash to plot
        fig = shifted_dataframe_to_plot.iplot(kind = 'line', xTitle='Time', yTitle='Consumption (kWh)', title = chosen_site, asFigure = True) 
    except KeyError: #https://github.com/santosjorge/cufflinks/issues/180 - although waiting 0.5s before calling the 2nd graph seems to aboid this
        pass

    return fig

### CALLBACK FOR WEEKLY GRAPH ###
@app.callback( 
    dash.dependencies.Output('weekly_graph', 'figure'), 
    [
    dash.dependencies.Input('Drop_Down_menu', 'value'), #site selection 
    dash.dependencies.Input('tab1_month_selection_output', 'children')#read the stored month )
        ] 
        
        )
def update_weekly_graph(selected_name, children):
    #filter the names 
    chosen_month = children #selected month 
    chosen_site = character_removal(selected_name) #this sanitises the chosen input into a standard string
    ### DYNAMICALLY CREATE DATAFRAME TO SHOW ALL MONTHS ###
    time.sleep(0.25) #mitigate an error where calling the plot function twice in a short amount of time means it does not plot the 2nd graph
    dataframe_to_plot = dataframe_chooser(config.Weekly_Interval_Data, chosen_site) #dynamically create dataframes to plot entire year of chosen 
    #Dynamically slice dataframe to only show the month 
    shifted_dataframe_to_plot = dataframe_to_plot.loc[:, chosen_month] #return only selected months 
    try: #create the figure to send to dash to plot
        fig = shifted_dataframe_to_plot.iplot(kind = 'line', xTitle='Day and Time', yTitle='Consumption (kWh)', title = chosen_site, asFigure = True) 
    except KeyError: #https://github.com/santosjorge/cufflinks/issues/180 - although waiting 0.25s before calling this graph seems to avoid this
        pass
    
    return fig

### CALLBACK FOR SLIDER ###
############# GRAPH UPDATES ON THIS SLIDER ACTION ##################
@app.callback(
    [ #output list
        dash.dependencies.Output('shifting_slider_display', 'figure'), #output graph
        dash.dependencies.Output('slider-output-container', 'children') #output selected value
        ], 
    [ #input list 
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
    
    ### STEP 5 - create a title for the figre
    plot_title = str(chosen_month) + ' - ' + chosen_site + ': LOAD SHIFTED ' + str(load_shift_number) + '%' #create title for graph depending on what is given to plot

    ### STEP 6 - Filter selected month
    month_filtered_site = shifted_site.loc[:, chosen_month] #return only selected months 

    ### STEP 7 - create figure from filtered site and selected month
    figure = month_filtered_site.iplot(kind = 'line', xTitle='Time', yTitle='Consumption (kWh)', title = plot_title, asFigure = True) #plot the figure 
    
    message = 'You have load shifted {}'.format(value) + '%' #to display in DASH

    return figure, message

### CALLBACK FOR SHIFTED DAILY GRAPH DROPDOWN SELECTOR ###
@app.callback(Output('memory_output', 'data'),
            [Input('Shifted_Drop_Down_menu', 'value')]) #storing this
def filter_sites(value):
    return value #just return the value and store it in the location called "memory_output"
        
######### CALLBACK FOR MONTH DROP DOWN BOX IN SITE SELECTION ######
@app.callback(
    dash.dependencies.Output('month_selection_output', 'children'),
    [dash.dependencies.Input('month_selection', 'value')])
def update_output(value):
    return (value) #ie, what is selected via the drop down box 

######### CALLBACK FOR DASH IMPORTING/LOADING FILES ##########
@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None: #this function of broken for some reason, and the empty lists fixes it
        #create empty list
        list_of_contents_fixed = []
        list_of_names_fixed = []
        list_of_dates_fixed = []
        #append the broken object to the list, allowing the zip function to iterate over an int
        list_of_contents_fixed.append(list_of_contents)
        list_of_names_fixed.append(list_of_names)
        list_of_dates_fixed.append(list_of_dates)
        #normal dash functionality occurs here
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents_fixed, list_of_names_fixed, list_of_dates_fixed)]
        return children

######### CALLBACK FOR MONTH DROP DOWN BOX IN PRICING ######
@app.callback(
    dash.dependencies.Output('pricing_month_selection_output', 'children'),
    [dash.dependencies.Input('pricing_month_selection', 'value')])
def update_output(value):
    return (value) #ie, what is selected via the drop down box 

## CALLBACK FOR PRICING DAILY GRAPH ###
@app.callback( 
    dash.dependencies.Output('Price_daily_graph', 'figure'), #no brackets indicate a single thing returned, brackets indicate a list
    [
    dash.dependencies.Input('Price_Drop_Down_menu', 'value'),
    dash.dependencies.Input('pricing_month_selection_output', 'children')
        ] #read the stored month )
    )
def update_daily_pricing_graph(selected_name, children):
    #filter the names
    chosen_month = children #selected month 
    chosen_site = character_removal(selected_name) #this sanitises the chosen input into a standard string
    ### DYNAMICALLY CREATE DATAFRAME TO SHOW ALL MONTHS ###
    dataframe_to_plot = dataframe_chooser(config.Daily_Pricing_Data, chosen_site) #dynamically create dataframes to plot 12x months on top of each other for the selected site
    shifted_dataframe_to_plot = dataframe_to_plot.loc[:, chosen_month] #return only selected months 
    try: #create the figure to send to dash to plot
        fig = shifted_dataframe_to_plot.iplot(kind = 'line', xTitle='Time', yTitle='Spot Price ($)', title = chosen_site, asFigure = True) 
    except KeyError: #https://github.com/santosjorge/cufflinks/issues/180 - although waiting 0.5s before calling the 2nd graph seems to aboid this
        pass

    return fig

### CALLBACK FOR PRICING WEEKLY GRAPH ###
@app.callback( 
    #input (single item)
    dash.dependencies.Output('Price_weekly_graph', 'figure'),
    #output list
    [ 
    dash.dependencies.Input('Price_Drop_Down_menu', 'value'), 
    dash.dependencies.Input('pricing_month_selection_output', 'children') #read the stored month )
    ]
    )
def update_weekly_pricing_graph(selected_name, children):
    #filter the names 
    chosen_month = children #selected month 
    chosen_site = character_removal(selected_name) #this sanitises the chosen input into a standard string
    
    ### DYNAMICALLY CREATE DATAFRAME TO SHOW ALL MONTHS ###
    time.sleep(0.25) #mitigate an error where calling the plot function twice in a short amount of time means it does not plot the 2nd graph

    dataframe_to_plot = dataframe_chooser(config.Weekly_Pricing_Data, chosen_site) #dynamically create dataframes to plot entire year of chosen 
    shifted_dataframe_to_plot = dataframe_to_plot.loc[:, chosen_month] #return only selected months 
    try: #create the figure to send to dash to plot
        fig = shifted_dataframe_to_plot.iplot(kind = 'line', xTitle='Day and Time', yTitle='Spot Price ($)', title = chosen_site, asFigure = True) 
    except KeyError: #https://github.com/santosjorge/cufflinks/issues/180 - although waiting 0.25s before calling this graph seems to avoid this
        pass
    
    return fig

######### CALLBACK FOR MONTH DROP DOWN BOX IN SITE GRAPGHS (TAB 1) ######
@app.callback(
    dash.dependencies.Output('tab1_month_selection_output', 'children'),
    [dash.dependencies.Input('tab1_month_selection', 'value')])
def update_output(value):
    return (value) #ie, what is selected via the drop down box 

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run_server(debug = True, 
        # port=port, #for development server comment this line out 
        # host='0.0.0.0' #and this line out
        )

