from dataclasses import dataclass
import requests
import json
from bs4 import BeautifulSoup as BSoup
from typing import TypeAlias
#  import traceback

Coord:  TypeAlias = tuple[float, float]   # (latitude, longitude)

'''@dataclass  # atlernativa? millor? més còmode a la vista...
class Coord:
    x: float
    y: float'''


@dataclass
class Film:
    title: str
    genres: list[str]
    director: str
    actors: list[str]


@dataclass
class Cinema:
    name: str
    address: str
    coord: Coord


@dataclass
class Projection:
    film: Film
    cinema: Cinema
    start: tuple[int, int]  # start time
    end: tuple[int, int]  # end time
    duration: int  # minutes
    language: str  # V.O or Spanish


@dataclass
class Billboard:
    films: list[Film]
    cinemas: list[Cinema]
    projections: list[Projection]
    poss_filters: list[str]  # llista de possibles filtres que es poden aplicar
    genres: set[str]  # conjunt dels diferents gèneres de les películes

    def __init__(self, f: list[Film] = [], c: list[Cinema] = [],
                 p: list[Projection] = [], g: set[str] = set()):
        '''Constructor'''

        self.films = f
        self.cinemas = c
        self.projections = p
        self.poss_filters = ['genre', 'director', 'film', 'cinema',
                             'time', 'duration', 'language']
        self.genres = g

    def filter(self, filters: dict[str, str]) -> list[Projection]:
        '''Retorna la cartellera aplicant el filtre donat. Els possibles tipus
        de llistes son a la llista self.poss_filters. El format és:
        {tipus_filtre: filtre}.
        El filtre time retorna les projeccions que
        comencen i acaben dins l'horari indicat, i el format és:
        {time: hh:mm-hh:mm} (start-end).
        El filtre duration retorna totes les projeccions de durada
        igual o inferior a la donada, en minuts.
        El filtre genre retorna totes les projeccions que siguin dels
        gèneres donats, i el format és: {genre: genre1-genre2-...}. Es poden
        donar múltiples gèneres. La resta de filtres actuen obviament.
        '''

        try:
            assert all([k in self.poss_filters for k in filters.keys()])

            return [x for x in self.projections if
                    all([self._apply_filter(x, f) for f in filters.items()])
                    ]

        except Exception:
            raise ValueError
            '''e = traceback.format_exc()
            print(f'\n \n {e} \n \n \n')
            raise Exception('...')'''

    def _filter_time(self, x: Projection, filter: str) -> bool:
        '''Aplica per separat el filtre d'horari a una
        projecció x. Retorna True si l'horari de la
        projecció donada est9à inclòs dins del del filtre.'''
        s, e = filter.split('-')
        start = tuple(map(int, s.split(':')))
        end: tuple[int, int] = tuple(map(int, e.split(':')))

        if end < start:
            return (start <= x.start) and \
                        (start <= x.end <= (end[0]+24, end[1]))
        elif x.end < x.start:
            return (start <= x.start) and \
                        (start <= (x.end[0]+24, x.end[1]) <= end)
        return (start <= x.start) and (start <= x.end <= end)

    def _filter_duration(self, x: Projection, filter: str) -> bool:
        '''Filtre de tipus duration'''
        return x.duration <= int(filter)

    def _filter_cinema(self, x: Projection, filter: str) -> bool:
        '''Filtre de tipus cinema'''
        return x.cinema.name == filter

    def _filter_genre(self, x: Projection, filter: str) -> bool:
        '''Filtre de tipus genre '''
        return all([g in x.film.genres for g in filter.split('-')])

    def _filter_film(self, x: Projection, filter: str) -> bool:
        ''''''
        return x.film.title == filter

    def _filter_language(self, x: Projection, filter: str) -> bool:
        ''''''
        return x.language == filter

    def _filter_director(self, x: Projection, filter: str) -> bool:
        ''''''
        return x.language == filter

    def _apply_filter(self, x: Projection, flt: tuple[str, str]) -> bool:
        '''Aplica el filtre donat a la projecció x. Retorna True si
        x compleix els requisits del filtre, i False altrament.'''

        return getattr(self, '_filter_' + flt[0])(x, flt[1])


def read() -> Billboard:
    '''Funció que descarrega les dades necessaries
    i retorna la cartellera del dia actual.
    '''
    bboard: Billboard = Billboard()

    urls = [
        "https://www.sensacine.com/cines/cines-en-72480/",
        "https://www.sensacine.com/cines/cines-en-72480/?page=2",
        "https://www.sensacine.com/cines/cines-en-72480/?page=3"]

    cinemas_coords: dict[str, Coord] = {
     'Arenas Multicines 3D': (41.3772755040237, 2.1494606118543174),
     'Aribau Multicines': (41.38627791232003, 2.1626466396047315),
     'Balmes Multicines': (41.40736701577681, 2.1386003665962647),
     'Boliche Cinemes': (41.395455693930685, 2.1537420837800743),
     'Bosque Multicines': (41.40170100944678, 2.151862866595919),
     'Cine Capri': (41.32596975311035, 2.0953600684360474),
     'Cinebaix': (41.38219022211328, 2.0450222819345742),
     'Cinema Comedia': (41.389840893154734, 2.1676697261098146),
     'Cinemes Can Castellet': (41.34543643591452, 2.0405818107673084),
     'Cinemes Girona': (41.399794384796934, 2.164527008925862),
     'Cinemes Sant Cugat': (41.469787854906144, 2.0901121242699876),
     'Cines Montcada': (41.494336421716746, 2.1802964954365134),
     'Cines Verdi Barcelona': (41.40418671718023, 2.156881199733329),
     'Cinesa Diagonal 3D': (41.39403763128772, 2.136224366595472),
     'Cinesa Diagonal Mar 18': (41.410455041612835, 2.216579268441141),
     'Cinesa La Farga 3D': (41.36332421392511, 2.10484096843832),
     'Cinesa La Maquinista 3D': (41.43972724360848, 2.19825733591856),
     'Cinesa SOM Multiespai': (41.435657030361924, 2.1807281512581507),
     'Filmax Gran Via 3D': (41.35838637725132, 2.1284332512534734),
     'Full HD Cinemes Centre Splau': (41.34768595488537, 2.0787896276608895),
     'Glòries Multicines': (41.40545590868874, 2.192622751256335),
     'Gran Sarrià Multicines': (41.394968294956726, 2.1339804089255914),
     'Maldá Arts Forum': (41.383427668697074, 2.17389273775988),
     'Ocine Màgic': (41.44394440377754, 2.230652241452959),
     'Renoir Floridablanca': (41.3818434726659, 2.162643654944318),
     'Sala Phenomena Experience': (41.409265798307516, 2.171714535916728),
     'Yelmo Cines Baricentro': (41.50844678386131, 2.138359280097517),
     'Yelmo Cines Icaria 3D': (41.390815346532214, 2.1981648665952647),
     'Zumzeig Cinema': (41.37754823657382, 2.145091453099332),
     'Yelmo Cines Sant Cugat': (41.48365672049728, 2.0538435271627873)
    }

    for url in urls:
        try:
            r = requests.get(url)
            soup = BSoup(r.content, "lxml")
        except Exception:
            print(f'Error sobstracting billboard form {url}')
            return bboard  # return empty BillBoard

        headers = soup.find_all('div', class_="margin_10b j_entity_container")
        panels = soup.find_all('div', class_='tabs_box_panels')

        cinema: Cinema
        film: Film
        projection: Projection

        for i in range(len(headers)):
            # build cinema
            name = headers[i].a.text[1:-1]
            address = headers[i].find_all(
                'span', class_="lighten")[1].text[1:-1]

            cinema = Cinema(name, address, cinemas_coords[name])
            bboard.cinemas.append(cinema)

            # today's panel is:
            actual_panel = panels[i].find('div', class_='item-0')

            if actual_panel is None:
                continue
            # build films; iterate through the current cinema's films
            for info in actual_panel.find_all('div', class_='item_resa'):

                data = json.loads(info.find('div', class_='j_w')['data-movie'])
                film = Film(data['title'],
                            data['genre'],
                            data['directors'][0],
                            data['actors'])

                for genre in data['genre']:
                    bboard.genres.add(genre)
                if film not in bboard.films:
                    bboard.films.append(film)

                # build projections
                if info.span.text == 'Digital':
                    language = 'V.O.'
                else:
                    language = 'Spanish'

                for session in info.find_all('em'):
                    start: tuple[int, int]
                    end: tuple[int, int]
                    duration: int

                    times = json.loads(session['data-times'])

                    start = times[0].split(':')
                    start = int(start[0]), int(start[1])
                    end = times[2].split(':')
                    end = int(end[0]), int(end[1])
                    if end < start:
                        duration = (end[0] + 24 - start[0]) * \
                            60 + end[1] - start[1]
                    else:
                        duration = (end[0] - start[0]) * 60 + end[1] - start[1]

                    projection = Projection(film, cinema,
                                            start, end, duration, language)
                    bboard.projections.append(projection)

    bboard.projections.sort(key=lambda t: t.start)
    bboard.cinemas.sort(key=lambda c: c.name)
    bboard.films.sort(key=lambda f: f.title)

    return bboard
