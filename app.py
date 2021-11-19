from flask import Flask
from lab import *
import json
import boto3
import os
import pickle
import time

##can use a client
client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get("ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("SECRET_ACCESS_KEY"),
)
##can use a session
session = boto3.Session(
    aws_access_key_id=os.environ.get("ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("SECRET_ACCESS_KEY"),
)

response = client.list_buckets()

# cambridge_nodes = client.get_object(Bucket="cambridgedata",Key="cambridge.nodes")
# cambridge_ways =  client.get_object(Bucket="cambridgedata",Key="cambridge.ways")

cambridge_nodes = ["cambridgedata","cambridge.nodes"]
cambridge_ways =  ["cambridgedata","cambridge.ways"]

print('building auxiliary structures...')
t = time.time()
aux = build_auxiliary_structures_s3(cambridge_nodes, cambridge_ways)
print('auxiliary structures built in %.02f seconds.' % (time.time() - t,))

# s3 = session.resource('s3')
# print(cambridge_nodes)
# print(cambridge_ways)

# # s3 = boto3.resource('s3')
# my_pickle = pickle.loads(s3.Bucket("cambridgedata").Object("cambridge.ways").get()['Body'].read())
# my_pickle2 = pickle.loads(s3.Bucket("cambridgedata").Object("cambridge.nodes").get()['Body'].read())




# print(cambridge_nodes["Body"].read())

# aux = build_auxiliary_structures("./resources/cambridge.nodes", "./resources/cambridge.ways")
# aux = build_auxiliary_structures_s3(cambridge_nodes, cambridge_ways)

app = Flask(__name__)

@app.route('/')
def index():
    return json.dumps([])

@app.route('/road/<float:lat1>/<float(signed=True):lon1>/<float:lat2>/<float(signed=True):lon2>')
def get_road(lat1, lon1,lat2, lon2):
    nodes = find_short_path(aux, (lat1, lon1), (lat2, lon2)) 
    return json.dumps(nodes)


# http://127.0.0.1:5000/road/42.2/-71.1/42.19/-70.9

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
    