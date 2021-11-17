#!/usr/bin/env python3

from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}

DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}


def build_auxiliary_structures(nodes_filename, ways_filename):
    """
    Create any auxiliary structures you are interested in, by reading the data
    from the given filenames (using read_osm_data)

    Returns:
        ways_graph => {node : list of ways that contains the node}
        node_data: dict => {node_id: dict => {"lat": latitude, "lon": longitude}}
    """

    # get all the allowed ways and the nodes along those ways
    ways_graph = {}
    node_data = {}

    for way in read_osm_data(ways_filename):
        nodes = way["nodes"]
        for node in nodes:
            if node in ways_graph:
                ways_graph[node].append(way)
            else:
                ways_graph[node] = [way]

    for node in read_osm_data(nodes_filename):
        # if node["id"] in nodes_graph:
        node_data[node["id"]] = (node["lat"], node["lon"])

    return ways_graph, node_data

def get_nearest_roads(ways_graph, node_data, loc1, loc2):
    node1 = get_closest_node(node_data, loc1)
    node2 = get_closest_node(node_data, loc2)


    print("node 1 ", node1)
    print("node 2 ", node2)


    ways1 = ways_graph[node1]
    ways2 = ways_graph[node2]

    print("way 1 ", [way["id"]for way in ways1])
    print("way 2 ", [way["id"]for way in ways2])

    # node_ways = []
    # for way1 in ways1:
    #     id1 = way1["id"]
    #     for way2 in ways2:
    #         if id1 == way2["id"]:
    #             node_ways.append(way1)
    node_ways = ways1 + ways2
    roads = []
    for way in node_ways:
        road = [node_data[node] for node in way["nodes"]]
        roads.append(road)
    return roads



def get_closest_node(nodes_data, node):
    """
    Return the node id of the node closest to node
    """
    current_distance = float("inf")
    current_node = None

    for test_node, location in nodes_data.items():
        test_dist = great_circle_distance(node, location)
        if test_dist < current_distance:
            current_node = test_node
            current_distance = test_dist
    return current_node

if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    counter = 0
    for way in read_osm_data("resources/mit.ways"):
        counter += 1
        print(way)
        if counter == 10: break
    pass
