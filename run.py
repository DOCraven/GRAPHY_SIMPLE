
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
import plotly.graph_objects as go
#USER CREATED FUNCTIONS 
from fcn_Averages import DailyAverage, WeeklyAverage, MonthToDaySum, ConsumptionSummer
from fcn_plotting import character_removal, dataframe_chooser, dash_solar_plotter
from fcn_Importing import xlsxReader_Monthly, Extension_Checker, Data_Consistency_Checker, intervalResampler, Data_Analyser, parse_contents
from fcn_loadshifting import load_shifter_average, load_shifter_long_list, solar_extractor_adder
from fcn_UTILS import dataJoiner, CopyCat, dataframe_list_generator, dataframe_compactor, dataframe_saver, dataframe_matcher
from myproject.pricing import total_Retail_Bill, tou, populate_NEW_Retail_Bill
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

#sean helping me


######## CALLBACKS FOR APP.PY FUNCTIONALITY GO HERE #########

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
        fig = shifted_dataframe_to_plot.iplot(kind = 'line', xTitle='Time', yTitle='Consumption (kWh)', title = chosen_site, asFigure = True, theme="white") 
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
        fig = shifted_dataframe_to_plot.iplot(kind = 'line', xTitle='Day and Time', yTitle='Consumption (kWh)', title = chosen_site, asFigure = True, theme="white")  
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
def update_output(value, data, children): 
    # slider is value, 
    # Selected site via dropdown menu is data, 
    # selected month is children 
    
    ## VARS
    chosen_site = data #to narrow down the dataframe using previously existing data MY INPUT NAMES 
    
    chosen_site_output = dataframe_matcher(input_site = chosen_site)
    load_shift_number = value #%value to load shift selected site by - IT IS AN INT - need to convert it to % though
    config.shifted_site_value = load_shift_number # for displaying in the dash app. 
    
    chosen_month = children #selected month
    ### STEP 1 - narrow down dataframe to chosen site 
    site_to_plot_raw = dataframe_chooser(config.Daily_Interval_Data, chosen_site) #dynamically create dataframes to plot 12x months on top of each other for the selected site
    #the above returns a 12x? dataframe. need to convert it to a list of dataframes 
    
    ### STEP 2 - Convert the single 12xN dataframe into a dataframe for each month  - NOT NECESSARY FOR YEARLY DATA
    site_to_plot_list = dataframe_list_generator(non_list_dataframe = site_to_plot_raw) #converts the above into a list of 1x month per list entry 

    ### STEP 3 - extract solar from the original dataframe, and add it to each list 
    site_to_plot_solar_added = solar_extractor_adder(single_site = site_to_plot_list, all_sites = config.Daily_Interval_Data) #adds the respective monthly solar to the respective month (in the list)
    
    ### STEP 4A - do the load shift calculations for daily averaged data (list of dataframes), and return a single dataframe of each month - site_to_plopt_solar_added is a list of dataframes
    shifted_site = load_shifter_average(site_to_plot_solar_added, load_shift_number) #returns a list of shifted sites - THIS IS SAVED AS A CSV WHEN EXPORTING
    
    ### STEP 4B - do the load shift calculations for the entire year (single datagframe) and return a single dataframe
    #returns a list of shifted sites - THIS IS SAVED AS A CSV WHEN EXPORTING ,  - NEED TO ADD EXCESS SOLAR GENERATION (TOTAL) to this dataframe
    config.YEARLY_shifted_site = load_shifter_long_list(dataframe_to_shift = config.Checked_YEARLY_Interval_Data,  value_to_shift = load_shift_number, site_to_shift = chosen_site) 
    
    ### STEP 4C - integrate the shifted site into the original dataframe passed to it 
    config.Entire_Yearly_Site_With_Single_Shifted = config.Checked_YEARLY_Interval_Data.copy() #create a copy of the original dataframe to insert the load shifted site into 
    config.Entire_Yearly_Site_With_Single_Shifted[chosen_site] = config.YEARLY_shifted_site #insert the shifted site into the original dataframe
    config.Entire_Yearly_Site_With_Single_Shifted.set_index('Interval End' ,inplace = True) #set index to datetime
    dataframe_columns_to_drop = [
        'Excess Solar Generation (Total)', 'Excess Solar Generation (WWTP)',  
        'Total Consumption', 'Solar Generation (kW)' 
        ] 
    config.Entire_Yearly_Site_With_Single_Shifted.drop(columns = dataframe_columns_to_drop, inplace = True)


    ## TURNING OFF PRICING ALGORITHM FOR NOW 

    # config.demandProfiles = config.Entire_Yearly_Site_With_Single_Shifted #pass yearly site data to the dataframe
    # config.demandProfiles.index = pd.to_datetime(config.demandProfiles.index)

    ### STEP 4D - Pass it to the pricing function 
    # Shifted_Retail_Bill = populate_NEW_Retail_Bill()
    
    # ### STEP 4E - Sum total site bill and sum individual site bill
    # config.total_NEW_bill = Shifted_Retail_Bill.values.sum() #total NEW electricity bill 
    #     #https://stackoverflow.com/a/32340834/13181119
    # print('\n#######\nTotal NEW Bill: ')
    # print('$' + str(config.total_NEW_bill))

    # config.total_site_bill = Shifted_Retail_Bill.loc[:, str(chosen_site_output)].sum() #sum price for chosen site
    # print('\n#######\nTotal SITE Bill: ')
    # print('$' + str(config.total_site_bill))

    ## TURNING OFF PRICING ALGORITHM FOR NOW 

    ### STEP 5 - copy dataframe to save it for later
    config.shifted_site_to_save = shifted_site.copy() #copy it to go outside of scope - currently has no DateTime index (ie, just 0 1 2 ...... 99 100)
    
    ### STEP 6 - create a title for the figre
    config.plot_title = str(chosen_month) + ' - ' + chosen_site + ': LOAD SHIFTED ' + str(load_shift_number) + '%' #create title for graph depending on what is given to plot

    ### STEP 6 - Filter selected month - HERE BE LOGIC ERRORS
    month_filtered_site = shifted_site.loc[:, chosen_month] #return only selected months 

    ### STEP 8 - create figure from filtered site and selected month
    figure = month_filtered_site.iplot(kind = 'line', xTitle='Time', yTitle='Consumption (kWh)', title = config.plot_title, asFigure = True, theme="white") #plot the figure 
    

    message = 'You have load shifted {}'.format(value) + '%. Total kWh shifted: {}'.format(config.summed*-1)  #to display in DASH - *-1 to make the number positive to show
    # message = 'By loadshifting {}'.format(value) + '% ' + 'at Site {}'.format(chosen_site_output) + ' the total electricity bill is ${}'.format(config.total_NEW_bill) + ' and the total shifted site bill is ${}'.format(config.total_site_bill) #to display in DASH
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
    solar_name = 'Excess Solar Generation (Total)'

    ### DYNAMICALLY CREATE DATAFRAME TO SHOW ALL MONTHS ###
    #dynamically create load dataframes to plot 12x months on top of each other for the selected site
    consumption_dataframe_to_plot = dataframe_chooser(config.Daily_Pricing_Data, chosen_site) 
    #dynamically create Solar dataframes to plot 12x months on top of each other for the selected site
    solar_dataframe_to_plot = dataframe_chooser(config.Daily_Interval_Data, solar_name) 
    ### DYNAMICALLY SLICE DATAFRAME FOR MONTH 
    shifted_dataframe_to_plot_consumption = consumption_dataframe_to_plot.loc[:, chosen_month] #return only selected months,  
    shifted_dataframe_to_plot_solar = solar_dataframe_to_plot.loc[:, chosen_month] #return only selected months, SOLAR 


    #combine both dataframes 
    actual_dataframe_to_plot = pd.concat([shifted_dataframe_to_plot_consumption, shifted_dataframe_to_plot_solar], axis = 1) #columns headers are both the month - Need to change
    actual_dataframe_to_plot.columns = ['Monthly Spot Price', 'Excess Solar Generation']

    try: #create the figure to send to dash to plot
        fig = actual_dataframe_to_plot.iplot(kind = 'line', xTitle='Time', yTitle='Spot Price ($)', title = chosen_site, secondary_y = ['Excess Solar Generation'], secondary_y_title="Excess Solar Generation (MWh)",   asFigure = True, theme="white") 
        ## update the figure with other excess solar generation 
        ## https://stackoverflow.com/a/60374362/13181119

    except KeyError: #https://github.com/santosjorge/cufflinks/issues/180 - although waiting 0.5s before calling the 2nd graph seems to aboid this
        pass

    return fig

### CALLBACK FOR SOLAR EXCESS GRAPH IN AVERAGE PRICING
@app.callback( 
    #input (single item)
    dash.dependencies.Output('Price_daily_solar_graph', 'figure'),
    #output list
    [ 
    dash.dependencies.Input('Price_Drop_Down_menu', 'value'), #selected site, unused in this function
    dash.dependencies.Input('pricing_month_selection_output', 'children') #read the stored month )
    ]
    )
def update_daily_pricing_solar_graph(selected_name, children):
    #filter the names 
    chosen_month = children #selected month 
    # chosen_site = character_removal(selected_name) #this sanitises the chosen input into a standard string
    chosen_site = 'Excess Solar Generation (Total)'
    ### DYNAMICALLY CREATE DATAFRAME TO SHOW ALL MONTHS ###
    time.sleep(0.25) #mitigate an error where calling the plot function twice in a short amount of time means it does not plot the 2nd graph

    dataframe_to_plot = dataframe_chooser(config.Daily_Interval_Data, chosen_site) #dynamically create dataframes to plot entire year of chosen 
    shifted_dataframe_to_plot = dataframe_to_plot.loc[:, chosen_month] #return only selected months 
    # try: #create the figure to send to dash to plot
    fig = shifted_dataframe_to_plot.iplot(kind = 'line', xTitle='Day and Time', yTitle='Excess Solar Generation (kWh)', title = chosen_site, asFigure = True, theme="white") 
    # except KeyError: #https://github.com/santosjorge/cufflinks/issues/180 - although waiting 0.25s before calling this graph seems to avoid this
        # pass
    
    return fig


@app.callback(
    dash.dependencies.Output('Average_File_Saved_Output', 'children'),
    [dash.dependencies.Input('Average_Save', 'n_clicks')])
    # [dash.dependencies.State('input-box', 'value')])
def update_output(n_clicks):
    if n_clicks is not None: 
        #save modified dataframe
        dataframe_saver(time_frame = 'Average') #save the dataframe as a csv file 
        
        return 'Average File Saved'


### CALLBACK TO SAVE WHOLE YEAR LOAD SHIFTED FILE ###
@app.callback(
    dash.dependencies.Output('Yearly_File_Saved_Output', 'children'),
    [dash.dependencies.Input('Yearly_Save', 'n_clicks')])
    # [dash.dependencies.State('input-box', 'value')])
def update_output(n_clicks):
    if n_clicks is not None: 
        dataframe_saver(time_frame = 'Yearly') #save the dataframe as a csv file, does not have a time index, so will have to recreate that 
        
        return 'Yearly File Saved'




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

