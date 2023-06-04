# CineBus 🎬🚌
Pau · (Mateo ∧ Fernández)
Wanna watch a movie? Choose one and go by bus!

## Getting Started 🚏<picture>
  <source srcset="https://fonts.gstatic.com/s/e/notoemoji/latest/1f92f/512.webp" type="image/webp">
  <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f92f/512.gif" alt="🤯" width="32" height="32">
</picture>
This project is divided in four parts: 

* `billboard.py` : Contains all the code related to obtaining the actual billboard and provifing search methods.

* `buses.py` : Contains all the code related to the construction of the buses graph.


* `city.py` : Contains all the code related to the construction of the city graph (that is, the street graph and the buses graph) and the search for routes between two points of the city.


* `demo.py` : Contains all the code related to user interface of the program.


### Prerequisites ❗
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
* `rich`, `loaders`, `pillow` for user interface
* `pickle` to save big datas to the computer (in this case, the osmnx graph of Bcn)
This las module is a Python's default one, so you shouldn't have to install it.

 
You can install this packages one by one with `pip3 install package_name`, or just with the following command:
```
pip3 install -r requirements.txt
```

Optionally, exclusifly for user's view, we reccommend to dowload the file `map_pointer.png` in the same directory where to run the program. It does not affect execution of the program.

## Usage 🤖
**Things to consider:**
- Currently, this project is exclusively confined to the city of Barcelona, some functionallities will not work outside Barcelona.
- The user interface is made in English, but the language of the Billboard it's in _spanish_. Therefore, all the names and search methods require to use the film names, cinemas names... in spanish.

The `demo.py` module offers a simple menu system for the user's interface. It needs to be executed in a __command prompt__, with the command `#>python demo.py` (or `#>py demo.py`,  depending on your python caller) at the same directory where the dowloaded files are. 

The functionalities offered by `demo.py` are as follows:
- Display today's Billboard and other information, such as all the cinemas and movies from the billboard, types of gernes...
- Offer filtering and searching methods to apply in the billboard
- Display the buses map and the city map.
- Display the indications and the path the user needs to take (by walking and maybe taking the bus) given it's time disponibility and location to go to the cinema to watch the earliest session of a movie he chooses. 
- Display the names and information of the project autors

<img src="CineBus_menu.png" > 


## Authors
Developed by [Pau Mateo Bernado](https://github.com/PauMateo) and [Pau Fernández Cester](https://github.com/PauFdz), first year students of Data Science and Engineering at UPC, 2022-23.

Contact us:  `pau.mateo.bernado@estudiantat.upc.edu`,  `pau.fernandez.cesterestudiantat.upc.edu`


