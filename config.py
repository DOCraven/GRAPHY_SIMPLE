import pandas as pd 

## file to define global variables ##


Weekly_Interval_Data = []
Daily_Interval_Data = []
Monthly_Sum = []
Yearly_Sum = []
names = []
chosen_site = ''
Solar_Imported = False
Solar_Exists = False

Data_Uploaded = False

#figures - yes this is bad juju but I need it to work 
solar_figure_line = ''
solar_figure_summed = ''
yearly_summed_figure = ''


#importing stuff 
Solar = pd.DataFrame() #empty dataframe for solar 
Consumption = pd.DataFrame() #empty dataframe for consumption  
reset_dataframes = False
number_of_files_uploaded = 0