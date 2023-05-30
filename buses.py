from typing import TypeAlias, Any
import networkx as nx
import requests
import matplotlib.pyplot as plt
from staticmap import *
from PIL import Image


BusesGraph: TypeAlias = nx.Graph

def get_json_data():
    url = 'https://www.ambmobilitat.cat/OpenData/ObtenirDadesAMB.json'
    try:
        response = requests.get(url)

        if response.status_code == 200:
            json_data = response.json()

    except Exception:
        print(f"Error substracting data from {url}")
    
    return json_data


def get_linies() -> list[Any]:
    """returns a list of buses' lines"""
    data = get_json_data()
    data = data[list(data.keys())[0]]
    linies = data[list(data.keys())[1]]

    return linies[list(linies.keys())[0]]


def get_buses_graph() -> BusesGraph:

    Buses: BusesGraph = BusesGraph()
    linies = get_linies()
    node_anterior = ""

    for linia in linies:
        for parades in linia["Parades"]["Parada"]:
            if parades["Municipi"] == "Barcelona":
                node_attributes = {"tipus": "Parada", "nom": parades["Nom"], "pos": (parades["UTM_X"], parades["UTM_Y"]), "linies": parades["Linies"].split(sep= ' - ')}
                Buses.add_node(parades["CodAMB"], **node_attributes)
                
                if node_anterior != "":
                    edge_attributes = {"tipus": "Bus", "linies": []}
                    for linia in Buses.nodes[node_anterior]['linies']:
                        if linia in Buses.nodes[parades["CodAMB"]]['linies']:
                            edge_attributes["linies"].append(linia)

                    Buses.add_edge(node_anterior, parades["CodAMB"], **edge_attributes)

                node_anterior = parades["CodAMB"]

            else:
                node_anterior = ""

        node_anterior = ""

    return Buses



def show(g: BusesGraph) -> None:
     
    print(g.nodes["003402"], g.nodes["001409"], g.edges["003402", "001409"])
    posicions = nx.get_node_attributes(g, 'pos')
    nx.draw(g, pos = posicions, with_labels=False, node_size = 20, node_color='lightblue', edge_color='gray')
    plt.show()

def paint_nodes(g: BusesGraph, m: StaticMap) -> None:
    """Paints all the nodes from the graph g in the
    StaticMap m with the color red"""

    for index, node in g.nodes(data=True):
        coord = (node['pos'])
        marker_node = CircleMarker(coord, 'white', 2)
        m.add_marker(marker_node)


def paint_edges(g: BusesGraph, m: StaticMap) -> None:
    """Paints all the edges from the graph g in the
    StaticMap m with the color blue"""

    for n1 in g.edges(data=True):
        coord = (g.nodes[n1[0]]['pos'], g.nodes[n1[1]]['pos'])
        line = Line(coord, 'blue', 5)
        m.add_line(line)

def plot(g: BusesGraph, nom_fitxer: str) -> None:
    """
    # we get the openstreetmap to be the background
    url: str = 'https://www.openstreetmap.org/#map=12/41.3997/2.1664'
    m: StaticMap = StaticMap(1000, 1000, url_template=url)

    paint_nodes(g, m)
    paint_edges(g, m)

    image = m.render()
    image.save(nom_fitxer, quality=1000)
    """
    """
    :param g: a graph of the metro of the city
    :param filename: a path and name to save the image
    :effect: an image of g will be saved in filename
    """

    metro_map = staticmap.StaticMap(2000, 2000)
    for node in g.nodes:
        metro_map.add_marker(staticmap.CircleMarker(g.nodes[node]['pos'], "red", 10))
    for edge in g.edges:
        metro_map.add_line(staticmap.Line(g.nodes[[edge[0]]["pos"], g.nodes[edge[1]]["pos"]],
                                          "blue", 5))
    image = metro_map.render()
    image.save(nom_fitxer)
    



def main():
    graph = get_buses_graph()
    """plot(graph, "buses_graph.png")"""
    show(graph)
    

if __name__ == "__main__":
    main()
