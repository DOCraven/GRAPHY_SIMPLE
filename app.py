### libraries

import pandas as pd
import datetime as dt
import numpy as np
import os
import matplotlib.pyplot as plt
import datetime as dt
import webbrowser
from calendar import day_name
import ctypes  # An included library with Python install.
import time

## USER DEFINED FUNCTIONS ##
from fcn_UTILS import dataJoiner, xlsxReader_Monthly, intervalResampler, Extension_Checker, Data_Consistency_Checker, CopyCat, load_shifter, dataframe_chooser, solar_extractor_adder, dataframe_list_generator, dash_solar_plotter, character_removal

## DASH ##

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output





def Dash_App(Daily_Interval_Data, Weekly_Interval_Data, Monthly_Sum, Solar_Exists = False): 
    """ file to create the nice sidebar dash app thingo"""


    ########## VARS ###############
    names = list(Daily_Interval_Data[0].columns) #get the names of the column, assuming every name is the same across each dataframe in the list
    chosen_site = '' #to make this VAR global
    

    if Solar_Exists: #only make this if the solar data has been uploaded
        solar_figure = dash_solar_plotter(Daily_Interval_Data) #make fancy figure 

    ####################### DASH GOES HERE ####################### 
    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

    # the style arguments for the sidebar. We use position:fixed and a fixed width
    SIDEBAR_STYLE = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "16rem",
        "padding": "2rem 1rem",
        "background-color": "#f8f9fa",
    }

    # the styles for the main content position it to the right of the sidebar and
    # add some padding.
    CONTENT_STYLE = {
        "margin-left": "18rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem",
    }

    sidebar = html.Div(
        [
            html.H2("NEW Graphy", className="display-4"),
            html.Hr(),
            html.P(
                "A historical load data analysis tool", className="lead"
                ),
            dbc.Nav(
                [
                    dbc.NavLink("Site Graphs", href="/page-1", id="page-1-link"),
                    dbc.NavLink("Load Shifting Site Graphs", href="/page-2", id="page-2-link"),
                    dbc.NavLink("Excess Solar Hours", href="/page-3", id="page-3-link"),
                    dbc.NavLink("About", href="/page-99", id="page-99-link"),
                ],
                vertical=True,
                pills=True,
                ),
            ],
        style=SIDEBAR_STYLE,
    )

    content = html.Div(id="page-content", style=CONTENT_STYLE)

    app.layout = html.Div([
        dcc.Location(id="url"), 
        dcc.Store(id='slider_output'), 
        sidebar, 
        content])


    # this callback uses the current pathname to set the active state of the
    # corresponding nav link to true, allowing users to tell see page they are on

    #### CALLBACKS ####
    ## CALLBACK FOR CHANGING TABS ##
    @app.callback(
        [Output(f"page-{i}-link", "active") for i in range(1, 5)],
        [Input("url", "pathname")],
    )
    def toggle_active_links(pathname):
        if pathname == "/":
            # Treat page 1 as the homepage / index
            return True, False, False
        return [pathname == f"/page-{i}" for i in range(1, 5)]

    ### CALLBACK FOR TAB - ACTUAL LAYOUT IN TABS GOES HERE ###
    @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
    def render_page_content(pathname):
        if pathname in ["/", "/page-1"]: #solar graphs
            return html.Div([
                html.P('Historical Energy Load Anaylsis Tool'), #quick graph
                dcc.Dropdown(id = 'Drop_Down_menu', #make selection menu
                    options=[{'label':name, 'value':name} for name in names],
                    value = names[0],#initial default selection upon loading 
                    multi=False #do not allow multiple selections 
                    ), 
                dcc.Graph(id='daily_graph'), #display daily graph
                dcc.Graph(id='weekly_graph'), #display weekly graph

            ])

        elif pathname == "/page-2": #load shifting 
            if Solar_Exists: 
                return html.Div([
                    dcc.Store(id='memory_output'), #storing the selected site here
                    html.P('Select a site to investigate'), 
                    dcc.Dropdown(  #make drop down selection menu - STORING THIS BAD BOY IN THE DCC.STORE ABOVE
                        id = 'Shifted_Drop_Down_menu', #unique identifier for DASH Callbacks
                        options=[{'label':name, 'value':name} for name in names], #dynamically populating the list 
                        value = names[0],#initial default selection upon loading 
                        multi=False #do not allow multiple selections 
                        ), 
                    
                    html.P(''), #blank row 
                    html.P('Select a % to load shift by'), 
                    dcc.Slider( #load shifting slider thingo 
                        id='shifting_slider', #unique identifier for DASH Callbacks
                        min=0,
                        max=50,
                        step=1,
                        value=0,
                    ),
                    html.Div(id='slider-output-container'), #display slider output
                    dcc.Graph(id='shifting_slider_display'), #display the dynamically shifted graph upon update of slider 
                    ])
            else: 
                return html.P("No Solar Data Uploaded")

        elif pathname == "/page-3": #Solar Total Graphing
            if Solar_Exists: ## ie, user uploaded a solar file, so plot the nice and pretty graphs
                return html.Div([
                    html.P("Solar Data Uploaded"),
                    dcc.Graph(id='Daily Excess Summmed Solar', figure = solar_figure), #display sum of all solar graph

                ]) 
            else: 
                return html.P("No Solar Data Uploaded")


        elif pathname == "/page-99": #readme
            return html.Div([ #README goes here - manually copied from github `README.MD`
                dcc.Markdown('''
                    # RMIT CAPSTONE PROJECT 
                    ## NORTH EAST WATER

                    ## Context
                    A program to assist in analysing NEW's industrial energy consumption. Takes two  `xls` files of interval data and solar forecast data, and returns a number of different average load profiles. 

                    ## Scope

                    Contains a GUI program that will:

                    - Code to manipulate data into DataFrames.
                    - Code to create some time series average
                    - Code to plot the data nicely.

                    This program includes NE Water data from External Sites and within WWTP. 


                    ## VERSION 

                    Version 1.0 

                    Last Updated: 17AUG20


                    ## OVERVIEW
                    1. This program will generate a GUI to load interval data, and displays the results via `DASH` in the default webbrowser. 

                    1.  Using `DASH`, the daily and weekly average load profiles for WWTP and external NE Water loads are plotted. The user can select a specific site for anaylsis. 


                    ## How to use

                    1. Clone the `master` branch. 
                    1.   `git clone https://github.com/DOCraven/GRAPHY_SIMPLE`.
                    1. Install Dependencies (if required - `PIP INSTALL [library]`).
                    1. In Visual Studio Code, open the folder that `Graphy.py` is located in via `CTRL + K + O`.
                    1. Ensure the `xls` file is in the root folder (ie, same as `Graphy.py`).
                    1. Run `Graphy.py`. 
                    -  either within your IDE (in VS CODE, green triangle in Upper RH corner).
                    -  or via the terminal using  `python graphy.py`.
                    1. Use the included GUI landing page to select the various options.


                    ## Contributing 
                    1.  Clone the master branch via `git clone https://github.com/DOCraven/Graphy.git`.
                    1.  Create a new branch either via `git branch [branch-name]` or via the inbuilt GitLens extension (bottom LH corner).
                    1.  Contribute code.
                    1.  commit code as necessary via `git commit -m "Message"` or via GitLens Extension.
                    1.  Push code to new branch via `git push origin [your branch]` or via GitLens Extension (bottom LH Corner).
                    1.  Request code review (if necessary).
                    1.  Merge with master when approved.

                    ## Known Issues


                    - This repo does not place nice with Anaconda. Please use this with a vanilla Python 3.8.x installation.
                    - There is minimal error checking involved. 
                    - `WWTP` data is lacking, and thus plotting it will not yield as many results and `EXTERNAL` data. 
                    - No solar data appended to `WWTP` plotting. 
                    - Solar data is currently placeholder data, and not site specific data. 


                    ## Dependencies

                    A `requirements.txt` fill will accompany this repo. 

                    `pip install requirements.txt` will install all dependencies required for this program


                ''') 
            ])
        # If the user tries to reach a different page, return a 404 message
        return dbc.Jumbotron(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognised..."),
            ]
        )

    ### CALLBACK FOR DAILY GRAPH ###
    @app.callback( 
        Output('daily_graph', 'figure'), 
        [Input('Drop_Down_menu', 'value')])
    def update_daily_graph(selected_name):
        #filter the names 
        chosen_site = character_removal(selected_name) #this sanitises the chosen input into a standard string
        ### DYNAMICALLY CREATE DATAFRAME TO SHOW ALL MONTHS ###
        dataframe_to_plot = dataframe_chooser(Daily_Interval_Data, chosen_site) #dynamically create dataframes to plot 12x months on top of each other for the selected site
        try: #create the figure to send to dash to plot
            fig = dataframe_to_plot.iplot(kind = 'line', xTitle='Time', yTitle='Consumption (kWh)', title = chosen_site, asFigure = True) 
        except KeyError: #https://github.com/santosjorge/cufflinks/issues/180 - although waiting 0.5s before calling the 2nd graph seems to aboid this
            Mbox('PLOT ERROR', 'Dash has encountered an error. Please select another site, and try again', 1)

        return fig

    ### CALLBACK FOR WEEKLY GRAPH ###
    @app.callback(
        Output('weekly_graph', 'figure'),
        [Input('Drop_Down_menu', 'value')])
    def update_weekly_graph(selected_name):
        #filter the names 
        chosen_site = character_removal(selected_name) #this sanitises the chosen input into a standard string
        ### DYNAMICALLY CREATE DATAFRAME TO SHOW ALL MONTHS ###
        time.sleep(0.25) #mitigate an error where calling the plot function twice in a short amount of time means it does not plot the 2nd graph
        dataframe_to_plot = dataframe_chooser(Weekly_Interval_Data, chosen_site) #dynamically create dataframes to plot entire year of chosen 
        try: #create the figure to send to dash to plot
            fig = dataframe_to_plot.iplot(kind = 'line', xTitle='Day and Time', yTitle='Consumption (kWh)', title = chosen_site, asFigure = True) 
        except KeyError: #https://github.com/santosjorge/cufflinks/issues/180 - although waiting 0.25s before calling this graph seems to avoid this
            Mbox('PLOT ERROR', 'Dash has encountered an error. Please select another site, and try again', 1)
        
        return fig
    
    ### CALLBACK FOR SLIDER ###
    ############# GRAPH UPDATES ON THIS SLIDER ACTION ##################
    @app.callback(
        [
            dash.dependencies.Output('shifting_slider_display', 'figure'), #output graph
            dash.dependencies.Output('slider-output-container', 'children') #output selected value
            ], 
        [
            dash.dependencies.Input('shifting_slider', 'value'), #read the slider input 
            dash.dependencies.Input('memory_output', 'data')
            ]) #AND READ THE STORED VALUE AT 'memory_output' in layout[]
    def update_output(value, data): #slider is value, dropdown menue is data
        ## VARS
        chosen_site = data #to narrow down the dataframe using previously existing data
        load_shift_number = value #%value to load shift selected site by - IT IS AN INT - need to convert it to % though

        ### STEP 1 - narrow down dataframe to chosen site 
        site_to_plot_raw = dataframe_chooser(Daily_Interval_Data, chosen_site) #dynamically create dataframes to plot 12x months on top of each other for the selected site
        #the above returns a 12x? dataframe. need to convert it to a list of dataframes 
        
        ### STEP 2 - Convert the dataframe for a list of dataframes 
        site_to_plot_list = dataframe_list_generator(non_list_dataframe = site_to_plot_raw) #converts the above into a list of 1x month per list entry 

        ### STEP 3 - extract solar from the original dataframe, and add it to each list 
        site_to_plot_solar_added = solar_extractor_adder(single_site = site_to_plot_list, all_sites = Daily_Interval_Data) #adds the respective monthly solar to the respective month (in the list)
        
        ### STEP 4 - do the load shift calculations, and return a single dataframe of each month 
        shifted_site = load_shifter(site_to_plot_solar_added, load_shift_number) #returns a list of shifted sites - IE, I PLOT THIS 
        

        ### STEP 5 - create a figure via cufflinks to ploit 
        plot_title = chosen_site + ': LOAD SHIFTED ' + str(load_shift_number) + '%'
        figure = shifted_site.iplot(kind = 'line', xTitle='Time', yTitle='Consumption (kWh)', title = plot_title, asFigure = True) #
        
        message = 'You have load shifted {}'.format(value) + '%'

        return figure, message

     ### CALLBACK FOR SHIFTED DAILY GRAPH DROPDOWN SELECTOR ###
    @app.callback(Output('memory_output', 'data'),
              [Input('Shifted_Drop_Down_menu', 'value')]) #storing this
    def filter_sites(value):
        return value #just return the value and store it in the location called "memory_output"
            


    webbrowser.open('http://127.0.0.1:8888/')  # open the DASH app in default webbrowser
    print('Starting Dash Server') #print to console, to for debugging/dev

    app.run_server(port=8888) #start the server. 

    return #nothing 
