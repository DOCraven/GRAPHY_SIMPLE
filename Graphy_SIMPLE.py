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
import cufflinks as cf
import numpy as np
import os
import matplotlib.pyplot as plt
import datetime as dt
from calendar import day_name
# import PySimpleGUIWeb as sg

import PySimpleGUI as sg
#external explicit function files
from fcn_GUI import GRAPH_GUI, GUI_Solar
from fcn_UTILS import dataJoiner, xlsxReader, intervalResampler
from fcn_Solar_Calculator import DaySummation, SolarSlicer 

### FUNCTIONS ###
def DailyAverage(monthly_data):
    """
    Takes a dataframe of monthly data, and returns an average (mean) day for that month.
    30 days in, 1 day out  
    """
    dailyAverage = [] # Average Day from the input
    columnName = 'Interval End' #name of column that contains Parsed DateTimeObject
    NumberofDataFrames = len(monthly_data)
    for months in  range(0, NumberofDataFrames): # sets each DF to have the correct index
        monthly_data[months] = monthly_data[months].set_index([columnName]) #set the index, as previous DF did not have have an index
        monthly_data[months].index = pd.to_datetime(monthly_data[months].index, unit='s') # some magic to make it not error out - 
        dailyAverage.append(monthly_data[months].groupby([monthly_data[months].index.hour, monthly_data[months].index.minute]).mean()) #sum each days demand, 
        #     returns the mean of the hours over the month 
            # https://stackoverflow.com/a/30580906/13181119
    
    return dailyAverage

def WeeklyAverage(monthly_data):
    """
    Takes a list of dataframes (12x) and returns the average for each week
    30 days in, 7 day out
    as a list of dataframes  
    """
    ## VARS
    fullDateColumnName = 'Interval End' #name of column that contains Parsed DateTimeObject
    WeeklyAverage = []
    day_index = [ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'] #needed for sorting the dataframe into specific days
    
    # Convert monthly datatime into NAME OF DAY and TIME 
    NumberofDataFrames = len(monthly_data)
    
    for months in  range(0, NumberofDataFrames): # iterate through the list of dataframes
        monthly_data[months].reset_index(inplace = True) #remove index to stop it from erroring out with INDEX_ERROR
        monthly_data[months]['TIME'] = monthly_data[months][fullDateColumnName].dt.time #splits time, throws it at the end  
            
        time_temp =  monthly_data[months]['TIME'] #creates new dataframe called TIME for each iteration through the for loop

        monthly_data[months].drop(labels=['TIME'], axis=1,inplace = True) #drops the DATE and TIME from the end of the dataframe
        monthly_data[months].insert(0, 'TIME', time_temp) #inserts TIME at the beginning of the dataframe
            # https://stackoverflow.com/a/25122293/13181119
        
        monthly_data[months]['DAY'] = monthly_data[months][fullDateColumnName].dt.day_name() # get the DAY NAME from datetime object (ie, MONDAY, TUESDAY etc)
            # https://stackoverflow.com/a/30222759/13181119

        dayofweek_temp = monthly_data[months]['DAY'] #new dataframe of day names, to replace DATE with
        
        monthly_data[months].drop(labels=['DAY', fullDateColumnName], axis=1,inplace = True) #drops the DAY column from the end of the dataframe
        monthly_data[months].insert(0, 'DAY', dayofweek_temp) #inserts DAY_OF_WEEK at the beginning of the dataframe
        
    ## DO SOME FANCY MATHS HERE ##
    for months in  range(0, NumberofDataFrames): #iterate through each month
        sorted = monthly_data[months] #temp dataframe to make sorting it easier 
        sorted['DAY'] = pd.Categorical(sorted['DAY'], categories = day_index, ordered = True) #look, some magic happens here, not entirely sure 
            #what the go is. This is the SO reference #https://stackoverflow.com/a/39223389/13181119

        median = sorted.groupby(['DAY', 'TIME']).median() #find the median grouping by DAY and TIME
        WeeklyAverage.append(median) #append to a list of dataframes, and return this to the main function
    
    return WeeklyAverage

def MonthToDaySum(df):
    """
    Sums up the entire DF for the month, returns a total energy consumption for each day of the month, as a % of the highest load in each site
    """
    sampled = [] #empty array
    NumberofDataFrames = len(df)
    
    for months in  range(0, NumberofDataFrames): # iterate through the list of dataframes
        SUMMED = df[months].resample("1D").sum() #sum each days demand 
        SUMMED = df[months].apply(lambda x: x.div(x.max())) #magic lambda function from Sean, divdes X by the max of X, making it into percentages
        sampled.append(SUMMED) #append to all 
            
    return sampled

def main():
    """ Main fcn"""
    plt.close('all')
    
    ## VARS ##
    cwd = os.getcwd()
    Input_Folder = cwd + '\\INPUT DATA\\'
    if not os.path.exists(cwd + '\\OUTPUT DATA\\'):
        os.mkdir(cwd + '\\OUTPUT DATA\\')
    startMSG = ('\nNE WATER DATA ANALYSIS TOOL\n\nThis code takes about a minute to run\nPlease be patient\n\n\n')
    print(startMSG)
    
   
      
    GENERATION_HOURS = CONSUMPTION_PROFILES = False #to choose things
    layout = [  [sg.Text('', size = (20, None)), sg.Text('NE WATER LANDING PAGE ', size = (40, None))], 
            [sg.Button('GENERATION HOURS'), sg.Button('AVERAGE CONSUMPTION PROFILES'), sg.Button('Exit')]] #Landing page, not made a function so I dont have to pass bulk values to it. Will fix shortly

    window = sg.Window('NE WATER LANDING PAGE', layout) #determine the window layout
    
    while True: #persistent window
        event, values = window.read() #read the GUI events

        if event == 'GENERATION HOURS': #choose to plot hours between user defined points
            GENERATION_HOURS = True
        elif event == 'AVERAGE CONSUMPTION PROFILES': #choose to make 
            CONSUMPTION_PROFILES = True
        elif event == 'Exit': 
            window.close() #close the window
            break #break the persistent loop
        ## CHOOSING WHAT TO PLOT ##
        if GENERATION_HOURS: 
            GUI_Solar(DAILY_EXTERNAL_MEAN_2018, DAILY_EXTERNAL_MEAN_2019, DAILY_EXTERNAL_MEAN_2020) #, DAILY_EXTERNAL_MEAN_2019, DAILY_EXTERNAL_MEAN_2020
            GENERATION_HOURS = False
        elif CONSUMPTION_PROFILES: 
            GRAPH_GUI(DAILY_EXTERNAL_MEAN_2018, DAILY_EXTERNAL_MEAN_2019, DAILY_EXTERNAL_MEAN_2020, WEEKLY_EXTERNAL_MEDIAN_2018, WEEKLY_EXTERNAL_MEDIAN_2019, WEEKLY_EXTERNAL_MEDIAN_2020, DAILY_WWTP_MEAN_2019, DAILY_WWTP_MEAN_2020, WEEKLY_WWTP_MEDIAN_2019, WEEKLY_WWTP_MEDIAN_2020) #need to clean up everything I'm passing to this function
            CONSUMPTION_PROFILES = False
    

    return #nothing main



### MAIN ###

main()



print('\nCODE \n C\n  O\n   M\n    P\n     L\n      E\n       T\n        E\n         D\n')


