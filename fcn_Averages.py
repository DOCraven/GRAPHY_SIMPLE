
import pandas as pd
import datetime as dt
# import cufflinks as cf
import numpy as np
import os
import matplotlib.pyplot as plt
import datetime as dt
from calendar import day_name
import PySimpleGUI as sg
#IMPORT USER DEFINED GLOBAL VARIABLES 
import cufflinks as cf
import config


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

def ConsumptionSummer(df_to_sum, sum_interval): 
    """ Function to sum the entire year, month, week and daily average data and return those numbers"""
    
    summed_consumption_data = []

    if sum_interval == 'MONTHLY': #sum each site and return a list of each month
        ### STEP 1: Sum data frame down the columns 
        for i in range(0, len(df_to_sum)): #iterate through each month (as given a list of dataframes)
            summed_consumption_data.append(df_to_sum[i].sum())

        return summed_consumption_data

    elif sum_interval == 'YEARLY': #sum the total kWh consumption for the year, and return a single dataframe 
        for i in range(0, len(df_to_sum)): #iterate through each month (as given a list of dataframes)
            summed_consumption_data.append(df_to_sum[i].sum()) #create a list of dataframes with the total summation for each site 

        for i in range(0, len(summed_consumption_data)): #iterate through each dataframe again
            summed_consumption_data[0] += summed_consumption_data[i]
            

    return summed_consumption_data[0].sort_values(ascending=False) #only return the first index of the list, sorted from Highest to Lowest