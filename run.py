
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
#USER CREATED FUNCTIONS 
from fcn_Averages import DailyAverage, WeeklyAverage, MonthToDaySum, ConsumptionSummer
from fcn_plotting import character_removal, dataframe_chooser, Mbox, dash_solar_plotter
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
#   app refers to app.py
#   server refers to the variable server INSIDE app.py
#
# #make sure local dir has the most recent version of the master
#   git pull 
# 
# push the code change to heroku
#   git push heroku HEAD:master
####################################################

########## ACTUAL DASH LAYOUT GOES HERE ##########

@app.callback(Output('tabs-example-content', 'children'),
              [Input('tabs-example', 'value')])
def render_content(tab):
    if tab == 'tab-1': #LOAD DATA - PLACEHOLDER - TO BE BUILT
        return html.Div([
            html.H3('Load Interval and Solar Data'),
            #upload data
            html.P('Please upload consumption interval files and/or solar files\n. Please ensure the solar data file has the word "Solar" in it.'),
            html.P('Please upload a maximum of 2 interval files'),
            html.P('There is minimal error checking for number of data files uploaded. This may be added in future versions'),
            html.P('Please be aware that the program takes a little while to do the analysis in the background. Currently there is no loading animation. This may change in future versions. Please be patient, this is a work in progress'),
            dcc.Upload(
                html.Button('Upload Files'), 
                id='upload-data',
                style={ #make a nice box around it
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=True
            ),
            html.Div(id='output-data-upload'), #show the data, and this needs to exist for the code to work 


        ])
    
    elif tab == 'tab-2': #FANCY INTERVAL GRAPHS
        if config.Data_Uploaded: 
            return html.Div([
                html.H3('Historical Energy Load Anaylsis Tool'), #quick graph
                dcc.Dropdown(id = 'Drop_Down_menu', #make selection menu
                    options=[{'label':name, 'value':name} for name in config.Pricing_names],
                    value = config.names[0],#initial default selection upon loading 
                    multi=False #do not allow multiple selections 
                    ), 
                dcc.Graph(id='Pricing_daily_graph'), #display daily graph
                dcc.Graph(id='Pricing_weekly_graph'), #display weekly graph
                
                
            ])
        else: 
            return html.Div([
                html.H3('Please upload interval and/or solar')
            ])
    
    elif tab == 'tab-3': #LOAD SHIFTING SITE STUFF
        if config.Data_Uploaded: 
            if config.Solar_Exists: 
                return html.Div([
                    dcc.Store(id='memory_output'), #storing the selected site here
                    dcc.Store(id='month_selection_output'), #storing the selected site here
                    html.H3('Select a site to investigate'), 
                    dcc.Dropdown(  #make drop down selection menu - STORING THIS BAD BOY IN THE DCC.STORE ABOVE
                        id = 'Shifted_Drop_Down_menu', #unique identifier for DASH Callbacks
                        options=[{'label':name, 'value':name} for name in config.names], #dynamically populating the list 
                        value = config.names[0],#initial default selection upon loading 
                        multi=False #do not allow multiple selections 
                        ), 
                    
                    html.P(''), #blank row 
                    html.H3('Select a % to load shift by'), 
                    dcc.Slider( #load shifting slider thingo 
                        id='shifting_slider', #unique identifier for DASH Callbacks
                        min=0,
                        max=50,
                        step=1,
                        value=0, #initial slider value - TODO: read dataframe holding that information in it 
                    ),
                    html.Div(id='slider-output-container'), #display slider output
                    html.P(''), #blank row 
                    html.H3('Select a Month to Plot'), 
                    dcc.Dropdown(
                        id='month_selection',
                        options=[ #display options for dropdown value 
                            {'label': 'January', 'value': 'January'},
                            {'label': 'February', 'value': 'February'},
                            {'label': 'March', 'value': 'March'},
                            {'label': 'April', 'value': 'April'},
                            {'label': 'May', 'value': 'May'},
                            {'label': 'June', 'value': 'June'},
                            {'label': 'July', 'value': 'July'},
                            {'label': 'August', 'value': 'August'},
                            {'label': 'September', 'value': 'September'},
                            {'label': 'October', 'value': 'October'},
                            {'label': 'November', 'value': 'November'},
                            {'label': 'December', 'value': 'December'},
                            ],
                        value='January',
                        multi=True
                    ),
                    
                    dcc.Graph(id='shifting_slider_display'), #display the dynamically shifted graph upon update of slider 
                    html.H4('Excess Solar'), #blank row 
                    dcc.Graph(id='Daily Excess Summmed Solar - line ', figure = config.solar_figure_line), #display sum of all solar graph as a summed box per month
                    ])
            else: 
                return html.H3("No Solar Data Uploaded")
        else: 
            return html.Div([
                html.H3('Please upload interval and/or solar')
            ]) 

    elif tab == 'tab-4': #EXCESS SOLAR DATA 
        if config.Data_Uploaded: 
            if config.Solar_Exists: ## ie, user uploaded a solar file, so plot the nice and pretty graphs
                return html.Div([
                    html.H3("Solar Data Uploaded"),
                    dcc.Graph(id='Daily Excess Summmed Solar - line ', figure = config.solar_figure_line), #display all excess solar graph as a line graph per month
                    dcc.Graph(id='Daily Excess Summmed Solar - bar', figure = config.solar_figure_summed), #display sum of all solar graph as a summed box per month

                ]) 
            else: 
                return html.H3("No Solar Data Uploaded")
        
        else: 
            return html.Div([
                html.H3('Please upload interval and/or solar')
            ])

    elif tab == 'tab-5': #EXPORT THE DATA TO A CSV - PLACEHOLDER - TO BE BUILT
        if config.Data_Uploaded:
                return html.Div([
                    html.H3('Export Load Shift Data'),

                ])
        
        else: 
            return html.Div([
                html.H3('Please upload interval and/or solar')
            ])
    
    elif tab == 'tab-6': #YEARLY TOTALS PER SITE
            if config.Data_Uploaded: 
                return html.Div([
                    html.H3('Yearly Site Consumption'),
                    dcc.Graph(id='Total Yearly Site Consumption - bar', figure = config.yearly_summed_figure)

                ])
            else: 
                return html.Div([
                    html.H3('Please upload interval and/or solar')
                ])


    elif tab == 'tab-7': #Pricing Data
            if config.Data_Uploaded: 
                return html.Div([
                    html.H3('Pricing Data'),
                    dcc.Dropdown(id = 'Price_Drop_Down_menu', #make selection menu
                        options=[{'label':name, 'value':name} for name in config.Pricing_names],
                        value = config.Pricing_names[0],#initial default selection upon loading 
                        multi=False #do not allow multiple selections 
                        ), 
                    dcc.Graph(id='Price_daily_graph'), #display daily graph
                    dcc.Graph(id='Daily Excess Summmed Solar - line ', figure = config.solar_figure_line), #display all excess solar graph as a line graph per month
                    dcc.Graph(id='Price_weekly_graph'), #display weekly graph
                    ])
            else: 
                return html.Div([
                    html.H3('Please upload interval and/or solar')
                ])


    elif tab == 'tab-99': #ABOUT - FILL IN WITH THE README WHEN I HAVE TIME
            return html.Div([
                html.H3('About'),
                
            ])




######## CALLBACKS FOR APP.PY FUNCTIONALITY GO HERE #########

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

######### CALLBACK FOR DASH IMPORTING/LOADING FILES ##########
@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates): #literal magic - I have no idea how it works,
    if list_of_contents is not None:
        config.number_of_files_uploaded = len(list_of_names) #determine the number of files uploaded
        config.reset_dataframes = True #to stop this function being called again
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


## CALLBACK FOR PRICING DAILY GRAPH ###
@app.callback( 
    Output('Price_daily_graph', 'figure'), 
    [Input('Price_Drop_Down_menu', 'value')])
def update_daily_graph(selected_name):
    #filter the names 
    chosen_site = character_removal(selected_name) #this sanitises the chosen input into a standard string
    ### DYNAMICALLY CREATE DATAFRAME TO SHOW ALL MONTHS ###
    dataframe_to_plot = dataframe_chooser(config.Daily_Pricing_Data, chosen_site) #dynamically create dataframes to plot 12x months on top of each other for the selected site
    try: #create the figure to send to dash to plot
        fig = dataframe_to_plot.iplot(kind = 'line', xTitle='Time', yTitle='Spot Price ($)', title = chosen_site, asFigure = True) 
    except KeyError: #https://github.com/santosjorge/cufflinks/issues/180 - although waiting 0.5s before calling the 2nd graph seems to aboid this
        Mbox('PLOT ERROR', 'Dash has encountered an error. Please select another site, and try again', 1)

    return fig

### CALLBACK FOR PRICING WEEKLY GRAPH ###
@app.callback(
    Output('Price_weekly_graph', 'figure'),
    [Input('Price_Drop_Down_menu', 'value')])
def update_weekly_graph(selected_name):
    #filter the names 
    chosen_site = character_removal(selected_name) #this sanitises the chosen input into a standard string
    ### DYNAMICALLY CREATE DATAFRAME TO SHOW ALL MONTHS ###
    time.sleep(0.25) #mitigate an error where calling the plot function twice in a short amount of time means it does not plot the 2nd graph
    dataframe_to_plot = dataframe_chooser(config.Weekly_Pricing_Data, chosen_site) #dynamically create dataframes to plot entire year of chosen 
    try: #create the figure to send to dash to plot
        fig = dataframe_to_plot.iplot(kind = 'line', xTitle='Day and Time', yTitle='Spot Price ($)', title = chosen_site, asFigure = True) 
    except KeyError: #https://github.com/santosjorge/cufflinks/issues/180 - although waiting 0.25s before calling this graph seems to avoid this
        Mbox('PLOT ERROR', 'Dash has encountered an error. Please select another site, and try again', 1)
    
    return fig



if __name__ == '__main__':
    app.run_server(
        port=8050, #for development server comment this line out 
        host='0.0.0.0' #and this line out
        )

# to run the file locally just input 
    # waitress-serve run:app.server
#into the Command Line