
# RMIT CAPSTONE PROJECT 
## NORTH EAST WATER

## JOSE TEST

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

