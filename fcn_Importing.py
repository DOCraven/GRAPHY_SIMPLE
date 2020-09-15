
import pandas as pd
import ctypes
import cufflinks as cf
import base64
import datetime as dt 
import io
#DASH DEPENDANCIES 
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
#USER CREATED FUNCTIONS 
from fcn_Averages import DailyAverage, WeeklyAverage, MonthToDaySum, ConsumptionSummer
from fcn_plotting import character_removal, dataframe_chooser, Mbox, dash_solar_plotter
from fcn_loadshifting import load_shifter_average, load_shifter_long_list, solar_extractor_adder
from fcn_UTILS import dataJoiner, CopyCat, dataframe_list_generator, dataframe_compactor
#IMPORT USER DEFINED GLOBAL VARIABLES 
import config




def xlsxReader_Monthly(dataframe_to_split): 
    """reads a given file (xls_file_path) and returns a list of DataFrames split into months
    Access said dataframe via indexing
    ie, JAN = 0
        FEB = 1
        ...
        DEC = 11
    """
    ### STEP 1 -  read the data without index files
    # data = pd.read_excel(xls_file_path, parse_dates = True, index_col = None) #reads entire df and parses dates without creating an index
    
    months = [g for n, g in dataframe_to_split.groupby(pd.Grouper(key='Interval End',freq='M'))] #splits it into months
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

def Data_Consistency_Checker(Dataframe_to_check):
    """Used to check if the dataframe is fully populated, and returns a interpolated dataframe is necessary"""
    
    ### STEP 1: Ensure all data is consistent (ie, exists)
    for x in  range(0, len(Dataframe_to_check)):
        if Dataframe_to_check[x].isnull().any().any(): #returns TRUE if NaN exists in teh dataframe
            Dataframe_to_check[x] = intervalResampler(Dataframe_to_check[x])
    
    return Dataframe_to_check

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

def Data_Analyser(consumption_interval, solar_interval = None): #solar can equal none because solar is not always passed to this function 
    """
    function to hold all the data anaylsis functions 
    """
    ## VARS ##
    # Interval_Data = [] #empty list for scope 
    # values = [consumption_interval, solar_interval] #dont need
## STEP 1: Read the file 
    try: #read the inverval load data and store it as a list of dataframes per month (ie, JAN = 0, FEB = 1 etc)
        # Interval_Data = Extension_Checker(values[0]) #check to see if the interval load data is input is valid (ie, xlsx only)
        Interval_Data = xlsxReader_Monthly(consumption_interval) #pass the entire year dataframe to a function that will return a dataframe for each month in a list 
    except UnboundLocalError: 
        pass
    try: #read the solar data
        if solar_interval: #only read if solar data is input
            config.Solar_Imported = True #for data handling later on. 
            Solar_Data = xlsxReader_Monthly(solar_interval) #check to see if Solar_data input is valid (ie, xlsx only)
    except UnboundLocalError: 
        pass

    ## STEP 1A: join the solar data to the dataframe (if necessary)
    if config.Solar_Imported: #combine Solar data to back of the interval load data if it exists - ALSO CALCULATES THE TOTAL CONSUMPTION - REQUIRED FOR LOAD SHIFTER
        config.Solar_Exists = True
        Full_Interval_Data = dataJoiner(Interval_Data, Solar_Data)
    else: #does not combine the solar data to the back of the interval load data
        Full_Interval_Data = Interval_Data
        config.Solar_Exists = False

    ## STEP 2: Check for consistency, and interpolate to 30 minute intervals if requried
    Checked_Interval_Data_0 = Data_Consistency_Checker(Full_Interval_Data)

    ## STEP 3: Copy dataframe (to get around an error of the dataframe being modifed by WeeklyAverage(), will fix properly later)
    Checked_Interval_Data_1 = CopyCat(Checked_Interval_Data_0)

    ## STEP 4: Calculate Weekly averages
    config.Weekly_Interval_Data = WeeklyAverage(Checked_Interval_Data_0) 
        
    ## STEP 5: Calculate Daily Averages
    config.Daily_Interval_Data = DailyAverage(Checked_Interval_Data_1)

    ## STEP 6: Calculate summation of energy used (Yearly, monthly, weekly, daily) and create figure
    config.Monthly_Sum = ConsumptionSummer(df_to_sum = Checked_Interval_Data_1, sum_interval = 'MONTHLY') #Total consumption for each site for each month (list of dataframes)
    config.Yearly_Sum = ConsumptionSummer(df_to_sum = Checked_Interval_Data_1, sum_interval = 'YEARLY') #total consumption for each site for the year (dataframe)

    #create plotly plot figure
    config.yearly_summed_figure = config.Yearly_Sum.iplot(kind = 'bar', xTitle='Site', yTitle='Total Consumption (kWh)', title = 'Yearly Consumption', asFigure = True) 
    #########////////////////////////\\\\\\\\\\\\\\\\\\\\#################
    print('succesfully loaded and did the backend stuff')

    ########## VARS SPECIFICALLY FOR DASH  ###############
    config.names = list(config.Daily_Interval_Data[0].columns) #get the names of the column, assuming every name is the same across each dataframe in the list
    config.chosen_site = '' #to make this VAR global
    

    #create excess solar plots for DASH
    if config.Solar_Exists: #only make this if the solar data has been uploaded
        config.solar_figure_summed = dash_solar_plotter(df_to_plot = config.Daily_Interval_Data, plot_type = 'bar' ) #make fancy figure 
        config.solar_figure_line = dash_solar_plotter(df_to_plot = config.Daily_Interval_Data, plot_type = 'line' ) #make fancy figure 

    return #nothing
    
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    #Pass each interval data to the respective CONSUMPTION or SOLAR dataframe
    # global config.Solar #make solar global 
    # global config.Consumption #make consumption global 
    if "SOLAR" in str(filename.upper()): #look for solar in the filename
        config.Solar = df #assume it is solar 
        print('reading solar input')
    else: 
        config.Consumption = df #else assume it is the Consumption data
        print('reading consumption input')
    ## Do the magic analysis here

    if not config.Consumption.empty and not config.Solar.empty: #ie, 2 files uploaded, pass both to the analysier function 

        #convert to global list of dataframes, and do the averaging etc for backend work 
        Data_Analyser(config.Consumption, config.Solar) #pass consumption data AND solar data
    
    elif not config.Consumption.empty and config.Solar.empty: #check that consumption data exists and solar does not. Pass only consumption data to the analyser

        #convert to global list of dataframes, and do the averaging etc for backend work 
        Data_Analyser(config.Consumption) #only pass the interval data


    return html.Div([ #display the data in the dash app for verification
        html.H5(filename),
        html.H6(dt.datetime.fromtimestamp(date)),

        dash_table.DataTable( #display the data in a table in the webbrowser
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),
        html.Hr(),  # horizontal line
    ])
