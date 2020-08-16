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

    #DASH STUFF 
    #https://github.com/facultyai/dash-bootstrap-components/tree/master/examples/multi-page-apps



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
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output




#external explicit function files
from fcn_GUI import GRAPH_GUI, GUI_Solar
from fcn_UTILS import dataJoiner, xlsxReader_Monthly, intervalResampler, Extension_Checker, Data_Consistency_Checker, CopyCat
from fcn_Solar_Calculator import DaySummation, SolarSlicer 
from fcn_Averages import DailyAverage, WeeklyAverage, MonthToDaySum, ConsumptionSummer
from dash_Graphs import Dash_App

def main():
    """ Main fcn"""
    
    ### VARS ###
    Solar_Exists = False
    plt.close('all') #ensure all windows are closed
    
    ## Create the MAIN GUI LANDING PAGE ##
    sg.theme('Light Blue 2')

    layout_landing = [[sg.Text('NEW Landing Page')],
            [sg.Text('Please open your interval data (and if required, solar data) in either XLS or CSV format')],
            [sg.Text('Interval Data', size=(10, 1)), sg.Input(), sg.FileBrowse()],
            [sg.Text('Solar Data', size=(10, 1)), sg.Input(), sg.FileBrowse()],
            [sg.Submit(), sg.Cancel()]]

    window = sg.Window('NEW Graphy (Simple)', layout_landing) #open the window 

    event, values = window.read()
    window.close()

    ## STEP 1: read files, check extensions are valid, and import as dataframes
    try: #read the inverval load data and store it as a list of dataframes per month (ie, JAN = 0, FEB = 1 etc)
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

    ## STEP 2: Check for consistency, and interpolate to 30 minute intervals if requried
    Checked_Interval_Data_0 = Data_Consistency_Checker(Full_Interval_Data)
        
    ## STEP 3: Copy dataframe (to get around an error of the dataframe being modifed by WeeklyAverage(), will fix properly later)
    Checked_Interval_Data_1 = CopyCat(Checked_Interval_Data_0)
    
    ## STEP 4: Calculate Weekly averages
    Weekly_Interval_Data = WeeklyAverage(Checked_Interval_Data_0)
        
    ## STEP 5: Calculate Daily Averages
    Daily_Interval_Data = DailyAverage(Checked_Interval_Data_1)

    ## STEP 6: Calculate summation of energy used (Yearly, monthly, weekly, daily)
    Monthly_Sum = ConsumptionSummer(Checked_Interval_Data_1) #total average month (x12 months)
   
    ## CREATE THE DASH APP, AND SEND THE DATA TOWARDS IT ##
    Dash_App(Daily_Interval_Data = Daily_Interval_Data, Weekly_Interval_Data = Weekly_Interval_Data, Monthly_Sum = Monthly_Sum)
    
    return #nothing main



### MAIN ###

main()



print('\nCODE \n C\n  O\n   M\n    P\n     L\n      E\n       T\n        E\n         D\n')


