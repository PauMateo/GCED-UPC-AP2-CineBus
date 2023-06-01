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
    source: int
    dest: int
    path: list[int]
    path_graph: nx.Graph
    



def get_osmnx_graph() -> OsmnxGraph:
    '''Funció que obte i retorna el graf
    dels carrers de Barcelona'''

    graph: OsmnxGraph = ox.graph_from_place("Barcelona",
                                            network_type='walk',
                                            simplify=True)  # type: ignore

    for u, v, key, geom in graph.edges(data="geometry", keys=True):
        if geom is not None:
            del (graph[u][v][key]["geometry"])
    for node in graph.nodes():
        graph.nodes[node]['pos'] = (graph.nodes[node]['x'], graph.nodes[node]['y'])
    return graph


def find_path(ox_g: OsmnxGraph, g: CityGraph,
              src: Coord, dst: Coord) -> Path:
    '''Retorna el camí (Path) més curt entre
    els punts src i dst. '''
    src_node, dist_src= ox.nearest_nodes(ox_g, src[1], src[0], return_dist=True)
    dst_node, dist_dst = ox.nearest_nodes(ox_g, dst[1], dst[0], return_dist=True)
    assert dist_src < 10000 and dist_dst < 10000
    shortest_path = nx.shortest_path(g, src_node, dst_node, weight='length', method='dijkstra')
    p = build_path_graph(src_node, dst_node, shortest_path, g)
    path: Path = Path(src_node, dst_node, shortest_path[1:-1], p)
    return path


def build_path_graph(src: int, dest: int, path: list[int], g: CityGraph):
    
    path_graph: nx.Graph = nx.Graph()
    path_graph.add_node(src, **g.nodes[src])
    path_graph.add_node(dest, **g.nodes[dest])  
    for node in path:
        path_graph.add_node(node, **g.nodes[node])

    node_ant = src
    for node in path:
        attr = g[str(node_ant)][str(node)]
        path_graph.add_edge(node_ant, node, **attr)
        node_ant = node
    attr = g[node_ant][dest]
    path_graph.add_edge(node_ant, dest, **attr)

    return path_graph


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



def build_city_graph(g1: OsmnxGraph, g2: BusesGraph) -> CityGraph:
    '''Retorna un graf fusió de g1 i g2'''
    city: CityGraph = nx.Graph()
    # add cinemas here?

    for u, nbrsdict in g1.adjacency():
        attr = g1.nodes[u]
        city.add_node(u, **attr)
        city.nodes[u]['tipus'] = 'Cruilla'
        # for each adjacent node v and its (u, v) edges' information ...
        for v, edgesdict in nbrsdict.items():
            attr = g1.nodes[v]
            city.add_node(v, **attr)
            city.nodes[v]['tipus'] = 'Cruilla'  # no caldira, ja ho fem lin. 37

            eattr = edgesdict[0]
            if u != v:
                city.add_edge(u, v, **eattr, tipus='carrer')


    print('checkpoint 1')

    nearest_nodes: dict[int, int] = {}
    list_x: list[float] = []
    list_y: list[float] = []

    for u in g2.nodes:
        assert g2.nodes[u]['tipus'] == 'Parada'
        attr = g2.nodes[u]
        city.add_node(u, **attr)
        list_x.append(g2.nodes[u]['pos'][0])  # ojo amb girar coordenades xd
        list_y.append(g2.nodes[u]['pos'][1])

    parada_cruilla: list[int] = ox.nearest_nodes(g1,
                                                   list_x,
                                                   list_y, return_dist=False)


    for i, u in enumerate(g2.nodes()):
        nearest_nodes[u] = parada_cruilla[i]

    assert len(parada_cruilla) == len(nearest_nodes)
    print('checkpoint 2')

    for u, v, k in g2.edges(data=True):
        #  assert g2.nodes[edge]['tipus'] == 'Bus'
        attr = k
        i = nearest_nodes[u]
        j = nearest_nodes[v]
        dist = nx.shortest_path_length(g1, i, j, weight='length') / 3
        city.add_edge(u, v, **attr, length=dist)  # **attr
        city.add_edge(i, u, length=0)
        city.add_edge(j, v, length=0)

    return city


def show(g: CityGraph) -> None:
    '''Mostra g de forma interactiva en una finestra'''
    posicions = nx.get_node_attributes(g,'pos')
    nx.draw(g, pos=posicions, with_labels=False, node_size=20, node_color='lightblue', edge_color='gray')
    plt.show()


def plot(g: CityGraph, filename: str) -> None:
    '''Desa g com una imatge amb el mapa de la
    cuitat de fons en l'arxiu filename'''
    city_map = StaticMap(3500, 3500)
    for pos in nx.get_node_attributes(g, 'pos').values():
        city_map.add_marker(CircleMarker((pos[0], pos[1]), "red", 6))
    for edge in g.edges:
        coord_1 = (g.nodes[edge[0]]['pos'][0], g.nodes[edge[0]]['pos'][1])
        coord_2 = (g.nodes[edge[1]]['pos'][0], g.nodes[edge[1]]['pos'][1])
        city_map.add_line(Line([coord_1, coord_2], "blue", 2))

    image = city_map.render()
    image.save(filename)


def plot_path(p: Path, filename: str) -> None:  #hem tret paràmetre g: CityGraph
    '''Mostra el camí p en l'arxiu filename'''
    g = p.path_graph
    city_map = StaticMap(3500, 3500)
    for pos in nx.get_node_attributes(g, 'pos').values():
        city_map.add_marker(CircleMarker((pos[0], pos[1]), "red", 6))
    for edge in g.edges:
        coord_1 = (g.nodes[edge[0]]['pos'][0], g.nodes[edge[0]]['pos'][1])
        coord_2 = (g.nodes[edge[1]]['pos'][0], g.nodes[edge[1]]['pos'][1])
        city_map.add_line(Line([coord_1, coord_2], "blue", 2))

    image = city_map.render()
    image.save(filename)


def print_osmnx_graph(g: OsmnxGraph) -> None:
    street_graph_projected = ox.project_graph(g)
    ox.plot_graph(street_graph_projected)



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



input('press enter to continu')

city = build_city_graph(c, b)
show(city)
plot(city, "city_graph.png")
"""show(city)"""
"""p=find_path(c,city, (41.40461, 2.080503), (41.41359, 2.079825))"""
"""print(city.get_edge_data(7212391973, 539787390))
plot_path(p, "plot_plath.png")"""
