from typing import TypeAlias
from dataclasses import dataclass
import osmnx as ox
import pickle
import networkx as nx
from buses import *
from haversine import haversine

Coord: TypeAlias = tuple[float, float]   # (latitude, longitude)
CityGraph: TypeAlias = nx.Graph
OsmnxGraph: TypeAlias = nx.MultiDiGraph


@dataclass
class Path:
    source: int
    dest: int
    path: list[int]
    path_graph: nx.Graph
    plot_graph: nx.Graph
    path_indications: str
    city_graph: CityGraph
    time: int  # minuts


def get_osmnx_graph() -> OsmnxGraph:
    '''Funció que obte i retorna el graf
    dels carrers de Barcelona'''

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
    '''Retorna el camí (Path) més curt entre
    els punts src i dst. '''
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

    path_graph = build_path_graph(src_node, dst_node, shortest_path[1:-1], g)
    path: Path = Path(src_node, dst_node,
                      shortest_path[1:-1],
                      path_graph, path_graph, '', g, int(time) // 60)
    try:
        indic = path_indications(path)

    except Exception:
        indic = ''

    plot = build_plot_graph(src_node,
                            dst_node,
                            shortest_path[1:-1],
                            path.city_graph,
                            ox_g)
    path: Path = Path(src_node, dst_node,
                      shortest_path[1:-1],
                      path_graph, plot, indic, g, int(time) // 60)

    return path


def build_plot_graph(
        src: int,
        dest: int,
        path: list[int],
        g: CityGraph,
        ox_g: OsmnxGraph):

    plot_graph: nx.Graph = nx.Graph()
    plot_graph.add_node(src, **g.nodes[src], size=25)
    plot_graph.add_node(dest, **g.nodes[dest], size=25)
    plot_graph.nodes[dest]['color'] = 'bright_green'
    for node in path:
        if g.nodes[node]['tipus'] == 'Cruilla':
            plot_graph.add_node(node, **g.nodes[node], size=0)
        else:
            plot_graph.add_node(node, **g.nodes[node], size=15)

    node_ant = src
    for node in path:
        if g.nodes[node_ant]['tipus'] == 'Parada' \
                and g.nodes[node]['tipus'] == 'Parada':
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
            shortest_path = nx.shortest_path(
                ox_g, nr_node_ant, nr_node, weight='length')
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
            attr = g.get_edge_data(node_ant, node)
            plot_graph.add_edge(node_ant, node, **attr)
            node_ant = node
    attr = g[node_ant][dest]
    plot_graph.add_edge(node_ant, dest, **attr)

    return plot_graph


def build_path_graph(src: int, dest: int, path: list[int], g: CityGraph):
    '''...'''

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
    '''Donat un recorregut, retorna les indicacions d'aquest.'''

    indic: str = ''
    g: nx.Graph = p.path_graph
    i = 1
    n: int | str = p.path[i]
    n_ant: int | str = p.path[i - 1]

    # en cas que no s'hagi d'agafar bus:
    if all(g.nodes[node]['tipus'] != 'Parada' for node in g.nodes):
        indic = 'Camina fins al cinema. No cal que agafis bus!'
        return indic

    while i < len(p.path):
        # ara estem caminant
        while g.nodes[n]['tipus'] == 'Cruilla' and i < len(p.path) - 1:
            i += 1
            n_ant, n = n, p.path[i]

        if i == len(p.path) - 1:
            indic += "Camina el que queda fins al Cinema."
            return indic

        # ara estem en bus
        assert g.nodes[n]['tipus'] == 'Parada' and \
                                      g.nodes[n_ant]['tipus'] == 'Cruilla'

        linia_parada: list[tuple[str, int]] = []  # (linia, parada on s'agafa)
        parada: int = n  # per controlar on fem canvis de línia
        ultima_parada: int = parada

        i += 1
        n_ant, n = p.path[i - 1], p.path[i]

        # cas trivial: passar per una parada però sense agafar bus.
        if g.nodes[n]['tipus'] == 'Cruilla':
            continue

        # variables per controlar els canvis de linia del trajecte en bus
        linies: set[str] = set([])
        noves_linies: set[str] = set(g[n_ant][n]['linies'])
        i += 1
        n_ant, n = n, p.path[i]

        # en cas que només s'agafi una parada de bus
        if g.nodes[n]['tipus'] == 'Cruilla':
            lin = noves_linies.pop()
            indic += f"Camina fins la parada {g.nodes[n_ant]['nom']} " + \
                     f"i agafa l'autobus {lin} fins la parada " + \
                     f"{g.nodes[n]['nom']}."
            p.city_graph.nodes[n_ant]['color'] = 'magenta'
            continue

        linies = noves_linies
        while g.nodes[n]['tipus'] == 'Parada' and i < len(p.path)-1:
            noves_linies = set(g[n_ant][n]['linies'])
            if linies & noves_linies == set():
                linia = linies.pop()  # qualsevol de les linies
                linia_parada.append((linia, parada))
                parada = n_ant  # actualitzar parada(transbord)
                linies = noves_linies
            else:
                linies = linies & noves_linies
            ultima_parada = n
            i += 1
            n_ant, n = n, p.path[i]

        linia_parada.append((linies.pop(), parada))

        # afegim el recorregut fet en bus
        lin, par = linia_parada[0]
        indic += f"Camina fins la parada {g.nodes[par]['nom']}, " + \
                 f"i agafa el bus {lin}.\n"

        p.city_graph.nodes[par]['color'] = 'magenta'

        for lin, par in linia_parada[1:]:
            indic += f"Viatja en bus fins la parada {g.nodes[par]['nom']}," + \
                     f" i fes transbord a la linia {lin}.\n"
            p.city_graph.nodes[par]['color'] = 'magenta'

        lin, par = linia_parada[-1]
        indic += f"Viatja en bus fins a la parada " + \
                 f"{g.nodes[ultima_parada]['nom']}.\n"

    return indic


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

    parada_cruilla: list[int] = ox.nearest_nodes(g1, list_x, list_y,
                                                 return_dist=False)

    for i, u in enumerate(parades_nodes):
        nearest_nodes[u] = parada_cruilla[i]

    assert len(parada_cruilla) == len(nearest_nodes)

    for u, v, k in g2.edges(data=True):
        #  assert g2.nodes[edge]['tipus'] == 'Bus'
        attr = k
        i = nearest_nodes[u]
        j = nearest_nodes[v]
        time = nx.shortest_path_length(g1, i, j, weight='length') / 8.5
        city.add_edge(u, v, **attr, time=time)  # **attr

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
    '''Mostra g de forma interactiva en una finestra'''
    posicions = nx.get_node_attributes(g, 'pos')
    nx.draw(
        g,
        pos=posicions,
        with_labels=False,
        node_size=20,
        node_color='lightblue',
        edge_color='gray')
    plt.show()


def plot(g: CityGraph, filename: str) -> None:
    '''Desa g com una imatge amb el mapa de la
    cuitat de fons en l'arxiu filename'''

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
    # hem tret paràmetre g: CityGraph
    '''Mostra el camí p en l'arxiu filename'''
    g = p.plot_graph
    city_map = StaticMap(3500, 3500)

    for node in g.nodes:
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


input('press enter to continue')

city = build_city_graph(c, b)
plot(city, 'city_graph.png')
input('find p:')
p = find_path(c, city, (41.386707215473166, 2.1284072680134725),
              (41.40436757284038, 2.1744032496886416))
indic = p.path_indications

input('Show indications:')
print(indic)
input('Type nodes:')
for node in p.path_graph:
    print(p.path_graph.nodes[node])
for u, v, k in p.path_graph.edges(data=True):
    print(k)
plot_path(p, "plot_plath.png")
