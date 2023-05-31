from typing import TypeAlias
from dataclasses import dataclass

import osmnx as ox
import pickle
import networkx as nx
from buses import *

Coord: TypeAlias = tuple[float, float]   # (latitude, longitude
CityGraph: TypeAlias = nx.Graph
OsmnxGraph: TypeAlias = nx.MultiDiGraph


@dataclass
class Edge:
    ...


@dataclass
class Path:
    ...


def get_osmnx_graph() -> OsmnxGraph:
    '''Funció que obte i retorna el graf
    dels carrers de Barcelona'''

    graph: OsmnxGraph = ox.graph_from_place("Barcelona",
                                            network_type='walk',
                                            simplify=True)  # type: ignore

    for u, v, key, geom in graph.edges(data="geometry", keys=True):
        if geom is not None:
            del (graph[u][v][key]["geometry"])

    return graph


def find_path(ox_g: OsmnxGraph, g: CityGraph,
              src: Coord, dst: Coord) -> Path:
    '''Retorna el camí (Path) més curt entre
    els punts src i dst. '''
    ...


def save_osmnx_graph(g: OsmnxGraph, filename: str) -> None:
    '''Guarda el graf g al fitxer filename'''
    file = open(filename, 'wb')
    pickle.dump(g, file)
    file.close()


def load_osmnx_graph(filename: str) -> OsmnxGraph:
    '''Retorna el graf guardat al fitxer filename'''

    file = open(filename, 'rb')
    g = pickle.load(file)
    file.close()
    assert isinstance(g, OsmnxGraph)
    return g


#                                                                  (Unknown)
def nearest_node(g: OsmnxGraph, point: Coord) -> None | int:  # node id (int?)
    '''Funció que retorna el node més proper al punt donat
    al graf g. Retorna None si la distància és major a {?}'''
    X, Y = point[0], point[1]
    nodes, dist = ox.nearest_nodes(g, X, Y, return_dist=True)

    if dist > 1000:  # assumint que torna distància en metres (en teoria si xd)
        return None
    if type(nodes) == list:
        assert nodes[0] in g.nodes
        return nodes[0]  # quansevol d'aquests nodes ja ens està bé!
    return nodes


def nearest_node2(g: OsmnxGraph, point: Coord) -> int:
    '''Funció que retorna el node més proper al punt donat
    al graf g. Retorna None si la distància és major a {?}'''
    X, Y = point[0], point[1]
    nodes, dist = ox.nearest_nodes(g, X, Y, return_dist=True)

    if type(nodes) == list:
        print(nodes)
        return nodes[0], dist  # quansevol d'aquests nodes ja ens està bé!
    return nodes


def build_city_graph(g1: OsmnxGraph, g2: BusesGraph) -> CityGraph:
    '''Retorna un graf fusió de g1 i g2'''
    city: CityGraph = nx.Graph()
    # add cinemas here?

    for u, nbrsdict in g1.adjacency():
        city.add_node(u)
        city.nodes[u]['tipus'] = 'Cruilla'
        # for each adjacent node v and its (u, v) edges' information ...
        for v, edgesdict in nbrsdict.items():
            city.add_node(v)
            city.nodes[v]['tipus'] = 'Cruilla'  # no caldira, ja ho fem lin. 37

            eattr = edgesdict[0]
            city.add_edge(u, v, **eattr)

    nearest_nodes: dict[int, int] = {}  # Parada: Cruilla

    print('checkpoint')

    for u in g2.nodes():
        assert g2.nodes[u]['tipus'] == 'Parada'
        city.add_node(u)
        nearest_nodes[u] = nearest_node2(g1, g2.nodes[u]['pos'])

    for edge in g2.edges():
        assert g2.nodes[edge]['tipus'] == 'Bus'
        u, v = edge
        i = nearest_nodes[u]
        j = nearest_nodes[v]
        dist = nx.shortest_path_length(g1, i, j, weight='length') / 3
        city.add_edge(u, v, weight=dist)  # **attr
        city.add_edge(i, u, weight=0)
        city.add_edge(j, v, weight=0)

    '''for u, nbrsdict in g2.adjacency():
        assert g2.nodes[u]['tipus'] == 'Parada'
        city.add_node(u)

        if u not in nearest_nodes: pass
        for v, edge in nbrsdict.items():
            city.add_node(v)

            
            i = nearest_node2(g1, g2.nodes[u]['pos'])
            j = nearest_node2(g1, g2.nodes[v]['pos'])
            dist = nx.shortest_path_length(g1, i, j, weight='length') / 3
            #  attr = {"weight": dist}
            city.add_edge(u, v, weight=dist)  # **attr
            city.add_edge(i, u, weight=0)
            city.add_edge(j, v, weight=0)'''

    return city


def show(g: CityGraph) -> None:
    '''Mostra g de forma interactiva en una finestra'''
    ...


def plot(g: CityGraph, filename: str) -> None:
    '''Desa g com una imatge amb el mapa de la
    cuitat de fons en l'arxiu filename'''
    ...


def plot_path(g: CityGraph, p: Path, filename: str) -> None:
    '''Mostra el camí p en l'arxiu filename'''
    ...


try:
    c = load_osmnx_graph('prova.pickle')
    print(type(c))
    b = get_buses_graph()
    print(type(b))
except Exception:
    c = get_osmnx_graph()
    save_osmnx_graph(c, 'prova.pickle')
    b = get_buses_graph()
    print(type(b))


city = build_city_graph(c, b)
print(type(city))

a = input()


def show(g: CityGraph) -> None:
    
    nx.draw(g, with_labels=False, node_size=20, node_color='lightblue', edge_color='gray')
    plt.show()


show(city)
