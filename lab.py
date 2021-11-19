#!/usr/bin/env python3

from util import read_osm_data,read_osm_data_s3, great_circle_distance, to_local_kml_url

import time


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

node_data_top_left = {}
a_top_left = {}
a_bottom_left = {}
a_top_right = {}
a_bottom_right = {}



node_data_bottom_left = {}
b_top_left = {}
b_bottom_left = {}
b_top_right = {}
b_bottom_right = {}


node_data_top_right = {}
c_top_left = {}
c_bottom_left = {}
c_top_right = {}
c_bottom_right = {}

node_data_bottom_right = {}
d_top_left = {}
d_bottom_left = {}
d_top_right = {}
d_bottom_right = {}

min_lat = 42.18
max_lat = 42.59
min_lon = -71.2999999
max_lon = -70.8199997

mid_lat = (max_lat + min_lat)/2
mid_lon = (max_lon + min_lon)/2

##Top left
a_min_lat = min_lat
a_max_lat = mid_lat
a_min_lon = mid_lon
a_max_lon = max_lon
a_mid_lat = (a_min_lat + a_max_lat)/2
a_mid_lon = (a_min_lon + a_max_lon)/2

##Top right
b_min_lat = mid_lat
b_max_lat = max_lat
b_min_lon = mid_lon
b_max_lon = max_lon
b_mid_lat = (b_min_lat + b_max_lat)/2
b_mid_lon = (b_min_lon + b_max_lon)/2

##bottom left
c_min_lat = min_lat
c_max_lat = mid_lat
c_min_lon = min_lon
c_max_lon = mid_lon
c_mid_lat = (c_min_lat + c_max_lat)/2
c_mid_lon = (c_min_lon + c_max_lon)/2

## right
d_min_lat = mid_lat
d_max_lat = max_lat
d_min_lon = min_lon
d_max_lon = mid_lon
d_mid_lat = (d_min_lat + d_max_lat)/2
d_mid_lon = (d_min_lon + d_max_lon)/2

def get_loc_graph(loc):
    lat, lon = loc
    if a_min_lat <= lat <= a_mid_lat and a_mid_lon <= lon <= a_max_lon:
        return a_top_left, 1

    if a_min_lat <= lat <= a_mid_lat and a_min_lon <= lon <= a_mid_lon:
        return a_bottom_left, 4

    if a_mid_lat <= lat <= a_max_lat and a_min_lon <= lon <= a_mid_lon:
        return a_bottom_right, 3

    if a_mid_lat <= lat <= a_max_lat and a_mid_lon <= lon <= a_max_lon:
        return a_top_right, 2

    ##FOR B
    if b_min_lat <= lat <= b_mid_lat and b_mid_lon <= lon <= b_max_lon:
        return b_top_left, 1

    if b_min_lat <= lat <= b_mid_lat and b_min_lon <= lon <= b_mid_lon:
        return b_bottom_left, 4

    if b_mid_lat <= lat <= b_max_lat and b_min_lon <= lon <= b_mid_lon:
        return b_bottom_right, 3

    if b_mid_lat <= lat <= b_max_lat and b_mid_lon <= lon <= b_max_lon:
        return b_top_right, 2

    ##FOR C
    if c_min_lat <= lat <= c_mid_lat and c_mid_lon <= lon <= c_max_lon:
        return c_top_left, 1

    if c_min_lat <= lat <= c_mid_lat and c_min_lon <= lon <= c_mid_lon:
        return c_bottom_left, 4

    if c_mid_lat <= lat <= c_max_lat and c_min_lon <= lon <= c_mid_lon:
        return c_bottom_right, 3

    if c_mid_lat <= lat <= c_max_lat and c_mid_lon <= lon <= c_max_lon:
        return c_top_right, 2

    ##FOR D
    if d_min_lat <= lat <= d_mid_lat and d_mid_lon <= lon <= d_max_lon:
        return d_top_left, 1

    if d_min_lat <= lat <= d_mid_lat and d_min_lon <= lon <= d_mid_lon:
        return d_bottom_left, 4

    if d_mid_lat <= lat <= d_max_lat and d_min_lon <= lon <= d_mid_lon:
        return d_bottom_right, 3

    if d_mid_lat <= lat <= d_max_lat and d_mid_lon <= lon <= d_max_lon:
        return d_top_right, 2



# def get_loc_graph(loc):
#     lat, lon = loc
#     if min_lat <= lat <= mid_lat and mid_lon <= lon <= max_lon:
#         return node_data_top_left, 0

#     if min_lat <= lat <= mid_lat and min_lon <= lon <= mid_lon:
#         return node_data_bottom_left, 1

#     if mid_lat <= lat <= max_lat and min_lon <= lon <= mid_lon:
#         return node_data_bottom_right, 3

#     if mid_lat <= lat <= max_lat and mid_lon <= lon <= max_lon:
#         return node_data_top_right, 2


def build_auxiliary_structures(nodes_filename, ways_filename):
    """
    Create any auxiliary structures you are interested in, by reading the data
    from the given filenames (using read_osm_data)

    Returns:
        nodes_graph: dict => {node_id: set =>{nodes connected to it}}
        speeds: dict => {(node_1, node_2): speed between them}
        node_data: dict => {node_id: dict => {"lat": latitude, "lon": longitude}}
    """

    # get all the allowed ways and the nodes along those ways
    nodes_graph = {}
    speeds = {}
    node_data = {}
    
    for way in read_osm_data(ways_filename):
        if way["tags"].get("highway", None) in ALLOWED_HIGHWAY_TYPES:
            for node_1, node_2 in zip(way["nodes"], way["nodes"][1:]):
                speed = 1
                update_auxiliary_structures(nodes_graph, speeds, node_1, node_2, speed)
                if way["tags"].get("oneway", "no") == "no":
                    update_auxiliary_structures(nodes_graph, speeds, node_2, node_1, speed)

    for node in read_osm_data(nodes_filename):
        if node["id"] in nodes_graph:
            node_data[node["id"]] = (node["lat"], node["lon"])

            id, loc = node["id"], (node["lat"], node["lon"])
            graph, _ = get_loc_graph(loc)
            graph[id] = loc

    return nodes_graph, node_data, speeds

def build_auxiliary_structures_s3(nodes_data, ways_data):
    """
    Create any auxiliary structures you are interested in, by reading the data
    from the given filenames (using read_osm_data)

    Returns:
        nodes_graph: dict => {node_id: set =>{nodes connected to it}}
        speeds: dict => {(node_1, node_2): speed between them}
        node_data: dict => {node_id: dict => {"lat": latitude, "lon": longitude}}
    """

    # get all the allowed ways and the nodes along those ways
    nodes_graph = {}
    speeds = {}
    node_data = {}
    
    for way in read_osm_data_s3(ways_data[0],ways_data[1]):
    # for way in read_osm_data(ways_filename):
        if way["tags"].get("highway", None) in ALLOWED_HIGHWAY_TYPES:
            for node_1, node_2 in zip(way["nodes"], way["nodes"][1:]):
                speed = 1
                update_auxiliary_structures(nodes_graph, speeds, node_1, node_2, speed)
                if way["tags"].get("oneway", "no") == "no":
                    update_auxiliary_structures(nodes_graph, speeds, node_2, node_1, speed)

    for node in read_osm_data_s3(nodes_data[0],nodes_data[1]):
        if node["id"] in nodes_graph:
            node_data[node["id"]] = (node["lat"], node["lon"])

            id, loc = node["id"], (node["lat"], node["lon"])
            graph, _ = get_loc_graph(loc)
            graph[id] = loc

    return nodes_graph, node_data, speeds

def update_auxiliary_structures(nodes_graph, speeds, node_1, node_2, speed):
    """
    Update the auxiliary structures with data about a pair of nodes
    """
    nodes_graph.setdefault(node_1, set()).add(node_2)
    nodes_graph.setdefault(node_2, set())
    curr_speed = speeds.setdefault((node_1, node_2), -float("inf"))
    speeds[(node_1, node_2)] = max(speed, curr_speed)


def trace_path(parents, start, end):
    """
    Trace the path from start to end using the parent pointers in parents
    """
    path = [end]
    while path[-1] != start:
        parent = parents[path[-1]]
        path.append(parent)

    return path[::-1]


def heuristic_distance(node_data, speeds, g_n, node2, next_node, child):
    curr_g_n = g_n.setdefault(child, float("inf"))
    curr_h_n = great_circle_distance(node_data[node2], node_data[child])
    dist = great_circle_distance(node_data[next_node], node_data[child])
    return curr_g_n, curr_h_n, dist


def heuristic_speed(node_data, speeds, g_n, node2, next_node, child):
    curr_g_n = g_n.setdefault(child, float("inf"))
    curr_h_n = great_circle_distance(node_data[node2], node_data[child]) / 60
    dist = great_circle_distance(node_data[next_node], node_data[child]) / speeds[(next_node, child)]
    return curr_g_n, curr_h_n, dist


def find_short_path_nodes_without_heuristic(aux_structures, node1, node2):
    """
    Return the shortest path between the two nodes

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    """
    nodes_graph, node_data, speeds = aux_structures
    parents: dict[int, int] = {}
    agenda: dict[int, float] = {node1: 0}
    seen: set[int] = {node1}

    while agenda and node2 not in seen:
        next_node = None
        next_node_dist = float("inf")
        for node, dist in agenda.items():
            if dist < next_node_dist:
                next_node = node
                next_node_dist = dist

        for child in nodes_graph[next_node]:
            if child not in seen:
                current_cost = agenda.setdefault(child, float("inf"))
                new_cost = next_node_dist + great_circle_distance(node_data[next_node], node_data[child])
                if new_cost < current_cost:
                    agenda[child] = new_cost
                    parents[child] = next_node

        del agenda[next_node]
        seen.add(next_node)

    return None if node2 not in seen else trace_path(parents, node1, node2)


def a_star(aux_structures, node1, node2, heuristic_function):
    nodes_graph, node_data, speeds = aux_structures
    parents: dict[int, int] = {}
    g_n = {node1: 0}
    f_n = {node1: 0}
    seen: set[int] = {node1}

    while f_n and node2 not in seen:
        next_node = None
        next_node_dist = float("inf")
        for node, dist in f_n.items():
            if dist < next_node_dist:
                next_node = node
                next_node_dist = dist

        for child in nodes_graph[next_node]:
            if child not in seen:
                curr_g_n, curr_h_n, dist = heuristic_function(node_data, speeds, g_n, node2, next_node, child)
                if dist + g_n[next_node] < curr_g_n:
                    parents[child] = next_node
                    g_n[child] = dist + g_n[next_node]
                    f_n[child] = g_n[child] + curr_h_n

        del f_n[next_node]
        del g_n[next_node]
        seen.add(next_node)

    return None if node2 not in seen else trace_path(parents, node1, node2)


def find_short_path_nodes(aux_structures, node1, node2):
    return a_star(aux_structures, node1, node2, heuristic_distance)


def get_closest_node(nodes_data, node):
    """
    Return the node id of the node closest to node
    """
    start = time.time()
    current_distance = float("inf")
    current_node = None

    graph, _ = get_loc_graph(node)
    for test_node, location in graph.items():
        test_dist = great_circle_distance(node, location)
        if test_dist < current_distance:
            current_node = test_node
            current_distance = test_dist
    end = time.time()

    print("find closest node took ", end-start)

    return current_node


def find_short_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """
    nodes_graph, node_data, speeds = aux_structures
    node1 = get_closest_node(node_data, loc1)
    node2 = get_closest_node(node_data, loc2)
    path_nodes = find_short_path_nodes(aux_structures, node1, node2)

    if path_nodes is None:
        return None

    return [node_data[node] for node in path_nodes]


def find_fast_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """
    nodes_graph, node_data, speeds = aux_structures
    node1 = get_closest_node(node_data, loc1)
    node2 = get_closest_node(node_data, loc2)
    path_nodes = a_star(aux_structures, node1, node2, heuristic_speed)

    if path_nodes is None:
        return None

    return [node_data[node] for node in path_nodes]


if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.

    for way in read_osm_data("resources/cambridge.ways"):
        print(way)
    # 
    # nodes_graph, node_data, speeds = build_auxiliary_structures("resources/mit.nodes", "resources/mit.ways")
    # 
    # for node, connected in nodes_graph.items():
    #     print(node, ":", connected)
    # 
    # print()
    # for node, data in node_data.items():
    #     print(node, ":", data)
    # 
    # print()
    # for pair, speed in speeds.items():
    #     print(pair, ":", speed)

    # # print(great_circle_distance((42.363745, -71.100999),(42.361283, -71.239677)))
    # data = read_osm_data("resources/midwest.nodes")
    # ways = read_osm_data("resources/midwest.ways")
    # for way in ways:
    #     if way["id"] == 21705939:
    #         print(way)
    #         nodes = [(node["lat"], node["lon"]) for node in data if node["id"] in way["nodes"]]
    #         distance = sum(great_circle_distance(node1, node2) for node1, node2 in zip(nodes, nodes[1:]))
    #         print(distance)
    #         break

    # loc1 = 2  # New House
    # loc2 = 8  # 34-501
    # aux = build_auxiliary_structures("resources/mit.nodes", "resources/mit.ways")
    # print(find_short_path_nodes(aux, loc1, loc2))
    pass
