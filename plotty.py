import pandas as pd
import cufflinks as cf
import matplotlib.pyplot as plt
import datetime as dt
import PySimpleGUI as sg
import xlsxwriter
import os



### THIS WILL PLOT AN EXCEL SPREADSHEET AS INPUT ###
### WILL REQUIRE MANUAL MANIPULATION ###
### IT IS DESIGNED FOR QUICK AND DIRTY PLOTTING, TO ENSURE A CONSISTENT LOOK FOR THE PROGRESS REPORT###

### HOW TO USE ###
# 1: INSERT YOUR spreadsheet name
# 2: set up for graph by choosing your x and y labels and title
# 3: pick your plot type


DATA_TO_PLOT_NAME =  'YOUR CSV OR XLSX.xlsx' #change this 
#make sure it is in the same directory as THIS FILE

DATA_TO_PLOT = pd.read_excel(DATA_TO_PLOT_NAME) #read data - dont change this 

### VARIABLES YOU NEED TO CHANGE ###
#titles
X_LABEL = 'This is a label on the X Axis!' #change this 
Y_LABEL = 'This is a label on the Y Axis!' #change this 
PLOT_TITLE = 'THIS IS THE PLOT TITLE' #change this 

#types of plot available#
#   - bar
#   - box
#   - histogram
#   - line plot (requires an extra step - See notes at end)


PLOT_TYPE = 'bar' #change this variable to change the plot type - more information here https://plotly.com/python/cufflinks/
PLOT_COLOUR = 'blue' #if you want to change the default colour. 

#The line below creates the data to be plotted as an object
# NOTE: TO PLOT A LINE GRAPH, YOU WILL NEED TO REMOVE `kind = 'PLOT_TYPE` from the line
fig = DATA_TO_PLOT.iplot(asFigure=True, xTitle=X_LABEL,yTitle=Y_LABEL, title=PLOT_TITLE, color="blue", kind = PLOT_TYPE) 

#this line outputs the actual code to your webrowser
fig.show() 

