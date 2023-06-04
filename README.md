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
* `typing_extensions` to define new types.
* `BeautifulSoup`, `requests` for web scraping.
* `networkx` to manipulate graphs.
* `osmnx` to obtain streets graphs .
* `haversine` calculating distances between coordinates.
* `staticmap` to draw and plot maps.
* `pickle` to dowload graph data so we don't
* `rich`, `loaders`, `pillow` for user interface
 
You can install this packages one by one with `pip3 install package_name`, or just with the following command:
```
pip3 install -r requirements.txt
```

Optionally, exclusifly for user's view, we reccommend to dowload the file ... . It does not affect execution of the program.

## Usage
**Things to consider:**
- Currently, this project is exclusively confined to the city of Barcelona, some functionallities will not work outside Barcelona.


