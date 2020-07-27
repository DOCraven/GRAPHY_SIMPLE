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
# import cufflinks as cf
import numpy as np
import os
import matplotlib.pyplot as plt
import datetime as dt
from calendar import day_name
import PySimpleGUI as sg


## DASH ##

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px



#external explicit function files
from fcn_GUI import GRAPH_GUI, GUI_Solar
from fcn_UTILS import dataJoiner, xlsxReader, intervalResampler, Extension_Checker, Data_Consistency_Checker, CopyCat
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
    for months in  range(0, NumberofDataFrames): # sets each DF to have the correct index ## HERE BE PROBLEMS ##
        #recreate the vars
        Index_30mins = pd.date_range("00:00", "23:30", freq="30min").time #create timeserires with 30 minute intervals. Goes from 00:00 to 23:30 (ie, 48 entries)
        Time_DF = pd.DataFrame({'Interval End' : Index_30mins}) #convert the above timeseries (Time_DF) into a dataframe 

        #do some averaging 
        monthly_data[months] = monthly_data[months].set_index([columnName]) #set the index, as previous DF did not have have an index
        monthly_data[months].index = pd.to_datetime(monthly_data[months].index, unit='s') # some magic to make it not error out - 
        try: 
            monthly_data[months].drop(columns=['index'], inplace = True) #clean up the dataframe
        except KeyError: 
            pass
        averaged_bad_index =  (monthly_data[months].groupby([monthly_data[months].index.hour, monthly_data[months].index.minute]).mean()) #sum each days demand, 
        #     returns the mean of the hours over the month 
            # https://stackoverflow.com/a/30580906/13181119
        ### FIXING THE INDEX for later plotting ### - not the best but #yolo 
        try: #code errors out for some reason without this. Even though this will fail, it needs to "force" the dataframe to do something. It just works now
            averaged_bad_index.reset_index(inplace = True) #removes the index, reverts it to a 0 1 2 3 etc
        except ValueError: 
            pass

        averaged_bad_index.set_index('Interval End', inplace = True) #set the index to interval end (gets rid of the double up )
        averaged_bad_index.reset_index(inplace = True) #removes the index, reverts it to a 0 1 2 3 etc
        averaged_bad_index.drop(columns=['Interval End'], inplace = True) #drops the final 'Interval End' column 
        
        dailyAverage.append(Time_DF.join(averaged_bad_index)) #append the joined dataframe to the list of dataframes to return to main
        dailyAverage[months].set_index('Interval End', inplace = True) #create the interval end as the index
    
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
        try: 
            median.drop(columns=['index'], inplace = True) #clean up the dataframe
        except KeyError: 
            pass
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

    window = sg.Window('NEW Graphy (Simple)', layout_landing)

    event, values = window.read()
    window.close()

    # ProgressBar() #placeholder for progress/update bar while the fcn Data_Analysis is occuring

    ## STEP 1: read files, check extensions are valid, and import as dataframes
    try: #read the inverval load data
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

    
    ## STEP 2: Check for consistency, and interpolate if requried
    Checked_Interval_Data_0 = Data_Consistency_Checker(Full_Interval_Data)
        
    ## STEP 3: Copy dataframe (to get around an error of the dataframe being modifed by WeeklyAverage(), will fix properly later)
    Checked_Interval_Data_1 = CopyCat(Checked_Interval_Data_0)
    
    ## STEP 4: Calculate Weekly averages
    Weekly_Interval_Data = WeeklyAverage(Checked_Interval_Data_0)
        
    ## STEP 5: Calculate Daily Averages
  
    Daily_Interval_Data = DailyAverage(Checked_Interval_Data_1)

    ########################## DASHLY TEST #########################
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    # assume you have a "long-form" data frame
    # see https://plotly.com/python/px-arguments/ for more options
    
    names = Daily_Interval_Data[1].keys() #get column names 
    
    fig = px.line(Daily_Interval_Data[1],  x=Daily_Interval_Data[1].index.get_level_values(0), y= names,   title='Consumption1') #plot all the things
    Daily_Interval_Data[1].to_csv('plotting.csv')
    fig.show()

    # app.layout = html.Div(children=[
    #     html.H1(children='Test'),

    #     html.Div(children='''
    #         Dash: A web application framework for Python.
    #     '''),

    #     dcc.Graph(
    #         id='example-graph',
    #         figure=fig
    #     )
    # ])

    # if __name__ == '__main__':
    #     app.run_server(debug=False)

    ########################## DASHLY TEST #########################

    print('Hold')
    # GRAPH_GUI(Weekly_Mean = Weekly_Interval_Data, Daily_Mean = Daily_Interval_Data)

    

    
    ## STEP 3: PLOT IT NICELY 
    # Plotting_GUI()

    # layout = [[sg.Text('My one-shot window.')],      
    #              [sg.InputText()],      
    #              [sg.Submit(), sg.Cancel()]]      

    # window = sg.Window('Window Title', layout)    

    # event, values = window.read()    
    # window.close()

    # text_input = values[0]    
    # sg.popup('You entered', text_input)

    return #nothing main



### MAIN ###

main()



print('\nCODE \n C\n  O\n   M\n    P\n     L\n      E\n       T\n        E\n         D\n')


