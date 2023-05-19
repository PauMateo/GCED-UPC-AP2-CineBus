from dataclasses import dataclass
import json
import requests
from bs4 import BeautifulSoup as BSoup


@dataclass
class Film:
    title: str
    genre: str
    director: str
    actors: list[str]


@dataclass
class Cinema:
    name: str
    address: str


@dataclass
class Projection:
    film: Film
    cinema: Cinema
    start: tuple[int, int]  # start time
    end: tuple[int, int]  # end time
    duration: int  # minutes
    language: str  # V.O or Spanish
    ...


@dataclass
class Billboard:
    films: list[Film]
    cinemas: list[Cinema]
    projections: list[Projection]
    ...  # metodes per cercar-hi inormacio !!


def read() -> Billboard:
    '''Funcio que descarrega i retorna les dades
    necessaries i retorna la cartellera actual
    '''
    bboard: Billboard = Billboard([], [], [])

    urls = [
        "https://www.sensacine.com/cines/cines-en-72480/",
        "https://www.sensacine.com/cines/cines-en-72480/?page=2",
        "https://www.sensacine.com/cines/cines-en-72480/?page=3"]

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

            cinema = Cinema(name, address)
            bboard.cinemas.append(cinema)

            # today's panel is:
            actual_panel = panels[i].find('div', class_='item-0')

            # build films; iterate through the current cinema's films
            if actual_panel is None:
                continue

            for info in actual_panel.find_all('div', class_='item_resa'):

                data = json.loads(info.find('div', class_='j_w')['data-movie'])
                film = Film(data['title'],
                            data['genre'],
                            data['directors'][0],
                            data['actors'])

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
                    duration = (end[0] - start[0])*60 + end[1] - start[1]

                    projection = Projection(film, cinema,
                                            start, end, duration, language)
                    bboard.projections.append(projection)

    return bboard
