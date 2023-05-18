from dataclasses import dataclass
import json
import urllib.request as ur
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
    time: tuple[int, int]
    language: str  # VSO or Spanish
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

    '''pag1 = "https://www.sensacine.com/cines/cines-en-72480/"
    pag2 = "https://www.sensacine.com/cines/cines-en-72480/?page=2" '''
    pag3 = "https://www.sensacine.com/cines/cines-en-72480/?page=3"

    # list_urls = [pag1, pag2, pag3]
    list_urls = [pag3]

    # user agent to web scraping
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        + 'AppleWebKit/537.36 (KHTML, like Gecko)'
        + ' Chrome/58.0.3029.110 Safari/537.3'}
    for url in list_urls:
        try:
            req = ur.Request(url, headers=headers)
            r = ur.urlopen(req).read()
            soup = BSoup(r, "lxml")
        except Exception:
            print(f'Error sobstracting billboard form {pag3}')
            return bboard  # return empty BillBoard

        film_html = soup.find_all('div', class_="tabs_box_pan item-0")
        cin_html = soup.find_all('div', class_='margin_10b j_entity_container')

        cinema: Cinema
        film: Film
        projection: Projection

        j = 0  # index to iterate the movies
        for i in range(len(cin_html)):
            # build cinema
            name = cin_html[i].find('a').text[1:-1]
            address = cin_html[i].find_all(
                'span', class_='lighten')[1].text[1:-1]

            cinema = Cinema(name, address)
            bboard.cinemas.append(cinema)

            # check if the set of films belong to the corresponding cinema,
            # in case one cinema had no sessions
            x = json.loads(
                film_html[j].find('div', class_='j_w')['data-theater'])

            if x['name'].strip() == cinema.name:
                # build films; iterate through the current cinema's films
                for info in film_html[j].find_all(
                            'div', class_='item_resa'):
                    data = json.loads(info.find(  # data of the movie
                                    'div', class_='j_w')['data-movie'])

                    film = Film(data['title'], data['genre'],
                                data['directors'][0], data['actors'])
                    bboard.films.append(film)

                    # build projections
                    if info.find('span', class_='bold').text == 'Digital':
                        language = 'Spanish'
                    else:
                        language = 'VO'

                    for session in info.find_all('em'):
                        time: tuple[int, int]
                        time = int(session.text[0:2]), int(session.text[3:5])

                        projection = Projection(film, cinema, time, language)
                        bboard.projections.append(projection)
                j += 1

    return bboard

read()
