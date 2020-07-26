import pandas as pd
import cufflinks as cf
import matplotlib.pyplot as plt
import datetime as dt
import PySimpleGUI as sg
import xlsxwriter

## MY FUNCTIONS ##
from fcn_Solar_Calculator import DaySummation, SolarSlicer, SolarOrganiser



def Solar_Plotter(df, TITLE = 'Percentage of Generation Between Two Set Points', X_LABEL = 'LOCATION', Y_LABEL = '% Of Generation'): 
    """plots box plots for the percentage of generation between two set points"""
    
    fig = df.iplot(asFigure=True, xTitle=X_LABEL, yTitle=Y_LABEL, title=TITLE, kind="bar", theme='white')
    fig.show() #show the figure in the default web browser

    return #nothing

def Average_Plotter(df = None, TITLE = 'DAILY MEAN', X_LABEL = 'Time', Y_LABEL = 'kWh', PLOTTYPE = 'Subplot'): #this is where things are plotted, will require _some_ manual manipulation until I make it nicer
    """ 
    Plots the given dataframe using cufflinks
    """
    ## determing the rows/columns for subplots, change this to output for your screen
    # plotting types
    #nice looking individual plot
    individual = False #for control 
    if PLOTTYPE == 'Individual':
        fig = df.iplot(asFigure=True, xTitle=X_LABEL, yTitle=Y_LABEL, title=TITLE, theme='white')
        individual = True
    elif PLOTTYPE == 'Bar':
        Plot_Kind = 'bar'
    elif PLOTTYPE == 'Histogram':
        # fig = df.iplot(asFigure=True, xTitle=X_LABEL, yTitle=Y_LABEL, title=TITLE, kind = 'histogram', theme='white')
        Plot_Kind = 'histogram'
    elif PLOTTYPE == 'Box':
        # fig = df.iplot(asFigure=True, xTitle=X_LABEL, yTitle=Y_LABEL, title=TITLE, kind = 'box', theme='white')
        Plot_Kind = 'box'
    elif PLOTTYPE == 'Heat':
        # fig = df.iplot(asFigure=True, xTitle=X_LABEL, yTitle=Y_LABEL, title=TITLE, kind = 'heat', theme='white')
        Plot_Kind = 'heat'
    elif PLOTTYPE == 'Spread':
        # fig = df.iplot(asFigure=True, xTitle=X_LABEL, yTitle=Y_LABEL, title=TITLE, kind = 'spread', theme='white')        
        Plot_Kind = 'spread'
    elif PLOTTYPE == 'Subplot': 
        Plot_Kind = 'subplot'
    else:
        print('Incorrect Plot Type')

    if not individual: 
        fig = df.iplot(asFigure=True, xTitle=X_LABEL, yTitle=Y_LABEL, title=TITLE, kind = Plot_Kind, theme='white')
    fig.show() #show the figure in the default web browser

    return #nothing

def GRAPH_GUI(Weekly_Mean = None, Daily_Mean = None): 
    """ 
    A simple GUI to make plotting easier and interactive 
    """
    ## VARS
    Months = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
    Interval = ('Daily', 'Weekly')
    Plot = ('Individual', 'Bar',  'Histogram', 'Box', 'Spread')
        
    NE_WATER_MONTHS = {0: 'JAN', 1: 'FEB', 2: 'MAR', 3: 'APR', 4: 'MAY', 5: 'JUN', 6: 'JUL', 7: 'AUG', 8: 'SEP', 9: 'OCT', 10: 'NOV', 11: 'DEC'} #dict for accessing months
    location = plottype = interval = month = year = None #so scope doesnt screw me. Could use a global var, but this is less typing


    #determining the layout
    layout = [  [sg.Text('', size = (20, None)), sg.Text('Plotting Options ', size = (20, None))], 
            [sg.Text('Pick a Month', size = (12, None)), sg.Listbox(Months, size=(20, len(Months)), key='Month')],
            [sg.Text('Pick a Data \nOutput Format', size = (12, None)), sg.Listbox(Interval, size=(20, len(Interval)), key='Interval')],
            [sg.Text('Pick a Plot Type', size = (12, None)), sg.Listbox(Plot, size=(20, len(Plot)), key='Plot Type')],
            [sg.Button('Plot'), sg.Button('Exit')]  ] #sg.Button('Save .CSV'), for future addon

    window = sg.Window('NE WATER GRAPHY', layout) #open the window

    while True: # so the window is peristent
        event, values = window.read() #keep waiting for a user input
        if event is None:
            break
        if event == 'Plot': #ie, plot button is pushed, so plot the selected time/date/average
            if values['Interval']: #determine the interval 
                selectedInterval = values['Interval']
                #do location logic
                if selectedInterval == ['Daily']: 
                    interval = 'Daily'
                elif selectedInterval == ['Weekly']:
                    interval = 'Weekly'
            else: 
                print('please select a interval type') #or different error

            if values['Plot Type']: #determine the Plot Type 
                selectedPlot = values['Plot Type']
                #do location logic
                if selectedPlot == ['Subplot']: 
                    plottype = 'Subplot'
                elif selectedPlot == ['Individual']:
                    plottype = 'Individual'
                elif selectedPlot == ['Bar']:
                    plottype = 'Bar'
                elif selectedPlot == ['Histogram']:
                    plottype = 'Histogram'
                elif selectedPlot == ['Box']:
                    plottype = 'Box'
                elif selectedPlot == ['Spread']:
                    plottype = 'Spread'
                elif selectedPlot == ['Heatmap']:
                    plottype = 'Heatmap'

            else: 
                print('please select a plot type') #or different error
                    
            #do month logic
            if values['Month']:    # Determine the month selected
                selectedMonth = values['Month']
                
                if selectedMonth == ['January']:
                    month = 0    
                elif selectedMonth == ['February']:
                        month = 1
                elif selectedMonth == ['March']:
                    month = 2
                elif selectedMonth == ['April']:
                    month = 3
                elif selectedMonth == ['May']:
                    month = 4
                elif selectedMonth == ['June']:
                    month = 5
                elif selectedMonth == ['July']:
                    month = 6
                elif selectedMonth == ['August']:
                    month = 7
                elif selectedMonth == ['September']:
                    month = 8
                elif selectedMonth == ['October']:
                    month = 9
                elif selectedMonth == ['November']:
                    month = 10
                elif selectedMonth == ['December']:
                    month = 11
            else: 
                print('please select a month')
            
            
            ## PLOTTING OCCURS HERE ##
            # if location == "External": 
            try: 
                if selectedInterval == ['Daily']: 
                    plotTitle = str(NE_WATER_MONTHS[month]) + ' DAILY MEAN CONSUMPTION'
                    Average_Plotter(Weekly_Mean[month], TITLE = plotTitle , PLOTTYPE = plottype) #daily average
                
                ## 2018 WEEKLY ##
                elif selectedInterval == 'Weekly': 
                    plotTitle = str(NE_WATER_MONTHS[month]) + ' WEEKLY MEAN CONSUMPTION'
                    Average_Plotter(Weekly_Mean[month], TITLE = plotTitle , PLOTTYPE = plottype) #weekly average

            except IndexError: 
                    pass

        
           
        elif event == 'Exit': #ie, exit button is pushed so quit 
            window.close()

        ### ONLY PLOTTING DATA ###
                ## 2019 DAILY ##


            
        
   
    window.close()

def GUI_Solar(DAILY_EXTERNAL_MEAN_2018 = None, DAILY_EXTERNAL_MEAN_2019 = None, DAILY_EXTERNAL_MEAN_2020 = None):
    """GUI to assist in plotting Solar Consumption Hours"""

    ### VARS ###
        ### VARS ###
    Start_Time = ['00:00', '00:30', '01:00', '01:30','02:00', '02:30','03:00', '03:30','04:00', '04:30','05:00', '05:30',
    '06:00', '06:30','07:00', '07:30','08:00', '08:30','09:00', '09:30','10:00', '10:30','11:00', '11:30',
    '12:00', '12:30','13:00', '13:30','14:00', '14:30','15:00', '15:30','16:00', '16:30','17:00', '17:30','18:00', '18:30',
    '19:00', '19:30','20:00', '20:30','21:00', '21:30','22:00', '22:30','23:00', '23:30'] #nasty way to determing input time
    Finish_Time = Start_Time #nasty way to determine output time, user selects input, and then code finds index location of matching input
    Year = ('2018', '2019', '2020')
    MONTHS = {0: 'JAN', 1: 'FEB', 2: 'MAR', 3: 'APR', 4: 'MAY', 5: 'JUN', 6: 'JUL', 7: 'AUG', 8: 'SEP', 9: 'OCT', 10: 'NOV', 11: 'DEC'} #dict for accessing months
    Start_Post = Finish_Post = selected_Start = selected_finish = 0 #initilising here, so scope doesnt screw me
    total_months = 12
    Plot = Export = False #to select whether to plot or export 

    ### LAYOUT ###
    layout = [  [sg.Text('', size = (20, None)), sg.Text('Daily Consumption Times ', size = (20, None))], 
            [sg.Text('Pick a year', size = (12, None)), sg.Listbox(Year, size=(20, len(Year)), key='Year')],
            [sg.Text('Start Time', size = (12, None)), sg.Listbox(Start_Time, size=(20, len(Start_Time)), key='Start_Time'), sg.Text('Finish Time', size = (12, None)), sg.Listbox(Finish_Time, size=(20, len(Finish_Time)), key='Finish_Time')],
            [sg.Button('Export'), sg.Button('Plot'), sg.Button('Exit')]] #sg.Button('Save .CSV'), for future addon

    window = sg.Window('NE WATER SOLAR HOURS', layout) #open the window

    ### STEP 2 - GET USER VALUES ###
    while True: #persistent window
        event, values = window.read() #read the GUI events
        if event is None:
            break
        if event == 'Export': #get whatever is selected when you press "GENERATE"
            Export = True
            if values['Start_Time']: #find the starting post
                
                selected_Start = values['Start_Time'] #this is a list, so you must index is accordingly
                Start_Post = Start_Time.index(selected_Start[0])
            else: 
                print('please select a Start Time')

                #do yearly logic
            if values['Year']:  #determine the year
                selectedYear = values['Year'] 
                #do year logic
                if selectedYear == ['2018']:
                    year = 2018
                elif selectedYear == ['2019']: 
                    year = 2019
                elif selectedYear == ['2020']:
                    year = 2020
            else: 
                print('please select a year')
            

            if values['Finish_Time']: #find the finish post
                selected_finish = values['Finish_Time']
                Finish_Post = Start_Time.index(selected_finish[0])
                ## error check ##
                if Finish_Post < Start_Post: 
                    print("ERROR: Please select a finishing time AFTER the starting time")
            else: 
                print('please select a Finish Time')
        
        
        ### LOGIC HAPPENS HERE ###
            ##LOGIC VARS##
        
       
        if event == 'Plot': #ie, plot button is pushed, so plot the selected time/date/average
            Plot = True
            if values['Start_Time']: #find the starting post
                selected_Start = values['Start_Time'] #this is a list, so you must index is accordingly
                Start_Post = Start_Time.index(selected_Start[0])
            else: 
                print('please select a Start Time')

                #do yearly logic
            if values['Year']:  #determine the year
                selectedYear = values['Year'] 
                #do year logic
                if selectedYear == ['2018']:
                    year = 2018
                elif selectedYear == ['2019']: 
                    year = 2019
                elif selectedYear == ['2020']:
                    year = 2020
            else: 
                print('please select a year')
            

            if values['Finish_Time']: #find the finish post
                selected_finish = values['Finish_Time']
                Finish_Post = Start_Time.index(selected_finish[0])
                ## error check ##
                if Finish_Post < Start_Post: 
                    print("ERROR: Please select a finishing time AFTER the starting time")
            else: 
                print("Error")

        if event == 'Exit':
            window.close()

        ## LOGIC GOES HERE ###

        save_folder = 'OUTPUT DATA\\'
        try:
            time_stamp = selected_Start[0] + '__' + selected_finish[0]
        except TypeError:
            time_stamp = 'ERROR'
        sanitized_time_stamp = time_stamp.replace(':', '.')
        

        if Export: #only save data
            if year == 2018: 
                Sliced_Consumption_Percentage_2018 = SolarOrganiser(DAILY_EXTERNAL_MEAN_2018, Start_Post, Finish_Post) #generate percentage
                writer = pd.ExcelWriter(save_folder + '2018_NE_WATER_SITE_PERCENTAGE ' + sanitized_time_stamp + '.xlsx', engine='xlsxwriter') #initilise the sheet writer
            
                for x in range (0, total_months): #iterate through each month 
                    Sliced_Consumption_Percentage_2018[x].to_excel(writer, sheet_name = MONTHS[x]) #save each dataframe into a new sheet

                writer.save() #close excel file and save

            elif year == 2019:
                Sliced_Consumption_Percentage_2019 = SolarOrganiser(DAILY_EXTERNAL_MEAN_2019, Start_Post, Finish_Post) #generate percentage
                writer = pd.ExcelWriter(save_folder + '2019_NE_WATER_SITE_PERCENTAGE ' + sanitized_time_stamp + '.xlsx', engine='xlsxwriter') #initilise the sheet writer
            
                for x in range (0, total_months): #iterate through each month 
                    Sliced_Consumption_Percentage_2019[x].to_excel(writer, sheet_name = MONTHS[x]) #save each dataframe into a new sheet
                
                writer.save() #close excel file and save

            elif year == 2020:
                Sliced_Consumption_Percentage_2020 = SolarOrganiser(DAILY_EXTERNAL_MEAN_2020, Start_Post, Finish_Post) #generate percentage
                writer = pd.ExcelWriter(save_folder + '2020_NE_WATER_SITE_PERCENTAGE ' + sanitized_time_stamp + '.xlsx', engine='xlsxwriter') #initilise the sheet writer

                for x in range (0, total_months): #iterate through each month 
                    Sliced_Consumption_Percentage_2020[x].to_excel(writer, sheet_name = MONTHS[x]) #save each dataframe into a new sheet

                writer.save() #close excel file and save

            Export = False

        if Plot: 
            if year == 2018: 
                Sliced_Consumption_Percentage_2018 = SolarOrganiser(DAILY_EXTERNAL_MEAN_2018, Start_Post, Finish_Post) #generate percentage
                for x in range(0, total_months): #plot 12 months at once
                    chosen_month = MONTHS[x] # converts integer month into string name of month via Months dict 

                    User_Title = chosen_month + ' ' + str(year) + ': Percentage of Generation Between ' + sanitized_time_stamp #procedurally geenerate 
                    Solar_Plotter(Sliced_Consumption_Percentage_2018[x], TITLE = User_Title )

            elif year == 2019:
                Sliced_Consumption_Percentage_2019 = SolarOrganiser(DAILY_EXTERNAL_MEAN_2019, Start_Post, Finish_Post) #generate percentage
                for x in range(0, total_months): #plot 12 months at once
                    chosen_month = MONTHS[x] # converts integer month into string name of month via Months dict 

                    User_Title = chosen_month + ' ' + str(year) + ': Percentage of Generation Between ' + sanitized_time_stamp #procedurally geenerate 
                    Solar_Plotter(Sliced_Consumption_Percentage_2019[x], TITLE = User_Title )
            
            elif year == 2020:
                Sliced_Consumption_Percentage_2020 = SolarOrganiser(DAILY_EXTERNAL_MEAN_2020, Start_Post, Finish_Post) #generate percentage
                for x in range(0, total_months): #plot 12 months at once
                    chosen_month = MONTHS[x] # converts integer month into string name of month via Months dict 

                    User_Title = chosen_month + ' ' + str(year) + ': Percentage of Generation Between ' + sanitized_time_stamp #procedurally geenerate 
                    Solar_Plotter(Sliced_Consumption_Percentage_2020[x], TITLE = User_Title )
            Plot = False

        
        elif event == 'Exit':
            window.close()
                    

    return #nothing
