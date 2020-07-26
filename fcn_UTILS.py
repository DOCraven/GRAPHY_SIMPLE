import pandas as pd
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
            MergedDF['Excess Solar Generation'] = MergedDF['Solar Generation (kW)'] - MergedDF['Wodonga WTP'] #calculate the total excess generation AFTER WWTP has used available generation
            MergedDF['Excess Solar Generation'].clip(lower = 0, inplace = True) #replace all negative values with 0
        except KeyError: #if WWTP doesnt exist for some reason
            pass
        finalDF.append(MergedDF)
    
    return finalDF

def xlsxReader(xls_file_path): 
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

def intervalResampler(input_df, chosen_interval = 30):
    """
    function to change and interpolate to a given interval 
    """
    resampledDF = []
    Index_Name = 'Interval End'
    NumberofDataFrames = len(input_df)
    for x in  range(0, NumberofDataFrames):
        resampling_df = input_df[x] #each month
        resampling_df.set_index(Index_Name, inplace = True) #set the datetime index 
        resampling_df.resample('30T').interpolate(method = 'polynomial', order = 2, inplace = True) #interpolate the hourly interval data to 30 mins via linear interpolation   
        resampling_df.reset_index(inplace = True)
        resampledDF.append(resampling_df)

    return resampledDF

    