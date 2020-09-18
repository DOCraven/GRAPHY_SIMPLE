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
# Price_filename = str(os.getcwd()) + '\\assets\\VIC1_SPOT_PRICE_2019.xlsx' # file name for VIC1 Spot print (2019) 

# file name for VIC1 Spot print (2019) (Pulling straight from GitHub for Heroku)
Price_URL = 'https://github.com/DOCraven/GRAPHY_SIMPLE/blob/master/assets/VIC1_SPOT_PRICE_2019.xlsx?raw=true'  
VIC1_Price_Data_Raw = pd.read_excel(Price_URL) #read teh file , header=None
Data_Analyser(Price_file = VIC1_Price_Data_Raw, execute_price_analysis=True) #create daily/weekly averages



### MAIN - hacked together for now ###
config.Solar_Imported = False
plt.close('all') #ensure all windows are closed
# image_filename = str(os.getcwd()) + '\\assets\\NEW_LOGO.jpg' # replace with your own image
# image_filename = '/assets/NEW_LOGO.jpg' # replace with your own image
# encoded_image = base64.b64encode(open(image_filename, 'rb').read())

##################////////////////// DASH \\\\\\\\\\\\\\\\\\################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app = app.server

app.layout = html.Div([ ### LAYOUT FOR TABS - ACTUAL LAYOUT IS DEFINED INSIDE TAB CALLBSCKS###
    # html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode())), #DISPLAY the NEW LOGO 
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



### CALLBACK TESTING ###
if __name__ == '__main__': ## run the server
    # webbrowser.open('http://127.0.0.1:8888/')  # open the DASH app in default webbrowser
    app.run_server(debug=True)





  

