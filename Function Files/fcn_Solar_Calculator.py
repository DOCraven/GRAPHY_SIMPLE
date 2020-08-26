#a collection of functions to assist with calculating load during solar hours

#IMPORT USER DEFINED GLOBAL VARIABLES 
import config

import pandas as pd


def SolarOrganiser(monthly_data, startpost = None, finishpost = None):
    """
    Returns list of list of list of  the total sum of kWh per dataframe, total sum of kWh between start- and finish post, and percentage of start/finish post per month
    """ 
    Total_Day_Consumption = []
    Sliced_Day_Interval_Consumption = []
    Sliced_Day_Consumption = []
    Percentage_Consumption = []

    # try: 
    #     global NumberofDataFrames = len(monthly_data)
    # except TypeError: 
    #     pass 
    NumberofDataFrames = len(monthly_data)
    start_post = startpost
    finish_post = finishpost
    
    for x in range(0, NumberofDataFrames): # iterate through the list of dataframes
        Total_Day_Consumption.append(DaySummation(monthly_data[x])) # add all the consumption of load for the entire day
        Sliced_Day_Interval_Consumption.append(SolarSlicer(monthly_data[x], startpost = start_post, finishpost = finish_post)) #slice the day into a solar generation time 
        #(ie, start time finish time)
        Sliced_Day_Consumption.append(DaySummation(Sliced_Day_Interval_Consumption[x])) #add all the consumption for the load for the sliced (solar) day
        Percentage_Consumption.append((Sliced_Day_Consumption[x] / Total_Day_Consumption[x])*100) #convert to percentage of total daily consumption

    
    return Percentage_Consumption #all I care about is percentage consumption

def DaySummation(daily_data):
    """
    sums all the data in a daily average for monthly invertal data, and returns total load for that average day 
    ie, 24 hourly or 48 half hourly in, 1 number out
    """
    # will have to organise how the data is presented later
    # Totalsummation = []
    # NumberofDataFrames = len(monthly_data)
    # for x in range(0, NumberofDataFrames): # iterate through the list of dataframes
    #     Totalsummation.append(monthly_data[x].sum(axis = 0))   #sum the entire day and append to a dataframe for each month  - NOT SURE THIS IS CORRECT
    Totalsummation = daily_data.sum(axis = 0)  #sum the entire day and append to a dataframe for each month  - NOT SURE THIS IS CORRECT
    return Totalsummation 

def SolarSlicer(monthly_data, startpost = 18, finishpost = 34): #numbers align with times, 0000 = 0, 0030 = 1, 0100 = 2 etc. Thus, 0900 = 18 and 1700 = 34
    """Slices the daily interval data between the startpost and finish post
    only works with daily data (ie, 48xY dataframe)
    """
    # Sliced = []
    # NumberofDataFrames = len(monthly_data)
    # for x in range(0, NumberofDataFrames): # iterate through the list of dataframes
        # Sliced.append(monthly_data[x].iloc[startpost:finishpost, :]) #for slicing, returns every column and and every row between startpost and finishpost. will need to add in a dict to ensure timings 

    Sliced = monthly_data.iloc[startpost:finishpost, :] #for slicing, returns every column and and every row between startpost and finishpost. will need to add in a dict to ensure timings 

    return Sliced

def SolarPercentage():
    """ returns the solar consumption as a percentage of entire consumption"""





    return #nothing