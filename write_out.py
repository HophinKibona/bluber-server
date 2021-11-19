from node_data import node_data_saved
from nodes_graph import nodes_graph_s
from node_data_all import node_data_all_saved
import json

# print(type(nodes_graph_s))
with open('nodes_data_saved.json', 'w') as f:
    f.write(json.dumps(node_data_saved))
    # json.dumps(node_data)

# print("finished")