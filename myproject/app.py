### USER DEFINED DASH FILES ###
from .server import app, server
#DASH
import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_table
#ANALYSIS ETC
import pandas as pd
import datetime as dt
import numpy as np
import os
import io
import matplotlib.pyplot as plt
import datetime as dt
import webbrowser
from calendar import day_name
import ctypes 
import time
import base64
import PySimpleGUI as sg
import cufflinks as cf
#USER CREATED FUNCTIONS 
from fcn_Averages import DailyAverage, WeeklyAverage, MonthToDaySum, ConsumptionSummer
from fcn_plotting import character_removal, dataframe_chooser, Mbox, dash_solar_plotter
from fcn_Importing import xlsxReader_Monthly, Extension_Checker, Data_Consistency_Checker, intervalResampler, Data_Analyser, parse_contents
from fcn_loadshifting import load_shifter_average, load_shifter_long_list, solar_extractor_adder
from fcn_UTILS import dataJoiner, CopyCat, dataframe_list_generator, dataframe_compactor
#IMPORT USER DEFINED GLOBAL VARIABLES 
import config

from dash.dependencies import Input, Output #NEED TO ENSURE ONE CAN STORE DATA IN DCC.STORE

###### IMPORTING AND DEALING WITH SPOT PRICE 
# to go into function 
Price_filename = str(os.getcwd()) + '\\assets\\VIC1_SPOT_PRICE_2019.xlsx' # file name for VIC1 Spot print (2019)
VIC1_Price_Data_Raw = pd.read_excel(Price_filename) #read teh file , header=None
Data_Analyser(Price_file = VIC1_Price_Data_Raw, execute_price_analysis=True) #create daily/weekly averages



### MAIN - hacked together for now ###
config.Solar_Imported = False
plt.close('all') #ensure all windows are closed
image_filename = str(os.getcwd()) + '\\assets\\NEW_LOGO.jpg' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

##################////////////////// DASH \\\\\\\\\\\\\\\\\\################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([ ### LAYOUT FOR TABS - ACTUAL LAYOUT IS DEFINED INSIDE TAB CALLBSCKS###
    html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode())), #DISPLAY the NEW LOGO 
    dcc.Tabs(id='tabs-example', value='tab-1', children=[ #DISPLAY TABS
        dcc.Tab(label='Load Data', value='tab-1'),
        dcc.Tab(label='Site Graphs', value='tab-2'),
        dcc.Tab(label='Load Shifting', value='tab-3'),
        dcc.Tab(label='Excess Solar', value='tab-4'),
        dcc.Tab(label='Export Load Shift Data', value='tab-5'),
        dcc.Tab(label='Total Site Summation', value='tab-6'),
        dcc.Tab(label='Average Pricing', value='tab-7'),
        dcc.Tab(label='About', value='tab-99'),
    ]),
    html.Div(id='tabs-example-content')
])


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


### CALLBACK TESTING ###
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

if __name__ == '__main__': ## run the server
    webbrowser.open('http://127.0.0.1:8888/')  # open the DASH app in default webbrowser
    app.run_server(port=8888, debug=True)





  

