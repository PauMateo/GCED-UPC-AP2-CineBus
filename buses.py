from typing import TypeAlias, Any
import networkx as nx
import requests
import matplotlib.pyplot as plt
from staticmap import Line, CircleMarker, StaticMap


BusesGraph: TypeAlias = nx.Graph


def get_json_data():
    '''Descarrega les dades de les linies i
    recorreguts de busos de l'AMB'''
    url = 'https://www.ambmobilitat.cat/OpenData/ObtenirDadesAMB.json'
    try:
        response = requests.get(url)
        json_data = response.json()

    except Exception:
        print(f"Error substracting data from {url}")
        exit(1)

    return json_data


def get_linies() -> list[Any]:
    """
    Returns a list of buses' lines and its information extracted
    from the json data.
    """
    data = get_json_data()
    data = data[list(data.keys())[0]]
    linies = data[list(data.keys())[1]]

    return linies[list(linies.keys())[0]]


def get_buses_graph() -> BusesGraph:
    """
    Creates the buses graph using the json_data and returns
    it as BusesGraph type.
    """
    Buses: BusesGraph = BusesGraph()
    linies = get_linies()
    node_anterior = ""

    for linia in linies:
        # we access the stops of a single line
        for parades in linia["Parades"]["Parada"]:
            # we verify the stops are from Barcelona city
            if parades["Municipi"] == "Barcelona":
                node_attributes = {
                    "tipus": "Parada",
                    "nom": parades["Nom"],
                    "pos": (
                        parades["UTM_Y"],
                        parades["UTM_X"]),
                    "linies": parades["Linies"].split(
                        sep=' - ')}
                Buses.add_node(parades["CodAMB"], **node_attributes)

                if node_anterior != "":
                    edge_attributes = {"tipus": "Bus", "linies": []}

                    for linia in Buses.nodes[node_anterior]['linies']:
                        if linia in Buses.nodes[parades["CodAMB"]]['linies']:
                            edge_attributes["linies"].append(linia)

                    if node_anterior != parades["CodAMB"]:
                        Buses.add_edge(
                            node_anterior,
                            parades["CodAMB"],
                            **edge_attributes, color='blue')
                node_anterior = parades["CodAMB"]
            else:
                node_anterior = ""

        node_anterior = ""

    return Buses


def show(g: BusesGraph) -> None:
    """Shows the buses graph using matplotlib.pyplot."""
    posicions = nx.get_node_attributes(g, 'pos')
    nx.draw(
        g,
        pos=posicions,
        with_labels=False,
        node_size=20,
        node_color='lightblue',
        edge_color='gray')
    plt.show()


def plot_buses(g: BusesGraph, nom_fitxer: str) -> None:
    """
    Plots the buses graph with the Barcelona map at the backraound and saves
    the file as "nom_fitxer.png".
    :param g: a graph of the metro of the city
    :param nom_fitxer: a path and name to save the image
    """
    buses_map = StaticMap(3500, 3500)

    for pos in nx.get_node_attributes(g, 'pos').values():
        buses_map.add_marker(CircleMarker((pos[0], pos[1]), "black", 6))

    for edge in g.edges:
        node_1 = edge[0]
        node_2 = edge[1]
        coord_1 = (g.nodes[node_1]['pos'][0], g.nodes[edge[0]]['pos'][1])
        coord_2 = (g.nodes[node_2]['pos'][0], g.nodes[edge[1]]['pos'][1])
        buses_map.add_line(
            Line([coord_1, coord_2], g[node_1][node_2]['color'], 2))

    image = buses_map.render()
    image.save(nom_fitxer)
