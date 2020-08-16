import pandas as pd
import ctypes
# import datetime as dt
# import numpy as np
# import datetime as dt
# from calendar import day_name

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

def xlsxReader_Monthly(xls_file_path): 
    """reads a given file (xls_file_path) and returns a list of DataFrames split into months
    Access said dataframe via indexing
    ie, JAN = 0
        FEB = 1
        ...
        DEC = 11
    """
    ### STEP 1 -  read the data without index files
    data = pd.read_excel(xls_file_path, parse_dates = True, index_col = None) #reads entire df and parses dates without creating an index
    
    months = [g for n, g in data.groupby(pd.Grouper(key='Interval End',freq='M'))] #splits it into months
        # is a list, so just access each list as an index (ie, JAN = 0, FEB = 1)
        # https://stackoverflow.com/a/49491178/13181119
    
    return months

def Extension_Checker(file_name_to_check):
    """ used to check if the extension is a xls(x) or a csv, or returns an error if not"""
    if file_name_to_check.endswith('.xls') or file_name_to_check.endswith('.xlsx'): #open via xls reader
        try: 
            read_file = xlsxReader_Monthly(file_name_to_check)
        except AttributeError: 
            pass
    elif file_name_to_check.endswith('.csv') or file_name_to_check.endswith('.xlsx'): #open via csv reader
        print('PLEASE ENSURE FILE IS A \'XLSX\' ONLY') #make this a bit better later
    else: 
        print('ERROR') #make this a bit better later
    
    return read_file

def intervalResampler(input_df, chosen_interval = 30):
    """
    function to change and interpolate dataframe to a given interval 
    """
    
    Index_Name = 'Interval End'
    # resampling_df = input_df #each month
    input_df.set_index(Index_Name, inplace = True) #set the datetime index 
    resampledDF = input_df.resample('30T').interpolate(method = 'polynomial', order = 2) #interpolate the hourly interval data to 30 mins via linear interpolation   , inplace = True
    resampledDF.reset_index(inplace = True)
    
    return resampledDF

def Data_Consistency_Checker(Dataframe_to_check):
    """Used to check if the dataframe is fully populated, and returns a interpolated dataframe is necessary"""
    
    ### STEP 1: Ensure all data is consistent (ie, exists)
    for x in  range(0, len(Dataframe_to_check)):
        if Dataframe_to_check[x].isnull().any().any(): #returns TRUE if NaN exists in teh dataframe
            Dataframe_to_check[x] = intervalResampler(Dataframe_to_check[x])
    
    return Dataframe_to_check

def CopyCat(dataframe_to_copy):
    """ Function to return a copy of a dataframe passed in """
    list_of_copied_dataframes = []
    for x in  range(0, len(dataframe_to_copy)):
        copied_dataframe = dataframe_to_copy[x].copy()
        list_of_copied_dataframes.append(copied_dataframe)
    
    return list_of_copied_dataframes

def character_removal(string_to_filter): 
    chars_to_remove = ['[', ']', '\'']
    filtered_list = []
    #determine if it is a list 
    if isinstance(string_to_filter, list): #if it is a list 
        for x in range(0, len(string_to_filter)): #iterate through lenghth of list
            for char in chars_to_remove: #filter through characters to remove
                string_to_filter[x] = string_to_filter[x].replace(char, '') #remove each character
            filtered_list.append(string_to_filter[x]) #append each filtered word to a new
        return filtered_list #return it 
        
    else: #not a list
        for char in chars_to_remove: #filter through chars to remove
            string_to_filter = string_to_filter.replace(char, '') #remove the char by replacing it with nothing
    return string_to_filter #return it 

def dataframe_chooser(Daily_Interval_Data, chosen_site): 
    """function to dynamically slice columns and create a new dataframe from a list of dataframes"""
    Months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'] #list of the months to access things later
    dynamically_created_dataframe = pd.concat([Daily_Interval_Data[0].loc[:, chosen_site], Daily_Interval_Data[1].loc[:, chosen_site],Daily_Interval_Data[2].loc[:, chosen_site],
                            Daily_Interval_Data[3].loc[:, chosen_site],Daily_Interval_Data[4].loc[:, chosen_site],Daily_Interval_Data[5].loc[:, chosen_site],
                            Daily_Interval_Data[6].loc[:, chosen_site],Daily_Interval_Data[7].loc[:, chosen_site],Daily_Interval_Data[8].loc[:, chosen_site],
                            Daily_Interval_Data[9].loc[:, chosen_site],Daily_Interval_Data[10].loc[:, chosen_site],Daily_Interval_Data[11].loc[:, chosen_site]], axis = 1) # append all DF's into a single dataframe YES THIS IS JANNKY I WILL FIX IT LATER 
    dynamically_created_dataframe.columns = Months #make the column names line up 

    return dynamically_created_dataframe

def Mbox(title, text, style):
    """ERROR BOX FUNCTION POP UP WINDOW"""
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)