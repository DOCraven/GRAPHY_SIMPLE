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
        single_df_site = dataframe_to_shift[month] #SINGLE DATAFRAME W/ EXCESS SOLAR GENERATION FOR THE MONTH

        #create new dataframe only where consumption > PV availability        IE< NON SOLAR EXCESS HOURS / OUTSIDE SOLAR HOURS  (RETURNS NAN FOR HOURS WHERE SOLAR EXCESS EXISTS [ie, daytime])
        no_solar_hours_consumption = single_df_site.iloc[:,0].where(single_df_site.iloc[:,0] > single_df_site['Excess Solar Generation (Total)']) #change name it OUTSIDE

        #create new dataframe only where consumption < PV availability        IE< SOLAR EXCESS HOURS / INSIDE SOLAR HOURS   (RETURNS NAN FOR HOURS WHERE THERE IS NO SOLAR EXCESS [ie, night time hours])
        solar_hours_consumption = single_df_site.iloc[:,0].where(single_df_site.iloc[:,0] < single_df_site['Excess Solar Generation (Total)']) #change name to INSIDE

        # sum the total excess solar hours 
        solar_summed = solar_hours_consumption.sum() #total (summed) of NON SOLAR HOURS (ie, evening hours) 

        # scaling available excess solar by the total available 
        #add this to the summed NON SOLAR EXCESS load #CHANGE NAME TO INSIDE
        # (RETURNS NAN FOR HOURS WHERE THERE IS NO SOLAR EXCESS [ie, night time hours])
        solar_hours_consumption_ratio = solar_hours_consumption/solar_summed 

        ## shift NON EXCESS SOLAR hours by value_to_shift_percentage,           value is negative, as we want to TAKE AWAY these hours
        # multiply to get smaller number (ie, number to add to original dataframe) #change name to OUTSIDE
        no_solar_hours_consumption_scaled = no_solar_hours_consumption*value_to_shift_percentage*inverter 

        ### STEP 4 - sum total SHIFTED HOURS (ie, in NO EXCESS SOLAR [evening hours])
        summed = no_solar_hours_consumption_scaled.sum() #total kWh in NON SOLAR HOURS to shift
        summed_positive = summed*inverter #to give a positive number for dividing 

        #create a dataframe with consumption to ADD to each interval INSIDE SOLAR HOURS (IE, NAN for NON SOLAR HHOURS [ie, evening])
        #this is what we need to ADD to INSIDE SOLAR HOURS
        scaled_inside_solar_hours_consumption = solar_hours_consumption_ratio*summed_positive 

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
    # shifted_site_consumption = []
    inverter = -1 #used to invert the shifted hours when adding a negative, you minus - NEEDED


    ### STEP 1 - convert value_to_shift into % (ie, 20 = 0.2)
    value_to_shift_percentage = value_to_shift/100 
    shifted_sites_inc_solar = [site_to_shift, 'Excess Solar Generation (Total)'] #create new column for excess solar generation
    single_df_site = dataframe_to_shift.loc[:, shifted_sites_inc_solar] #slice the dataframe to only include the site under consideration and the total excess solar generation 
    
    ### STEP 2 - Generate solar and no solar hours 
    # create new dataframe only where consumption > PV availability        IE< NON SOLAR EXCESS HOURS / OUTSIDE SOLAR HOURS
    no_solar_hours_consumption = single_df_site.iloc[:,0].where(single_df_site.iloc[:,0] > single_df_site['Excess Solar Generation (Total)']) #change name it OUTSIDE

    #create new dataframe only where consumption < PV availability        IE< SOLAR EXCESS HOURS / INSIDE SOLAR HOURS
    solar_hours_consumption = single_df_site.iloc[:,0].where(single_df_site.iloc[:,0] < single_df_site['Excess Solar Generation (Total)']) #change name to INSIDE

    ### STEP 3 - sum solar hours, and determine ratio
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
    # shifted_site_consumption.append(shifted_inside_solar_hours)

    return shifted_inside_solar_hours

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

