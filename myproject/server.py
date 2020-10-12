from flask import Flask
from dash import Dash
#IMPORT USER DEFINED GLOBAL VARIABLES 
import config

#########################################
## CODE IS UP TO DATE AS OF 12/10/2020 ##
#########################################


#some magic for Heroku below
server = Flask('myproject') 
app = Dash(server=server)