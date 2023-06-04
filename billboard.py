import requests
import json

from dataclasses import dataclass
from bs4 import BeautifulSoup as BSoup
from typing import TypeAlias
from constants import cinemas_coords


Coord:  TypeAlias = tuple[float, float]   # (latitude, longitude)


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
                             'time', 'duration', 'language', 'city']
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

    def _filter_city(self, x: Projection, filter: str) -> bool:

        return filter in x.cinema.address

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

    for url in urls:
        try:
            r = requests.get(url)
            soup = BSoup(r.content, "lxml")
        except Exception:
            print(f'Error suobstracting billboard from {url}')
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
