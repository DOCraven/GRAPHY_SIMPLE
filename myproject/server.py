from flask import Flask
from dash import Dash
import flask
#IMPORT USER DEFINED GLOBAL VARIABLES 
import config

server = Flask('myproject')
app = Dash(server=server)