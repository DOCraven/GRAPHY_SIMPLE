import pandas as pd
import ctypes
import cufflinks as cf
#IMPORT USER DEFINED GLOBAL VARIABLES 
import config


def character_removal(string_to_filter): 
    """Sanitises input characters to essentially select a substring between two \' characters"""
    chars_to_remove = ['[', ']', '\''] #list of characters we dont want
    filtered_list = []
    #determine if it is a list 
    if isinstance(string_to_filter, list): #if it is a list 
        for x in range(0, len(string_to_filter)): #iterate through each string
            for char in chars_to_remove: #filter through characters to remove
                string_to_filter[x] = string_to_filter[x].replace(char, '') #remove each character by replacing it with a '' value
            filtered_list.append(string_to_filter[x]) #append each filtered word to a new list
        return filtered_list #and return said list
        
    else: #not a list
        for char in chars_to_remove: #filter through chars to remove
            string_to_filter = string_to_filter.replace(char, '') #remove each character by replacing it with a '' value
    return string_to_filter #return it 

def dataframe_chooser(Daily_Interval_Data, chosen_site): 
    """
    function to dynamically slice columns and return a single dataframe from a given list of dataframes. 
    It returns every month for the chosen site. 
    """
    #list of the months to recreate the dataframe headers
    Months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'] 
    dynamically_created_dataframe = pd.concat([ # append all DF's into a single dataframe YES THIS IS JANNKY I WILL FIX IT LATER 
                            Daily_Interval_Data[0].loc[:, chosen_site], Daily_Interval_Data[1].loc[:, chosen_site],Daily_Interval_Data[2].loc[:, chosen_site],
                            Daily_Interval_Data[3].loc[:, chosen_site], Daily_Interval_Data[4].loc[:, chosen_site],Daily_Interval_Data[5].loc[:, chosen_site],
                            Daily_Interval_Data[6].loc[:, chosen_site], Daily_Interval_Data[7].loc[:, chosen_site],Daily_Interval_Data[8].loc[:, chosen_site],
                            Daily_Interval_Data[9].loc[:, chosen_site], Daily_Interval_Data[10].loc[:, chosen_site],Daily_Interval_Data[11].loc[:, chosen_site]], axis = 1) 
    dynamically_created_dataframe.columns = Months #insert month name as the respective header
    return dynamically_created_dataframe

def dash_solar_plotter(df_to_plot, plot_type): 
    """sum and plot the total solar consumption for each month"""
    ### VARS 
    chosen_site = 'Excess Solar Generation (Total)', #only plot the excess solar
    ### STEP 1 - Load the DF
    dataframe_to_plot = dataframe_chooser(df_to_plot, chosen_site), #dynamically create dataframes to plot 12x months on top of each other for the selected site 
    if plot_type == 'bar':
        ## STEP 2 - SUM the dataframe 
        summed_dataframe = dataframe_to_plot[0].sum(axis = 0) #sum along rows
        try: #create the figure to send to dash to plot
            figure = summed_dataframe.iplot(kind = 'bar', xTitle='Month', yTitle='Total Consumption (kWh)', title = 'SOLAR TEST', asFigure = True, theme="white"),
        except KeyError: #https://github.com/santosjorge/cufflinks/issues/180 - although waiting 0.5s before calling the 2nd graph seems to aboid this
            pass
        
        return figure[0] #it somehow makes itself a 1x1 list, and thus to return just the image one needs to index it. NFI why. 
    elif plot_type == 'line': #plot a line for each month
        try: #create the figure to send to dash to plot
            fig = dataframe_to_plot[0].iplot(kind = 'line', xTitle='Time', yTitle='Consumption (kWh)', title = chosen_site[0], asFigure = True, theme="white") 
        except KeyError: #https://github.com/santosjorge/cufflinks/issues/180 - although waiting 0.5s before calling the 2nd graph seems to aboid this
            pass

        return fig

