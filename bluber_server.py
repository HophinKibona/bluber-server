from flask import Flask
from lab import *
import json

aux = build_auxiliary_structures("./resources/cambridge.nodes", "./resources/cambridge.ways")

app = Flask(__name__)

@app.route('/')
def index():
    return json.dumps([])

@app.route('/road/<float:lat1>/<float(signed=True):lon1>/<float:lat2>/<float(signed=True):lon2>')
def get_road(lat1, lon1,lat2, lon2):
    nodes = find_short_path(aux, (lat1, lon1), (lat2, lon2)) 
    return json.dumps(nodes)


# http://127.0.0.1:5000/road/42.2/-71.1/42.19/-70.9/