import pandas as pd 
## file to define global variables ##

#interval data
Weekly_Interval_Data = []
Daily_Interval_Data = []
Monthly_Sum = []
Yearly_Sum = []
names = [] #placeholder for column headers (ie, site names) for interval data
chosen_site = ''

#pricing data
Daily_Pricing_Data = []
Weekly_Pricing_Data = []
Pricing_names = [] #placeholder for column headers for pricing data


Solar_Imported = False
Solar_Exists = False

Data_Uploaded = False

#figures - yes this is bad juju but I need it to work 
solar_figure_line = ''
solar_figure_summed = ''
yearly_summed_figure = ''


#importing stuff - related to parse_contents file 
Solar = pd.DataFrame() #empty dataframe for solar 
Consumption = pd.DataFrame() #empty dataframe for consumption  


reset_dataframes = False
number_of_files_uploaded = 0