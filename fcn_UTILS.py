import pandas as pd
import ctypes
import cufflinks as cf
import os
#IMPORT USER DEFINED GLOBAL VARIABLES 
import config

def dataJoiner(Full_df, incomplete_df):
    """
    function to join merge a smaller dataframe to a larger on, on a common index 
    """
    Index_Name = 'Interval End'
    finalDF = []
    
    NumberofDataFrames = len(Full_df)
    for x in  range(0, NumberofDataFrames):
        
        MergedDF = pd.merge(Full_df[x], incomplete_df[x], how = 'outer', on = Index_Name) #merges two dataframes on consistent "Interval End" names 
        # https://realpython.com/pandas-merge-join-and-concat/#pandas-merge-combining-data-on-common-columns-or-indices
        MergedDF.interpolate(method = 'polynomial', order = 2, inplace = True) #use linear interpolation to fill in the blank places
        try: 
            #clean up the dataframe, removing any column that is unnamed
            MergedDF.drop(MergedDF.columns[MergedDF.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True) 
            #sum all rows and give a total consumption for each half hour interval (WWTP and EXTERNAL SITES)
            MergedDF = pd.concat([MergedDF,pd.DataFrame(MergedDF.sum(axis=1),columns=['Total Consumption'])],axis=1) 
            #remove total solar consumption from the total summed
            MergedDF['Total Consumption'] = MergedDF['Total Consumption'] - MergedDF['Solar Generation (kW)']
            #calculate the total excess generation AFTER WWTP has used available generation
            MergedDF['Excess Solar Generation (WWTP)'] = MergedDF['Solar Generation (kW)'] - MergedDF['Wodonga WTP'] 
            #calculate the total excess generation AFTER WWTP has used available generation
            MergedDF['Excess Solar Generation (Total)'] = (MergedDF['Solar Generation (kW)'] - MergedDF['Total Consumption']) 
            #replace all negative values with 0
            MergedDF['Excess Solar Generation (WWTP)'].clip(lower = 0, inplace = True) 
            MergedDF['Excess Solar Generation (Total)'].clip(lower = 0, inplace = True) 
        except KeyError: #if WWTP doesnt exist for some reason
            pass
        finalDF.append(MergedDF)
    
    return finalDF

def CopyCat(dataframe_to_copy):
    """ Function to return a copy of a dataframe passed in """
    list_of_copied_dataframes = []
    for x in  range(0, len(dataframe_to_copy)):
        copied_dataframe = dataframe_to_copy[x].copy()
        list_of_copied_dataframes.append(copied_dataframe)
    
    return list_of_copied_dataframes

def dataframe_list_generator(non_list_dataframe): 
    """converts a single 12xN dataframe into a list containing 12 1xN dataframes by appending each indexed dataframe to the list """
    dataframe_headers = list(non_list_dataframe.columns) #get the names of the column, assuming every name is the same across each dataframe in the list
    listed_dataframes = []
    
    for name in range(0, len(dataframe_headers)): #iterate through each column 
        listed_dataframes.append(non_list_dataframe.loc[:, dataframe_headers[name]]) #isolate and append the column to its own dataframe in a list
    
    return listed_dataframes

def dataframe_compactor(dataframes_to_compact, yearly_data = False): 
    """takes in a list of len N of dataframes, and returns a single dataframe with N columns"""
    
    if not yearly_data: #
        index_names = list(dataframes_to_compact[0].index) #rip index from first dataframe  
        compacted_dataframe = pd.DataFrame(index = index_names) 
        column_to_drop = 'Excess Solar Generation (Total)'
    
        for month in range(0, len(dataframes_to_compact)): #iterate through each 
            dataframes_to_compact[month].drop(columns = column_to_drop, inplace = True) #remove the solar generarion for the respective month
            
        compacted_dataframe = pd.concat(dataframes_to_compact, axis = 1) #merge all of them into a single dataframe 
        return compacted_dataframe

    elif yearly_data: 
        compacted_dataframe = pd.DataFrame() #create empty dataframe
        compacted_dataframe = pd.concat(dataframes_to_compact, axis = 0) #merge all of them into a single dataframe - NO INDEX HERE
        compacted_dataframe.set_index('Interval End')
        return compacted_dataframe

def dataframe_saver(time_frame = 'Average'): 
    """
    function to save a given dataframe using dataframes already existing in memory from other functions 
    """
    #yes this is bad juju 

    # test is output directory exists
    file_save_location = os.getcwd() + '\\SHIFTED FILES'
    if not os.path.exists(file_save_location): #check to see if folder is created
     os.makedirs(file_save_location) #create folder if not created

    if time_frame == 'Average': #only save the average
        csv_save_name = config.plot_title + '.csv' #dymamically generated plot title
        csv_save_name = csv_save_name.replace(':', '-') #remove : sign to save it in windows
        csv_save_name = file_save_location +'\\' + csv_save_name.replace('%', 'PC') #remove % sign to save it in windows
        config.shifted_site_to_save.to_csv(csv_save_name) #save the whole year
    
    elif time_frame == 'Yearly': 
        csv_save_name = 'YEARLY ' + config.plot_title + '.csv' #dymamically generated plot title - bit janky for now, so we will have to fix it later
        csv_save_name = csv_save_name.replace(':', '-') #remove : sign to save it in windows
        csv_save_name = file_save_location +'\\' + csv_save_name.replace('%', 'PC') #remove % sign to save it in windows
        config.YEARLY_shifted_site.to_csv(csv_save_name) #save the whole year

    return #nothing



