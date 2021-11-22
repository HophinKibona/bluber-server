#!/usr/bin/env python3

from util import great_circle_distance
from node_data import node_data_saved
from nodes_graph import nodes_graph_saved
from node_data_all import node_data_all_saved

ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
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


# Top left
a_min_lat = min_lat
a_max_lat = mid_lat
a_min_lon = mid_lon
a_max_lon = max_lon
a_mid_lat = (a_min_lat + a_max_lat)/2
a_mid_lon = (a_min_lon + a_max_lon)/2

# Top right
b_min_lat = mid_lat
b_max_lat = max_lat
b_min_lon = mid_lon
b_max_lon = max_lon
b_mid_lat = (b_min_lat + b_max_lat)/2
b_mid_lon = (b_min_lon + b_max_lon)/2

# bottom left
c_min_lat = min_lat
c_max_lat = mid_lat
c_min_lon = min_lon
c_max_lon = mid_lon
c_mid_lat = (c_min_lat + c_max_lat)/2
c_mid_lon = (c_min_lon + c_max_lon)/2

# bottom right
d_min_lat = mid_lat
d_max_lat = max_lat
d_min_lon = min_lon
d_max_lon = mid_lon
d_mid_lat = (d_min_lat + d_max_lat)/2
d_mid_lon = (d_min_lon + d_max_lon)/2


def get_loc_graph(loc):
    lat, lon = loc
    if a_min_lat <= lat <= a_mid_lat and a_mid_lon <= lon <= a_max_lon:
        return a_top_left, 0

    if a_min_lat <= lat <= a_mid_lat and a_min_lon <= lon <= a_mid_lon:
        return a_bottom_left, 1

    if a_mid_lat <= lat <= a_max_lat and a_min_lon <= lon <= a_mid_lon:
        return a_bottom_right, 2

    if a_mid_lat <= lat <= a_max_lat and a_mid_lon <= lon <= a_max_lon:
        return a_top_right, 3

    # FOR B
    if b_min_lat <= lat <= b_mid_lat and b_mid_lon <= lon <= b_max_lon:
        return b_top_left, 4

    if b_min_lat <= lat <= b_mid_lat and b_min_lon <= lon <= b_mid_lon:
        return b_bottom_left, 5

    if b_mid_lat <= lat <= b_max_lat and b_min_lon <= lon <= b_mid_lon:
        return b_bottom_right, 6

    if b_mid_lat <= lat <= b_max_lat and b_mid_lon <= lon <= b_max_lon:
        return b_top_right, 7

    # FOR C
    if c_min_lat <= lat <= c_mid_lat and c_mid_lon <= lon <= c_max_lon:
        return c_top_left, 8

    if c_min_lat <= lat <= c_mid_lat and c_min_lon <= lon <= c_mid_lon:
        return c_bottom_left, 9

    if c_mid_lat <= lat <= c_max_lat and c_min_lon <= lon <= c_mid_lon:
        return c_bottom_right, 10

    if c_mid_lat <= lat <= c_max_lat and c_mid_lon <= lon <= c_max_lon:
        return c_top_right, 11

    # FOR D
    if d_min_lat <= lat <= d_mid_lat and d_mid_lon <= lon <= d_max_lon:
        return d_top_left, 12

    if d_min_lat <= lat <= d_mid_lat and d_min_lon <= lon <= d_mid_lon:
        return d_bottom_left, 13

    if d_mid_lat <= lat <= d_max_lat and d_min_lon <= lon <= d_mid_lon:
        return d_bottom_right, 14

    if d_mid_lat <= lat <= d_max_lat and d_mid_lon <= lon <= d_max_lon:
        return d_top_right, 15


def trace_path(parents, start, end):
    """
    Trace the path from start to end using the parent pointers in parents
    """
    path = [end]
    while path[-1] != start:
        parent = parents[path[-1]]
        path.append(parent)

    return path[::-1]


def heuristic_distance(node_data, g_n, node2, next_node, child):
    curr_g_n = g_n.setdefault(child, float("inf"))
    curr_h_n = great_circle_distance(node_data[node2], node_data[child])
    dist = great_circle_distance(node_data[next_node], node_data[child])
    return curr_g_n, curr_h_n, dist


def a_star(node1, node2, heuristic_function):
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

        for child in nodes_graph_saved[next_node]:
            if child not in seen:
                curr_g_n, curr_h_n, dist = heuristic_function(
                    node_data_all_saved, g_n, node2, next_node, child)
                if dist + g_n[next_node] < curr_g_n:
                    parents[child] = next_node
                    g_n[child] = dist + g_n[next_node]
                    f_n[child] = g_n[child] + curr_h_n

        del f_n[next_node]
        del g_n[next_node]
        seen.add(next_node)

    return None if node2 not in seen else trace_path(parents, node1, node2)


def find_short_path_nodes(node1, node2):
    return a_star(node1, node2, heuristic_distance)


def get_closest_node(node):
    """
    Return the node id of the node closest to node
    """
    current_distance = float("inf")
    current_node = None

    graph, index = get_loc_graph(node)
    for test_node, location in node_data_saved[index].items():
        test_dist = great_circle_distance(node, location)
        if test_dist < current_distance:
            current_node = test_node
            current_distance = test_dist

    return current_node


def find_short_path(loc1, loc2):
    """
    Return the shortest path between the two locations

    Parameters:
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """
    node1 = get_closest_node(loc1)
    node2 = get_closest_node(loc2)
    path_nodes = find_short_path_nodes(node1, node2)

    if path_nodes is None:
        return None

    return [node_data_all_saved[node] for node in path_nodes]


if __name__ == '__main__':
    pass
