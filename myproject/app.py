### USER DEFINED DASH FILES ###
from .server import app, server
#DASH
import dash
from dash.dependencies import Input, Output, State #NEED TO ENSURE ONE CAN STORE DATA IN DCC.STORE
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
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
import cufflinks as cf
import flask
from rq import Queue
#USER CREATED FUNCTIONS 
from fcn_Averages import DailyAverage, WeeklyAverage, MonthToDaySum, ConsumptionSummer
from fcn_plotting import character_removal, dataframe_chooser, dash_solar_plotter
from fcn_Importing import xlsxReader_Monthly, Extension_Checker, Data_Consistency_Checker, intervalResampler, Data_Analyser, parse_contents
from fcn_loadshifting import load_shifter_average, load_shifter_long_list, solar_extractor_adder
from fcn_UTILS import dataJoiner, CopyCat, dataframe_list_generator, dataframe_compactor, dataframe_saver
#IMPORT USER DEFINED GLOBAL VARIABLES 
import config


#########################################
## CODE IS UP TO DATE AS OF 12/10/2020 ##
#########################################



###### IMPORTING AND DEALING WITH SPOT PRICE 
# file name for VIC1 Spot print (2019) (Pulling straight from GitHub for Heroku)
Price_URL = 'https://github.com/DOCraven/GRAPHY_SIMPLE/blob/master/assets/VIC1_SPOT_PRICE_2019.xlsx?raw=true'  
VIC1_Price_Data_Raw = pd.read_excel(Price_URL) #read teh file , header=None
# Data_Analyser(Price_file = VIC1_Price_Data_Raw, execute_price_analysis=True) #create daily/weekly averages of price file
Data_Analyser(Price_file = VIC1_Price_Data_Raw, execute_price_analysis=True) #create daily/weekly averages of price file

### SET UP PRICING DATA ###

config.spotPrices = pd.read_csv("INPUT Data/Spot Price.csv", index_col=0)
config.spotPrices.index = pd.to_datetime(config.spotPrices.index)


config.lossFactors = pd.read_csv("INPUT DATA/Loss Factors.csv", index_col=0)


config.networkTariffs = pd.read_csv("INPUT Data/Network Tariffs.csv")
config.networkTariffs['Tariff Structure'] = config.networkTariffs['Tariff Structure'].astype(str)
config.networkTariffs['Capacity ($/kVA/year)'] = config.networkTariffs['Capacity ($/kVA/year)'].fillna(0)
config.demandCapacity = pd.read_csv("INPUT DATA/Capacity Charges.csv")


config.tariffTypeExcel = pd.ExcelFile("INPUT DATA/Tariff Type.xlsx")

config.tariffType2 = pd.read_excel(config.tariffTypeExcel, sheet_name="Tariff2", index_col=0)

config.tariffType3 = pd.read_excel(config.tariffTypeExcel, sheet_name="Tariff3", index_col=0)
config.tariffType13 = pd.read_excel(config.tariffTypeExcel, sheet_name="Tariff13", index_col=0)
config.tariffType14 = pd.read_excel(config.tariffTypeExcel, sheet_name="Tariff14", index_col=0)
config.tariffTypeNDM = pd.read_excel(config.tariffTypeExcel, sheet_name="TariffNDM", index_col=0)
config.tariffTypeLLV = pd.read_excel(config.tariffTypeExcel, sheet_name="TariffLLV", index_col=0)
config.tariffTypeND5 = pd.read_excel(config.tariffTypeExcel, sheet_name="TariffND5", index_col=0)
config.facilityIndex = pd.read_excel(config.tariffTypeExcel, sheet_name="FacilityIndex", index_col=0)
config.timeOfUse = pd.read_excel(config.tariffTypeExcel, sheet_name="TOU", index_col=0)


### MAIN - hacked together for now ###
config.Solar_Imported = False
plt.close('all') #ensure all windows are closed
image_filename = str(os.getcwd()) + '\\assets\\NEW_LOGO.jpg' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

##################////////////////// DASH \\\\\\\\\\\\\\\\\\################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

server = app.server #PROCFILE must point to this. 

app.layout = html.Div([ ### LAYOUT FOR TABS - ACTUAL LAYOUT IS DEFINED INSIDE TAB CALLBSCKS###
    html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode())), #DISPLAY the NEW LOGO - commented out for heroku deployment
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
    if tab == 'tab-1': #LOAD DATA 
        return html.Div([
            html.H3('Load Interval Data'),
            #upload data
            html.P('Please upload consumption interval files.'),
            html.P('There is minimal error checking for number of data files uploaded. This may be added in future versions'),
            html.P('Please be aware that the program takes a little while to do the analysis in the background. Currently there is no loading animation. This may change in future versions. Please be patient, this is a work in progress'),
            dcc.Upload( #upload button
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
            ),
            html.Div(id='output-data-upload'), #show the data, and this needs to exist for the code to work for some reason. Prefer it it didn't


        ])
    
    elif tab == 'tab-2': #FANCY INTERVAL GRAPHS
        if config.Data_Uploaded: #only show if data is uploaded
            return html.Div([
                dcc.Store(id='tab1_month_selection_output', storage_type= 'session'), #storing the selected site here
                html.H3('Historical Energy Load Anaylsis Tool'), 
                dcc.Dropdown(id = 'Drop_Down_menu', #make selection menu
                    options=[{'label':name, 'value':name} for name in config.names], #dynamically create drop down menu contents
                    value = config.names[0],#initial default selection upon loading 
                    multi=False #do not allow multiple selections 
                    ), 
                 html.H3('Select a Month to Plot'), 
                    dcc.Dropdown( #monthly drop down 
                        id='tab1_month_selection',
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
                        value='January', #initial value is January
                        multi=True #allow more than one month to be selected at a time
                    ),
                dcc.Graph(id='daily_graph'), #display daily graph
                dcc.Graph(id='weekly_graph'), #display weekly graph
                
                
            ])
        else: #no data uploaded
            return html.Div([
                html.H3('Please upload interval data.')
            ])
    
    elif tab == 'tab-3': #LOAD SHIFTING SITE STUFF
        if config.Data_Uploaded: #only show if data is uploaded
            if config.Solar_Exists: #only show if solar is uploaded
                return html.Div([ #overaching layout
                    html.Div([ #should place the drop down and load shifter side by side, but it is currently broken. I suspect it has to do with external stylesheets
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


                    ]),
                    dcc.Store(id='memory_output', storage_type= 'session'), #storing the user selected site here
                    dcc.Store(id='month_selection_output', storage_type= 'session'), #storing the user selected month here
                   
                    html.P(''), #blank row 
                    html.H3('Select a Month to Plot'), 
                    dcc.Dropdown( #month selection plot
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
                        multi=True #allow multiple months to be selected
                    ),
                    ### EXPORTING BUTTON SAVES
                    html.Button('Export Average Load Shifted Data', id='Average_Save'),
                    html.Div(id='Average_File_Saved_Output',
                        children='Enter a value and press submit'),
                    html.Button('Export Yearly Load Shifted Data', id='Yearly_Save'),
                    html.Div(id='Yearly_File_Saved_Output',
                        children='Enter a value and press submit'),
                    
                    #display graph
                    dcc.Graph(id='shifting_slider_display'), #display the dynamically shifted graph upon update of slider 
                    html.P(' '), #blank row
                    
                    
                    html.H4('Excess Solar'), #blank row 
                    dcc.Graph(id='Daily Excess Summmed Solar - line ', figure = config.solar_figure_line), #display sum of all solar graph as a summed box per month
                    ])
            else: 
                return html.H3("No Solar Data Uploaded")
        else: #no consumption data uploaded
            return html.Div([
                html.H3('Please upload interval and/or solar')
            ]) 

    elif tab == 'tab-4': #EXCESS SOLAR DATA 
        if config.Data_Uploaded: #only show if data is uploaded
            if config.Solar_Exists: ## ie, user uploaded a solar file, so plot the nice and pretty graphs
                return html.Div([
                    html.H3("Solar Data Uploaded"),
                    dcc.Graph(id='Daily Excess Summmed Solar - line ', figure = config.solar_figure_line), #display all excess solar graph as a line graph per month
                    dcc.Graph(id='Daily Excess Summmed Solar - bar', figure = config.solar_figure_summed), #display sum of all solar graph as a summed box per month
                ]) 
            else: 
                return html.H3("No Solar Data Uploaded")
        
        else: #no consumption data uploaded
            return html.Div([
                html.H3('Please upload interval and/or solar')
            ])

    elif tab == 'tab-5': #EXPORT THE DATA TO A CSV - PLACEHOLDER - TO BE BUILT
        if config.Data_Uploaded: #only show if data is uploaded
                return html.Div([
                    html.H3('Export Load Shift Data'),
                ])
        
        else: #no consumption data uploaded
            return html.Div([
                html.H3('Please upload interval and/or solar')
            ])
    
    elif tab == 'tab-6': #YEARLY TOTALS PER SITE
            if config.Data_Uploaded: #only show if data is uploaded
                return html.Div([
                    html.H3('Yearly Site Consumption'),
                    dcc.Graph(id='Total Yearly Site Consumption - bar', figure = config.yearly_summed_figure) #pretty graph of summed yearly site consumption data 

                ])
            else: #no consumption data uploaded
                return html.Div([
                    html.H3('Please upload interval and/or solar')
                ])

    elif tab == 'tab-7': #Pricing Data
            if config.Data_Uploaded: #only show if data is uploaded
                return html.Div([
                    dcc.Store(id='pricing_month_selection_output', storage_type= 'session'), #storing the selected site here
                    html.H3('Pricing Data'),
                    dcc.Dropdown(id = 'Price_Drop_Down_menu', #make selection menu
                        options=[{'label':name, 'value':name} for name in config.Pricing_names], #dynamically create drop down menu contents
                        value = config.Pricing_names[0],#initial default selection upon loading 
                        multi=False #do not allow multiple selections 
                        ), 
                    html.H3('Select a Month to Plot'), 
                    dcc.Dropdown( #month selection
                        id='pricing_month_selection',
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
                        multi=False #allow multiple months
                    ),
                    
                    dcc.Graph(id='Price_daily_graph'), #display daily graph
                    
                    ])
            else: #no consumption data uploaded
                return html.Div([
                    html.H3('Please upload interval and/or solar')
                ])


    elif tab == 'tab-99': #ABOUT - FILL IN WITH THE README WHEN I HAVE TIME
            return html.Div([
                html.H3('About'),
                
            ])


### CALLBACK TESTING ###



if __name__ == '__main__': ## run the server
    # webbrowser.open('http://127.0.0.1:8888/')  # open the DASH app in default webbrowser
    app.run_server(debug=True)





  

