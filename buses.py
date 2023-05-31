from typing import TypeAlias, Any
import networkx as nx
import requests
import matplotlib.pyplot as plt
from staticmap import Line, CircleMarker, StaticMap


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
                node_attributes = {
                    "tipus": "Parada",
                    "nom": parades["Nom"],
                    "pos": (
                        parades["UTM_X"],
                        parades["UTM_Y"]),
                    "linies": parades["Linies"].split(
                        sep=' - ')}
                Buses.add_node(parades["CodAMB"], **node_attributes)

                if node_anterior != "":
                    edge_attributes = {"tipus": "Bus", "linies": []}
                    for linia in Buses.nodes[node_anterior]['linies']:
                        if linia in Buses.nodes[parades["CodAMB"]]['linies']:
                            edge_attributes["linies"].append(linia)

                    Buses.add_edge(
                        node_anterior,
                        parades["CodAMB"],
                        **edge_attributes)

                node_anterior = parades["CodAMB"]

            else:
                node_anterior = ""

        node_anterior = ""

    return Buses


def show(g: BusesGraph) -> None:

    print(g.nodes["003402"], g.nodes["001409"], g.edges["003402", "001409"])
    posicions = nx.get_node_attributes(g, 'pos')
    nx.draw(
        g,
        pos=posicions,
        with_labels=False,
        node_size=20,
        node_color='lightblue',
        edge_color='gray')
    plt.show()


def plot(g: BusesGraph, nom_fitxer: str) -> None:
    """
    :param g: a graph of the metro of the city
    :param nom_fitxer: a path and name to save the image
    """

    buses_map = StaticMap(3500, 3500)
    for pos in nx.get_node_attributes(g, 'pos').values():
        buses_map.add_marker(CircleMarker((pos[1], pos[0]), "red", 6))
    for edge in g.edges:
        coord_1 = (g.nodes[edge[0]]['pos'][1], g.nodes[edge[0]]['pos'][0])
        coord_2 = (g.nodes[edge[1]]['pos'][1], g.nodes[edge[1]]['pos'][0])
        buses_map.add_line(Line([coord_1, coord_2], "blue", 2))

    image = buses_map.render()
    image.save(nom_fitxer)


def main():
    graph = get_buses_graph()
    plot(graph, "buses_graph.png")
    show(graph)


if __name__ == "__main__":
    main()
