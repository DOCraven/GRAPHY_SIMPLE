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
        compacted_dataframe = pd.concat(dataframes_to_compact, axis = 0) #merge all of them into a single dataframe, axis = 0 
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


def dataframe_matcher(input_site):
    """
    function to align input names to output names 
    """
    chosen_site_OUTPUT_LIST = ['Yarrawonga Offtake Pump station', 
                                'Yarrawonga Wastewater Winter Storage - Irrigation', 
                                'Non Potable Offtake Water Pump Station (purple pipe)', 
                                'Wangaratta Kerr St Tanks', 
                                'Wangaratta Wastewater Purification Plant', 
                                'Myrtleford Buffalo Creek Sewer Pump Station', 
                                'Baranduda Low Level Water Pump Station', 
                                'Wodonga (Baranduda) Wastewater Purification Plant', 
                                'Mount Beauty Wastewater Purification Plant', 
                                'Bright Wastewater Purification Plant', 
                                'Wangaratta - Phillipson St Storage  Clear Water Pump Station', 
                                'Myrtleford Water Treatment Plant & Reservoir', 
                                'Corryong Water Treatment Plant - Water Storage 3', 
                                'Wodonga Head Office', 
                                'Bright Water Treatment Plant & Off stream storage', 
                                'Wodonga Raw Water Pump Station', 
                                'Wangaratta Offtake / Treatment Plant / Distribution Pumping', 
                                'Benalla Wastewater Purification Plant / Farm', 
                                'Bright Hawthorn Lane Sewer pump station', 
                                'Wangaratta Wastewater Purification Plant', 
                                'Wangaratta Swan St Sewer Pump Station', 
                                'Wangaratta Trade Waste Treatment Plant', 
                                'Wahgunyah Wastewater Purification Plant', 
                                'Wodonga Pump Station 01', 
                                'Wahgunyah Water Treatment Plant', 
                                'Wodonga High Level Water Pump Station', 
                                'Corryong Offtake Sewer Pump Station (Nariel Creek)', 
                                'Wodonga Water Treatment Plant', 
                                'Benalla Water Treatment Plant', 
                                'Myrtleford Wastewater Purification Plant - Area 2 (Depot)', 
                                'Yarrawonga Water Treatment Plant', 
                                'Wodonga West Wod Wastewater Purification Plant', 
                            ]
    
    chosen_site_INPUT_LIST = [
                                'River Road YARRAWONGA - kWh Consumption', 
                                'Beatties Road YARRAWONGA - kWh Consumption', 
                                '40 Bailey Street BUNDALONG - kWh Consumption', 
                                'Kerr Street WANGARATTA - kWh Consumption', 
                                'Detour Road WANGARATTA - kWh Consumption', 
                                'Buffalo Creek Road BUFFALO CREEK - kWh Consumption', 
                                'Murray Valley Highway BANDIANA   - kWh Consumption', 
                                '261 Whytes Road BARANDUDA  - kWh Consumption', 
                                'Embankment Dr MOUNT BEAUTY - kWh Consumption', 
                                'Back Porepunkah Rd BRIGHT - kWh Consumption', 
                                '228 Phillipson Street WANGARATTA - kWh Consumption', 
                                'Halls Road MYRTLEFORD - kWh Consumption', 
                                'Greenwattle Gap Road CORRYONG - kWh Consumption', 
                                '83 Thomas Mitchell Drive WODONGA - kWh Consumption', 
                                'Great Alpine Road FREEBURGH - kWh Consumption', 
                                'Mill Street WODONGA - kWh Consumption', 
                                'Faithful Street WANGARATTA - kWh Consumption', 
                                'Holdsworth Road BENALLA - kWh Consumption', 
                                'Hawthorn Lane BRIGHT - kWh Consumption', 
                                'Detour Road WANGARATTA - kWh Consumption', 
                                'Swan Street WANGARATTA - kWh Consumption', 
                                'Sandford Road WANGARATTA - kWh Consumption', 
                                'Back Wahgunyah Road WAHGUNYAH - kWh Consumption', 
                                'South Street WODONGA - kWh Consumption', 
                                'Cadel Terrace WAHGUNYAH - kWh Consumption', 
                                'Beechworth Road WODONGA - kWh Consumption', 
                                'Nariel Rd CUDGEWA - kWh Consumption', 
                                'Murray Valley Hwy BANDIANA MILPO - kWh Consumption', 
                                'Kilfera Road MOLYULLAH - kWh Consumption', 
                                'Great Alpine Road MYRTLEFORD - kWh Consumption', 
                                'Witt Street YARRAWONGA - kWh Consumption', 
                                'Wodonga WTP', 
                            ]
    
    if input_site ==  chosen_site_INPUT_LIST[0]:
        return chosen_site_OUTPUT_LIST[0]
    elif input_site ==  chosen_site_INPUT_LIST[1]:
        return chosen_site_OUTPUT_LIST[1]
    elif input_site ==  chosen_site_INPUT_LIST[2]:
        return chosen_site_OUTPUT_LIST[2]
    elif input_site ==  chosen_site_INPUT_LIST[3]:
        return chosen_site_OUTPUT_LIST[3]
    elif input_site ==  chosen_site_INPUT_LIST[4]:
        return chosen_site_OUTPUT_LIST[4]
    elif input_site ==  chosen_site_INPUT_LIST[5]:
        return chosen_site_OUTPUT_LIST[5]
    elif input_site ==  chosen_site_INPUT_LIST[6]:
        return chosen_site_OUTPUT_LIST[6]
    elif input_site ==  chosen_site_INPUT_LIST[7]:
        return chosen_site_OUTPUT_LIST[7]
    elif input_site ==  chosen_site_INPUT_LIST[8]:
        return chosen_site_OUTPUT_LIST[8]
    elif input_site ==  chosen_site_INPUT_LIST[9]:
        return chosen_site_OUTPUT_LIST[9]
    elif input_site ==  chosen_site_INPUT_LIST[10]:
        return chosen_site_OUTPUT_LIST[10]
    elif input_site ==  chosen_site_INPUT_LIST[11]:
        return chosen_site_OUTPUT_LIST[11]
    elif input_site ==  chosen_site_INPUT_LIST[12]:
        return chosen_site_OUTPUT_LIST[12]
    elif input_site ==  chosen_site_INPUT_LIST[13]:
        return chosen_site_OUTPUT_LIST[13]
    elif input_site ==  chosen_site_INPUT_LIST[14]:
        return chosen_site_OUTPUT_LIST[14]
    elif input_site ==  chosen_site_INPUT_LIST[15]:
        return chosen_site_OUTPUT_LIST[15]
    elif input_site ==  chosen_site_INPUT_LIST[16]:
        return chosen_site_OUTPUT_LIST[16]
    elif input_site ==  chosen_site_INPUT_LIST[17]:
        return chosen_site_OUTPUT_LIST[17]
    elif input_site ==  chosen_site_INPUT_LIST[18]:
        return chosen_site_OUTPUT_LIST[18]
    elif input_site ==  chosen_site_INPUT_LIST[19]:
        return chosen_site_OUTPUT_LIST[19]
    elif input_site ==  chosen_site_INPUT_LIST[20]:
        return chosen_site_OUTPUT_LIST[20]
    elif input_site ==  chosen_site_INPUT_LIST[21]:
        return chosen_site_OUTPUT_LIST[21]
    elif input_site ==  chosen_site_INPUT_LIST[22]:
        return chosen_site_OUTPUT_LIST[22]
    elif input_site ==  chosen_site_INPUT_LIST[23]:
        return chosen_site_OUTPUT_LIST[23]
    elif input_site ==  chosen_site_INPUT_LIST[24]:
        return chosen_site_OUTPUT_LIST[24]
    elif input_site ==  chosen_site_INPUT_LIST[25]:
        return chosen_site_OUTPUT_LIST[25]
    elif input_site ==  chosen_site_INPUT_LIST[26]:
        return chosen_site_OUTPUT_LIST[26]
    elif input_site ==  chosen_site_INPUT_LIST[27]:
        return chosen_site_OUTPUT_LIST[27]
    elif input_site ==  chosen_site_INPUT_LIST[28]:
        return chosen_site_OUTPUT_LIST[28]
    elif input_site ==  chosen_site_INPUT_LIST[29]:
        return chosen_site_OUTPUT_LIST[29]
    elif input_site ==  chosen_site_INPUT_LIST[30]:
        return chosen_site_OUTPUT_LIST[30]
    elif input_site ==  chosen_site_INPUT_LIST[31]:
        return chosen_site_OUTPUT_LIST[31]
    elif input_site ==  chosen_site_INPUT_LIST[32]:
        return chosen_site_OUTPUT_LIST[32]
 

    #END OF FCN