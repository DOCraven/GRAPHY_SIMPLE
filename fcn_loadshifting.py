import pandas as pd
import ctypes
import cufflinks as cf
#USER CREATED FUNCTIONS 
from fcn_UTILS import dataJoiner, CopyCat, dataframe_list_generator, dataframe_compactor
#IMPORT USER DEFINED GLOBAL VARIABLES 
import config



def load_shifter_average(dataframe_to_shift, value_to_shift):
    """
    dynamically load shifts a list of dataframes (ie, the averages) in solar hours by given value to shift
    returns a single df to make plotting easy. Scales thge shifted amount by available solar"""

    #### VARS ####
    shifted_site_consumption = []
    inverter = -1 #used to invert the shifted hours when adding a negative, you minus - NEEDED
    
    ### STEP 1 - convert value_to_shift into % (ie, 20 = 0.2)
    value_to_shift_percentage = value_to_shift/100 #t
    
    for month in range(0, len(dataframe_to_shift)): #iterate through each month in the list

        #isolate single dataframe to work on 
        single_df_site = dataframe_to_shift[month]

        #create new dataframe only where consumption > PV availability        IE< NON SOLAR EXCESS HOURS / OUTSIDE SOLAR HOURS
        no_solar_hours_consumption = single_df_site.iloc[:,0].where(single_df_site.iloc[:,0] > single_df_site['Excess Solar Generation (Total)']) #change name it OUTSIDE

        #create new dataframe only where consumption < PV availability        IE< SOLAR EXCESS HOURS / INSIDE SOLAR HOURS
        solar_hours_consumption = single_df_site.iloc[:,0].where(single_df_site.iloc[:,0] < single_df_site['Excess Solar Generation (Total)']) #change name to INSIDE

        # sum the total excess solar hours 
        solar_summed = solar_hours_consumption.sum() #total (summed) SOLAR GENERATION to shift

        # determine solar ratio by dividing half hourly solar generation by total solar generation 
        solar_hours_consumption_ratio = solar_hours_consumption/solar_summed #add this to the summed NON SOLAR EXCESS load #CHANGE NAME TO INSIDE

        ## shift NON EXCESS SOLAR hours by value_to_shift_percentage,           value is negative, as we want to TAKE AWAY these hours
        no_solar_hours_consumption_scaled = no_solar_hours_consumption*value_to_shift_percentage*inverter #multiple to get smaller number (ie, number to add to original dataframe) #change name to OUTSIDE

        ### STEP 4 - sum total SHIFTED HOURS (ie, in NO EXCESS SOLAR)
        summed = no_solar_hours_consumption_scaled.sum() #total kWh in NON SOLAR HOURS to shift
        summed_positive = summed*inverter #to give a positive number for dividing 

        #create a dataframe with consumption to ADD to each interval INSIDE SOLAR HOURS
        scaled_inside_solar_hours_consumption = solar_hours_consumption_ratio*summed_positive #this is what we need to ADD to INSIDE SOLAR HOURS

        #adding the scaled shifted consumption to the original solar hours 
        shifted_inside_solar_hours = solar_hours_consumption + scaled_inside_solar_hours_consumption 

        #take away the shifted load from the original 
        shifted_outside_solar_hours = no_solar_hours_consumption + no_solar_hours_consumption_scaled

        #combine the two dataframe 
        shifted_inside_solar_hours.update(shifted_outside_solar_hours)

        #append shifted dataframe to big list to return 
        shifted_site_consumption.append(shifted_inside_solar_hours)

    #convert list of dataframe to single dataframe 
    single_site_dataframe = dataframe_compactor(dataframes_to_compact = shifted_site_consumption) #converts the list of dataframes to a single dataframe 
    
      
    return single_site_dataframe

def load_shifter_long_list(dataframe_to_shift, value_to_shift, site_to_shift): #CURRENTLY JUST THE FIRST PASS VERSION - NEED TO UPDATE IT 
    """dynamically load shifts a single long dataframe (ie, a year) in solar hours by given value to shift"""

    #### VARS ####
    shifted_site_consumption = []
    ### STEP 1 - convert value_to_shift into % (ie, 20 = 0.2)
    value_to_shift_percentage = value_to_shift/100 
    shifted_sites_inc_solar = [site_to_shift, 'Excess Solar Generation (Total)']
    single_df_site = dataframe_to_shift.loc[:, shifted_sites_inc_solar] #slice the dataframe to only include the site under consideration and the total excess solar generation 
    
    ### STEP 2 - #populate new dataframe only where consumption < PV availability 
    no_solar_hours_consumption = single_df_site.iloc[:,0].where(single_df_site.iloc[:,0] > single_df_site['Excess Solar Generation (Total)']) 
        
    ### STEP 3 - shift NON EXCESS SOLAR hours by value_to_shift_percentage
    no_solar_hours_consumption_scaled = no_solar_hours_consumption*value_to_shift_percentage #multiply to get smaller number (ie, number to add to original dataframe)
    
    ### STEP 4 - sum total SHIFTED HOURS
    summed = no_solar_hours_consumption_scaled.sum() #total kWh to shift
    
    ### STEP 5 - divide TOTAL SUMMED hours by total EXCESS SOLAR HOURS 
    total_available_hours = no_solar_hours_consumption_scaled.isna().sum() #determine number of excess hours (as identified by being a NaN)
    individual_30_minute_block_scaled = summed/total_available_hours #what to add to each NaN
    
    ### STEP 6 - evenly add DIVIDED SUMMED TOTAL HOURS to each EXCESS SOLAR HOUR
    shifted_dataframe_solar_hours = single_df_site.iloc[:,0].where(single_df_site.iloc[:,0] < single_df_site['Excess Solar Generation (Total)']) 
    #identify which hours are available for adding in extra solar (ie, the inverse of no_solar_hours_consumption)
    shifted_dataframe_solar_hours +=individual_30_minute_block_scaled #add the evenly split shifted generation 

    ### STEP 7 - recreate new dataframe by subtracting SHIFTED HOURS and adding EXCESS SOLAR HOUR to each hour in the original dataframe  
    shifted_dataframe_no_solar_hours = no_solar_hours_consumption - no_solar_hours_consumption_scaled #dataframe of shifted NO SOLAR HOURS consumption
    
    shifted_dataframe_no_solar_hours.update(shifted_dataframe_solar_hours) #join the two dataframes as one
    
    return shifted_dataframe_no_solar_hours

def solar_extractor_adder(single_site, all_sites):
    """
    appends the solar generation to the chosen single site to plot and returns as a list of dataframes
    """
    ### VARS ###
    solar_added_dataframe = []
    column_to_extract = 'Excess Solar Generation (Total)'

    for month in range(0, len(all_sites)): #iterate through all sites 
        solar_generation = all_sites[month].loc[:, column_to_extract] #extract the solar generation and store as a column to add to the other dataframe

        solar_added_dataframe.append(pd.concat([single_site[month],  all_sites[month].loc[:, column_to_extract]], axis = 1)) #concat solar to the chosen individual month
    
    return solar_added_dataframe

