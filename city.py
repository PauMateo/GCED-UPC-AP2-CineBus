from typing import TypeAlias
from dataclasses import dataclass
import osmnx as ox
import pickle
import networkx as nx
from buses import *
from haversine import haversine
from staticmap import CircleMarker, StaticMap, IconMarker


Coord: TypeAlias = tuple[float, float]   # (latitude, longitude)
CityGraph: TypeAlias = nx.Graph
OsmnxGraph: TypeAlias = nx.MultiDiGraph


@dataclass
class Path:
    source: int
    dest: int
    path: list[int]  # path nodes' list
    path_graph: nx.Graph
    plot_graph: nx.Graph
    path_indications: str
    city_graph: CityGraph
    osmnx_graph: OsmnxGraph
    time: int  # in minutes

    def __init__(self, source: int, dest: int,
                 path: list[int], time: int,
                 city: CityGraph, omsnx: OsmnxGraph) -> None:
        """Constructor"""

        self.source = source
        self.dest = dest
        self.path = path
        self.time = time
        self.city_graph = city
        self.osmnx_graph = omsnx

    def get_other_data(self) -> None:
        self.path_graph = build_path_graph(self.source, self.dest,
                                           self.path, self.city_graph)
        try:
            indic: str = path_indications(self)
        except Exception:
            indic = ''  # if we cannot calculate the indicactions

        self.path_indications = indic
        self.plot_graph = build_plot_graph(self.source,
                                           self.dest,
                                           self.path,
                                           self.city_graph,
                                           self.osmnx_graph)


def get_osmnx_graph() -> OsmnxGraph:
    """Function which gets and returns the graf of Barcelona streets."""

    graph: OsmnxGraph = ox.graph_from_place("Barcelona",
                                            network_type='walk',
                                            simplify=False)  # type: ignore

    for u, v, key, geom in graph.edges(data="geometry", keys=True):
        if geom is not None:
            del (graph[u][v][key]["geometry"])

    for node in graph.nodes():
        graph.nodes[node]['pos'] = (
            graph.nodes[node]['x'],
            graph.nodes[node]['y'])
    return graph


def find_path(ox_g: OsmnxGraph, g: CityGraph,
              src: Coord, dst: Coord) -> Path:
    """Returns the shortest path (Path) between the nodes src and dst."""
    src_node, dist_src = ox.nearest_nodes(
        ox_g, src[1], src[0], return_dist=True)
    dst_node, dist_dst = ox.nearest_nodes(
        ox_g, dst[1], dst[0], return_dist=True)

    assert dist_src < 10000 and dist_dst < 10000
    shortest_path = nx.shortest_path(
        g, src_node, dst_node, weight='time', method='dijkstra')

    time = 0
    node_ant = shortest_path[0]
    for node in shortest_path[1:]:
        time += g[node_ant][node]['time']
        node_ant = node

    path: Path = Path(src_node, dst_node, shortest_path[1:-1],
                      int(time) // 60, g, ox_g)

    return path


def build_plot_graph(
                    src: int,
                    dest: int,
                    path: list[int],
                    g: CityGraph,
                    ox_g: OsmnxGraph) -> nx.Graph:
    """
    Builds a complementary graph of the path,
    just for ploting it in a nicely way.
    This function makes the bus lines (edges) not go throw buildings
    and adds colors to specific nodes (source, dest and changing line).
    """

    plot_graph: nx.Graph = nx.Graph()

    plot_graph.add_node(src, **g.nodes[src], size=30)
    plot_graph.add_node(dest, **g.nodes[dest], size=30)

    plot_graph.nodes[src]['tipus'] = 'src'
    plot_graph.nodes[dest]['tipus'] = 'dest'
    plot_graph.nodes[dest]['color'] = 'green'
    plot_graph.nodes[src]['color'] = '#FF00FF'  # magenta color in hexadecimal

    for node in path:
        if g.nodes[node]['tipus'] == 'Cruilla':
            plot_graph.add_node(node, **g.nodes[node], size=0)
        else:
            plot_graph.add_node(node, **g.nodes[node], size=15)

    node_ant = src

    for node in path:
        if g.nodes[node_ant]['tipus'] == 'Parada' \
                and g.nodes[node]['tipus'] == 'Parada':
            # If both the previous and current node are bus stops ('Parada'),
            # adjust the edges and create a new route between them
            # without going throw buildings.
            nr_node_ant = ox.nearest_nodes(
                ox_g,
                g.nodes[node_ant]['pos'][0],
                g.nodes[node_ant]['pos'][1],
                return_dist=0)

            nr_node = ox.nearest_nodes(
                ox_g,
                g.nodes[node]['pos'][0],
                g.nodes[node]['pos'][1],
                return_dist=0)

            # Find the shortest path between the nearest nodes from two
            # consecutive bus stosp using streets graph (ox_g).
            shortest_path = nx.shortest_path(
                ox_g, nr_node_ant, nr_node, weight='length')

            # Divides the time into the different subedges
            # for still having the same time in that bus ride.
            num_sh_edges = len(shortest_path) + 1
            g[node_ant][node]['time'] /= num_sh_edges

            attr = g.get_edge_data(node_ant, node)
            plot_graph.add_edge(node_ant, nr_node_ant, **attr)
            short_ant = shortest_path[0]
            plot_graph.add_node(
                short_ant,
                pos=g.nodes[short_ant]['pos'],
                color='blue',
                tipus='gir_linia', size=0)

            for u in shortest_path[1:]:
                plot_graph.add_edge(short_ant, u, **attr)
                plot_graph.add_node(
                    u,
                    pos=g.nodes[u]['pos'],
                    color='blue',
                    tipus='gir_linia', size=0)
                short_ant = u

            plot_graph.add_edge(nr_node, node, **attr)
            node_ant = node
        else:
            # else: just add the other nodes to the plot_graph
            attr = g.get_edge_data(node_ant, node)
            plot_graph.add_edge(node_ant, node, **attr)
            node_ant = node

    attr = g[node_ant][dest]
    plot_graph.add_edge(node_ant, dest, **attr)

    return plot_graph


def build_path_graph(
                    src: int,
                    dest: int,
                    path: list[int],
                    g: CityGraph) -> nx.Graph:
    """
    Builds a graph from the path which will be
    used for calculating the path indications.
    """

    path_graph: nx.Graph = nx.Graph()
    path_graph.add_node(src, **g.nodes[src])
    path_graph.add_node(dest, **g.nodes[dest])
    for node in path:
        path_graph.add_node(node, **g.nodes[node])

    node_ant = src
    for node in path:
        attr = g.get_edge_data(node_ant, node)
        path_graph.add_edge(node_ant, node, **attr)
        node_ant = node
    attr = g[node_ant][dest]
    path_graph.add_edge(node_ant, dest, **attr)

    return path_graph


def path_indications(p: Path) -> str:
    """
    Given a path (Path), returns the indications to the destination.
    It also modiies the nodes' color where a bus line should be taken
    or change to another line as orange.
    """

    indic: str = ''
    g: nx.Graph = p.path_graph

    for n in p.path:  # we start with all black nodes
        g.nodes[n]['color'] = 'black'

    i = 1
    n: int | str = p.path[i]
    n_ant: int | str = p.path[i-1]

    # In case we don't need to take bus:
    if all(g.nodes[node]['tipus'] != 'Parada' for node in g.nodes):
        indic = "Walk to the cinema. You don't need to take a bus!"
        return indic

    while i < len(p.path):
        # currently walking
        while g.nodes[n]['tipus'] == 'Cruilla' and i < len(p.path) - 1:
            i += 1
            n_ant, n = n, p.path[i]

        if i == len(p.path) - 1:
            indic += "Walk to the Cinema."
            return indic

        # by bus
        assert g.nodes[n]['tipus'] == 'Parada' and \
                                      g.nodes[n_ant]['tipus'] == 'Cruilla'

        # line (bus stop where is taken)
        linia_parada: list[tuple[str, int]] = []
        parada: int = n  # to control where to change from bus line
        ultima_parada: int = parada

        i += 1
        n_ant, n = p.path[i-1], p.path[i]

        # trivial case: passing throgh a bus stop but without taking the bus
        if g.nodes[n]['tipus'] == 'Cruilla':
            continue

        # variables to control the line changes in a bus ride.
        linies: set[str] = set([])
        noves_linies: set[str] = set(g[n_ant][n]['linies'])
        i += 1
        n_ant, n = n, p.path[i]

        # trivial cas: take the bus for only one bus stop ride length
        # (should get off the bus at the next stop)
        if g.nodes[n]['tipus'] == 'Cruilla':
            lin = noves_linies.pop()
            indic += f"Camina fins la parada {g.nodes[n_ant]['nom']} " + \
                     f"i agafa l'autobus {lin} fins la parada " + \
                     f"{g.nodes[n]['nom']}."
            p.city_graph.nodes[n_ant]['color'] = 'orange'
            continue

        linies = noves_linies
        while g.nodes[n]['tipus'] == 'Parada' and i < len(p.path) - 1:
            noves_linies = set(g[n_ant][n]['linies'])
            if linies & noves_linies == set():
                linia = linies.pop()  # any of the line
                linia_parada.append((linia, parada))
                parada = n_ant  # update stop (line change)
                linies = noves_linies
            else:
                linies = linies & noves_linies
            ultima_parada = n
            i += 1
            n_ant, n = n, p.path[i]

        linia_parada.append((linies.pop(), parada))

        # add the indications from the bus ride
        lin, par = linia_parada[0]
        indic += f"Walk to the bus stop {g.nodes[par]['nom']}, " + \
                 f"and take bus {lin}.\n"

        p.city_graph.nodes[par]['color'] = 'orange'

        for lin, par in linia_parada[1:]:
            indic += f"Travel by bus to the stop {g.nodes[par]['nom']}," + \
                     f" and transfer to line {lin}.\n"
            p.city_graph.nodes[par]['color'] = 'orange'

        lin, par = linia_parada[-1]
        indic += f"Travel by bus to the stop " + \
                 f"{g.nodes[ultima_parada]['nom']}.\n"

    return indic


def save_osmnx_graph(g: OsmnxGraph, filename: str) -> None:
    """Saves the g graph as filname."""
    file = open(filename, 'wb')
    pickle.dump(g, file)
    file.close()


def load_osmnx_graph(filename: str) -> OsmnxGraph:
    """Returns the graph previously saved at the filname path."""

    file = open(filename, 'rb')
    g = pickle.load(file)
    file.close()
    assert isinstance(g, OsmnxGraph)
    return g


def build_city_graph(g1: OsmnxGraph, g2: BusesGraph) -> CityGraph:
    """Returns a graph combining g1 and g2."""
    city: CityGraph = nx.Graph()

    for u, nbrsdict in g1.adjacency():
        attr = g1.nodes[u]
        city.add_node(u, **attr, color='black')
        city.nodes[u]['tipus'] = 'Cruilla'

        for v, edgesdict in nbrsdict.items():
            attr = g1.nodes[v]
            city.add_node(v, **attr, color='black')
            city.nodes[v]['tipus'] = 'Cruilla'

            eattr = edgesdict[0]
            if u != v:
                city.add_edge(u, v, **eattr,
                              tipus='carrer', color='red',
                              time=eattr['length'] / 1.5)

    nearest_nodes: dict[int, int] = {}
    parades_nodes: list[str] = []
    list_x: list[float] = []
    list_y: list[float] = []

    for u in g2.nodes:
        assert g2.nodes[u]['tipus'] == 'Parada'
        attr = g2.nodes[u]
        city.add_node(u, **attr, color='black')
        list_x.append(g2.nodes[u]['pos'][0])
        list_y.append(g2.nodes[u]['pos'][1])
        parades_nodes.append(u)

    # calculates the nearest node from a bus stop for each bus stop in g2
    parada_cruilla: list[int] = ox.nearest_nodes(g1, list_x, list_y,
                                                 return_dist=False)

    for i, u in enumerate(parades_nodes):
        nearest_nodes[u] = parada_cruilla[i]

    assert len(parada_cruilla) == len(nearest_nodes)

    # Add edges between the buses stops and their corresponding
    # nearest nodes from the streets graph
    for u, v, k in g2.edges(data=True):
        attr = k
        i = nearest_nodes[u]
        j = nearest_nodes[v]
        time = nx.shortest_path_length(g1, i, j, weight='length') / 5.5
        city.add_edge(u, v, **attr, time=time)

        coord_i = g1.nodes[i]['y'], g1.nodes[i]['x']
        coord_j = g1.nodes[j]['y'], g1.nodes[j]['x']
        coord_u = g2.nodes[u]['pos'][1], g2.nodes[u]['pos'][0]
        coord_v = g2.nodes[v]['pos'][1], g2.nodes[v]['pos'][0]

        city.add_edge(i, u, stipus='enllaç', color='green',
                      time=(haversine(coord_i, coord_u) / 1.5) + 150)

        city.add_edge(j, v, tipus='enllaç', color='green',
                      time=(haversine(coord_j, coord_v) / 1.5) + 150)

    return city


def show(g: CityGraph) -> None:
    """Shows the graph g in an interactive way on another window"""
    posicions = nx.get_node_attributes(g, 'pos')
    nx.draw(
        g,
        pos=posicions,
        with_labels=False,
        node_size=20,
        node_color='lightblue',
        edge_color='gray')
    plt.show()


def plot_city(g: CityGraph, filename: str) -> None:
    """
    Saves g as an image with the Barcelona
    map in the background as 'filename'.
    """

    city_map = StaticMap(3500, 3500)
    for node in g.nodes:
        if g.nodes[node]['tipus'] == 'Cruilla':
            city_map.add_marker(CircleMarker((
                                g.nodes[node]['pos'][0],
                                g.nodes[node]['pos'][1]),
                                g.nodes[node]['color'], 0))
        else:
            city_map.add_marker(CircleMarker((
                            g.nodes[node]['pos'][0],
                            g.nodes[node]['pos'][1]),
                            g.nodes[node]['color'], 4))

    for edge in g.edges:
        coord_1 = (g.nodes[edge[0]]['pos'][0], g.nodes[edge[0]]['pos'][1])
        coord_2 = (g.nodes[edge[1]]['pos'][0], g.nodes[edge[1]]['pos'][1])
        node_1 = (edge[0])
        node_2 = (edge[1])
        city_map.add_line(
            Line([coord_1, coord_2], g[node_1][node_2]['color'], 1))

    image = city_map.render()
    image.save(filename)


def plot_path(p: Path, filename: str) -> None:
    """
    Plots the shortest path to the destination on the Barcelona
    map and saves it as an image at 'filename'.
    """
    g = p.plot_graph
    city_map = StaticMap(3500, 3500)

    # Gets the map_pointer image which should
    # be named as 'map_pointer.png'and have size 100 x 100 pixels.
    map_pointer = 'map_pointer.png'

    for node in g.nodes:
        if g.nodes[node]['tipus'] == 'dest':
            # Tries to get a map_pointer image to draw
            # the destination node nicely.
            # Exception (image not found):
            # The destionation node would be a green dot.
            try:
                city_map.add_marker(IconMarker((
                                    g.nodes[node]['pos'][0],
                                    g.nodes[node]['pos'][1]), map_pointer,
                                    50, 50))
            except Exception:
                city_map.add_marker(CircleMarker((
                                g.nodes[node]['pos'][0],
                                g.nodes[node]['pos'][1]),
                                g.nodes[node]['color'], g.nodes[node]['size']))
        else:
            city_map.add_marker(CircleMarker((
                                g.nodes[node]['pos'][0],
                                g.nodes[node]['pos'][1]),
                                g.nodes[node]['color'], g.nodes[node]['size']))

    for edge in g.edges:
        coord_1 = (g.nodes[edge[0]]['pos'][0], g.nodes[edge[0]]['pos'][1])
        coord_2 = (g.nodes[edge[1]]['pos'][0], g.nodes[edge[1]]['pos'][1])
        node_1 = (edge[0])
        node_2 = (edge[1])
        city_map.add_line(
            Line([coord_1, coord_2], g[node_1][node_2]['color'], 10))

    image = city_map.render()
    image.save(filename)
