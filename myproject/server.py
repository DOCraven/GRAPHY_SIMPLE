from flask import Flask
from dash import Dash
#IMPORT USER DEFINED GLOBAL VARIABLES 
import config
#some magic for Heroku below
server = Flask('myproject') 
app = Dash(server=server)