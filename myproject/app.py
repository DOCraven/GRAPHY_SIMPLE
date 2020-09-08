### USER DEFINED DASH FILES ###
from .server import app, server
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
import base64
import PySimpleGUI as sg
import cufflinks as cf
#USER CREATED FUNCTIONS 
from fcn_Averages import DailyAverage, WeeklyAverage, MonthToDaySum, ConsumptionSummer
from fcn_plotting import character_removal, dataframe_chooser, Mbox, dash_solar_plotter
from fcn_Importing import xlsxReader_Monthly, Extension_Checker, Data_Consistency_Checker, intervalResampler
from fcn_loadshifting import load_shifter_average, load_shifter_long_list, solar_extractor_adder
from fcn_UTILS import dataJoiner, CopyCat, dataframe_list_generator, dataframe_compactor
#IMPORT USER DEFINED GLOBAL VARIABLES 
import config



from dash.dependencies import Input, Output #NEED TO ENSURE ONE CAN STORE DATA IN DCC.STORE

### MAIN - hacked together for now ###
Solar_Imported = False
plt.close('all') #ensure all windows are closed

## Create the MAIN GUI LANDING PAGE ##
sg.theme('Light Blue 2')

layout_landing = [[sg.Text('NEW Landing Page')],
        [sg.Text('Please open your interval data (and if required, solar data) in XLS format')],
        [sg.Text('Interval Data', size=(10, 1)), sg.Input(), sg.FileBrowse()],
        [sg.Text('Solar Data', size=(10, 1)), sg.Input(), sg.FileBrowse()],
        [sg.Submit(), sg.Cancel()]]

window = sg.Window('NEW Graphy (Simple)', layout_landing) #open the window 

event, values = window.read()
window.close()

### AUTOMATICALLY load the data so I dont have to - FOR DEVELOPMENT ONLY 
# values = ['C:\\Scratch\\Python\\Simple_Graphy\\INPUT DATA\\test.xlsx', 'C:\\Scratch\\Python\\Simple_Graphy\\INPUT DATA\\SOLAR_REPRESENTATIVE_YEAR_60_MINUTES.xlsx']

try: #so I dont have to comment this out when automatically loading test data 
    if event == 'Cancel': 
        exit() #close the app
except NameError: 
    pass 


#ensure someone has uploaded a file 
if not values[0]: #nothing uploaded
    Mbox('UPLOAD ERROR', 'Please upload a CSV or XLSX file', 1) #spit out an error box 
    exit() #close the app

## STEP 1: Read the file 
try: #read the inverval load data and store it as a list of dataframes per month (ie, JAN = 0, FEB = 1 etc)
    Interval_Data = Extension_Checker(values[0]) #check to see if the interval load data is input is valid (ie, xlsx only)
except UnboundLocalError: 
    pass
try: #read the solar data
    if values[1]: #only read if solar data is input
        Solar_Imported = True #for data handling later on. 
        Solar_Data = Extension_Checker(values[1]) #check to see if Solar_data input is valid (ie, xlsx only)
except UnboundLocalError: 
    pass

## STEP 1A: join the solar data to the dataframe (if necessary)
if Solar_Imported: #combine Solar data to back of the interval load data if it exists - ALSO CALCULATES THE TOTAL CONSUMPTION - REQUIRED FOR LOAD SHIFTER
    Solar_Exists = True
    Full_Interval_Data = dataJoiner(Interval_Data, Solar_Data)
else: #does not combine the solar data to the back of the interval load data
    Full_Interval_Data = Interval_Data
    Solar_Exists = False

## STEP 2: Check for consistency, and interpolate to 30 minute intervals if requried
Checked_Interval_Data_0 = Data_Consistency_Checker(Full_Interval_Data)

## STEP 3: Copy dataframe (to get around an error of the dataframe being modifed by WeeklyAverage(), will fix properly later)
Checked_Interval_Data_1 = CopyCat(Checked_Interval_Data_0)

## STEP 4: Calculate Weekly averages
config.Weekly_Interval_Data = WeeklyAverage(Checked_Interval_Data_0) 
    
## STEP 5: Calculate Daily Averages
config.Daily_Interval_Data = DailyAverage(Checked_Interval_Data_1)

## STEP 6: Calculate summation of energy used (Yearly, monthly, weekly, daily)
config.Monthly_Sum = ConsumptionSummer(Checked_Interval_Data_1) #total average month (x12 months)

#########////////////////////////\\\\\\\\\\\\\\\\\\\\#################
print('succesfully loaded and did the backend stuff')

########## VARS SPECIFICALLY FOR DASH  ###############
names = list(config.Daily_Interval_Data[0].columns) #get the names of the column, assuming every name is the same across each dataframe in the list
chosen_site = '' #to make this VAR global
image_filename = str(os.getcwd()) + '\\assets\\NEW_LOGO.jpg' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

#create excess solar plots for DASH
if Solar_Exists: #only make this if the solar data has been uploaded
    solar_figure_summed = dash_solar_plotter(df_to_plot = config.Daily_Interval_Data, plot_type = 'bar' ) #make fancy figure 
    solar_figure_line = dash_solar_plotter(df_to_plot = config.Daily_Interval_Data, plot_type = 'line' ) #make fancy figure 


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
            html.H3('LOAD DATA GOES HERE'),






        ])
    
    elif tab == 'tab-2': #FANCY INTERVAL GRAPHS
        return html.Div([
            html.H3('Historical Energy Load Anaylsis Tool'), #quick graph
            dcc.Dropdown(id = 'Drop_Down_menu', #make selection menu
                options=[{'label':name, 'value':name} for name in names],
                value = names[0],#initial default selection upon loading 
                multi=False #do not allow multiple selections 
                ), 
            dcc.Graph(id='daily_graph'), #display daily graph
            dcc.Graph(id='weekly_graph'), #display weekly graph
        ])
    
    elif tab == 'tab-3': #LOAD SHIFTING SITE STUFF
        if Solar_Exists: 
            return html.Div([
                dcc.Store(id='memory_output'), #storing the selected site here
                dcc.Store(id='month_selection_output'), #storing the selected site here
                html.H3('Select a site to investigate'), 
                dcc.Dropdown(  #make drop down selection menu - STORING THIS BAD BOY IN THE DCC.STORE ABOVE
                    id = 'Shifted_Drop_Down_menu', #unique identifier for DASH Callbacks
                    options=[{'label':name, 'value':name} for name in names], #dynamically populating the list 
                    value = names[0],#initial default selection upon loading 
                    multi=False #do not allow multiple selections 
                    ), 
                
                html.P(''), #blank row 
                html.H3('Select a % to load shift by'), 
                dcc.Slider( #load shifting slider thingo 
                    id='shifting_slider', #unique identifier for DASH Callbacks
                    min=0,
                    max=50,
                    step=1,
                    value=0,
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
                html.P('Excess Solar'), #blank row 
                dcc.Graph(id='Daily Excess Summmed Solar - line ', figure = solar_figure_line), #display sum of all solar graph as a summed box per month
                ])
        else: 
            return html.H3("No Solar Data Uploaded")
        
    elif tab == 'tab-4': #EXCESS SOLAR DATA 
        if Solar_Exists: ## ie, user uploaded a solar file, so plot the nice and pretty graphs
            return html.Div([
                html.H3("Solar Data Uploaded"),
                dcc.Graph(id='Daily Excess Summmed Solar - line ', figure = solar_figure_line), #display all excess solar graph as a line graph per month
                dcc.Graph(id='Daily Excess Summmed Solar - bar', figure = solar_figure_summed), #display sum of all solar graph as a summed box per month

            ]) 
        else: 
            return html.H3("No Solar Data Uploaded")

    elif tab == 'tab-5': #EXPORT THE DATA TO A CSV - PLACEHOLDER - TO BE BUILT
            return html.Div([
                html.H3('Export Load Shift Data'),






            ])

    elif tab == 'tab-6': #ABOUT - FILL IN WITH THE README WHEN I HAVE TIME
            return html.Div([
                html.H3('About'),





                
            ])


### CALLBACK TESTING ###



if __name__ == '__main__': ## run the server
    webbrowser.open('http://127.0.0.1:8888/')  # open the DASH app in default webbrowser
    app.run_server(port=8888, debug=True)






