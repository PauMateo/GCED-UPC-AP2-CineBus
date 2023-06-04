# CineBus
Pau · (Mateo ∧ Fernández)
Wanna watch a movie? Choose one and go by bus!

## Getting Started
This project is divided in four parts: 

* `billboard.py` : Contains all the code related to obtaining the actual billboard and provifing search methods.

* `buses.py` : Contains all the code related to the construction of the buses graph.


* `city.py` : Contains all the code related to the construction of the city graph (that is, the street graph and the buses graph) and the search for routes between two points of the city.


* `demo.py` : Contains all the code related to user interface of the program.


### Prerequisites
This program is build in `python3` and `pip3`, both minimally updated. You can update them with the following commands:
```
pip3 install --upgrade pip3
pip3 install --upgrade python3
```
The librarys used are:
 `networkx` to manipulate graphs.
 `osmnx` to obtain city graphs (Barcelona in this case).
 `haversine` for calculating distances between coordinates.
 `staticmap` to draw and plot maps.
 `python-telegram-bot` to create and interact with a Telegram bot.
 `pandas` to read CSV files.
 `fuzzysearch` to do diffuse searches.
 `typing_extensions` to define a new name for a type.
