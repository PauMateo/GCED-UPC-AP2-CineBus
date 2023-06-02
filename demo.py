import billboard
import os
from rich.table import Table
from rich.panel import Panel
from rich import box
import city
import time
from loaders import TextLoader
import rich.console
#  from constants import genres as film_genres
from constants import film_genres
from PIL.Image import Image as ImageType
from PIL import Image as Image

'''console = rich.console.Console()
Bus: city.BusesGraph
Streets: city.OsmnxGraph
City: city.CityGraph
Bboard: billboard.Billboard'''

loader = TextLoader(colour='yellow',
                    text='Loading',
                    animation='loop',
                    speed=.2)
console = rich.console.Console()
Bus: city.BusesGraph
Streets: city.OsmnxGraph
City: city.CityGraph
Bboard: billboard.Billboard


def clear() -> None:
    '''Clear terminal'''
    os.system('cls' if os.name == 'nt' else 'clear')


def show_png(image: ImageType) -> None:
    '''Mostra en un pop-up la imatge donada, fent
    servir la llibreria PIL. Si no es pot mostrar,
    ho notifica a la terminal.'''
    try:
        image.show()
    except Exception:
        print('Could not plot image. Check your library.')


def plot_billboard_menu() -> None:
    '''Mostra a la terminal el menú i les opcions de la Cartellera.'''
    options = '[cyan]1 - Plot full billboard\n' + \
         '2 - Cinemas \n' + \
         '3 - Films \n' + \
         '4 - Genres \n' + \
         '5 - Filter \n' + \
         '0 - Return'

    console.print(Panel(options, title="[magenta]Billboard options",
                        expand=False))
    return next_plot(shift=4, actual=1, options=[i for i in range(6)])


def plot_full_billboard() -> None:
    '''Mostra a la terminal la certellera completa.'''
    table = Table(title='BILLBOARD', border_style='blue3',
                  safe_box=False, box=box.ROUNDED)

    table.add_column("Film🎥", justify="center", style="cyan", no_wrap=True)
    table.add_column("Cinema🍿", justify='center', style="magenta")
    table.add_column("Time🕗", justify="center", style="green")
    table.add_column("Duration", justify="center", style="green")
    table.add_column("Language🔊", justify="center", style="green")

    for p in Bboard.projections:
        table.add_row(
            p.film.title,
            p.cinema.name,
            f'{p.start[0]}:{p.start[1]:02d}',
            f'{p.duration}',
            p.language)

    console.print(table)
    return next_plot(direct=1)


def plot_cinemas() -> None:
    '''Mostra a la terminal la llista de cinemes de la cartellera'''
    op: str = ''
    for c in Bboard.cinemas:
        op = op + c.name + '\n'
    console.print(
        Panel(op[:-1], title="[magenta]Cinemas", expand=False))
    return next_plot(direct=1)


def plot_films() -> None:
    '''Mostra a la terminal les películes de la cartellera.'''
    op: str = ''
    for f in Bboard.films:
        op = op + f.title + '\n'
    console.print(Panel(
        op[:-1], title="[magenta]Films", expand=False))
    return next_plot(direct=1)


def plot_genres() -> None:
    '''Mostra a la terminal la llista dels gèneres 
    de les películes de la Cartellera'''
    op: str = ''
    for g in Bboard.genres:
        op = op + g + '\n'
    console.print(Panel(
        op[:-1],
        title="[magenta]Genres",
        expand=False, safe_box=True))
    return next_plot(direct=1)


def plot_filter() -> None:
    '''Llegeix un filtre, l'aplica a la
     cartellera i la mostra.'''
    # op: str = ''
    '''for f in Bboard.poss_filters:
        op = op + f + '\n' --> ['cyan]{op[:-1]} '''

    console.print(Panel(  # plot filter types available
        '[cyan]' +
        'genre ------ genre = name_genre\n' +
        'director --- director = name_director\n' +
        'film ------- film = film_title\n' +
        'cinema ----- cinema = cinema_name\n' +
        'time ------- time = hh:mm - hh:mm\n' +
        'duration --- duration = duration_minutes\n' +
        'language --- language = V.O. / Spanish\n' +
        'city ------- city = Name_city',
        title="[magenta]Filter types---Specific format",
        expand=False))

    print(f'Format: filter_type = ___ ; filter_type = ___ ; ...')
    print('(Enter 0 to go back)')
    f: str = str(input('Enter filters: '))

    clear()
    if f == '0':  # go back
        return plot_billboard_menu()

    filters: dict[str, str] = {}
    try:
        for x in f.split(';'):
            k, v = x.split('=')
            k = k.strip()
            v = v.strip()
            filters[k] = v
    except Exception:
        console.print('[red]Wrong format!😓')
        return plot_filter()

    table = Table(title=f'BILLBOARD \n filters: {f}',
                  border_style='blue3',
                  safe_box=True, box=box.ROUNDED)

    table.add_column("Film🎥", justify="center", style="cyan")
    table.add_column("Cinema🍿", justify='center', style="magenta")
    table.add_column("Time🕗", justify="center", style="green")
    table.add_column("Duration", justify="center", style="green")
    table.add_column("Language🔊", justify="center", style="green")

    try:
        filtered_billboard = Bboard.filter(filters)
    except Exception:
        txt = "[red]Sorry, couldn't apply this filter😥💀. See filter options:"
        return next_plot(direct=9, text=txt)
    if len(filtered_billboard) == 0:
        txt = '[red]No movies found with this filter. See filter options:'
        return next_plot(direct=9, text=txt)
    for p in filtered_billboard:
        table.add_row(
            p.film.title,
            p.cinema.name,
            f'{p.start[0]}:{p.start[1]:02d}',
            f'{p.duration}',
            p.language)
    console.print(table)

    return next_plot(direct=9)


def plot_maps_menu() -> None:
    '''Mostra a la terminal el menú dels mapes.'''
    options = '[cyan]1 - Bus map\n' + \
              '2 - City map\n' + \
              '0 - Return'

    console.print(Panel(options, title="[magenta]Maps", expand=False))
    return next_plot(direct=2)


def plot_bus_map() -> None:
    '''Mostra en un pop-up el mapa dels busos.'''
    try:
        image = Image.open('bus_map.png')
    except Exception:
        loader.start()
        city.plot(Bus, 'bus_map.png')
        image = Image.open('bus_map.png')
        loader.stop()
    show_png(image)
    return next_plot(direct=3)


def plot_city_map():
    '''Mostra en un pop-up el mapa de la ciutat.'''
    try:
        image = Image.open('city_map.png')
    except Exception:
        loader.start()
        city.plot(City, 'city_map.png')
        image = Image.open('city_map.png')
        loader.stop()
    show_png(image)
    return next_plot(direct=3)


def plot_watch() -> None:
    options = '[cyan]Wanna watch a movie? Tell us \n' + \
                      "wich one and we'll guide you."

    console.print(Panel(options, title="[magenta]Watch movie", expand=False))
    print('(Enter 0 to Return)')
    movie = input('Enter movie: ')
    if movie == 0:
        return next_plot(direct=15)
    try:
        time = input('Enter your time disponibility:\n(Format: hh:mm-hh:mm)')
        FilteredBboard = Bboard.filter({'time': str(time),
                                        'city': 'Barcelona',
                                        'film': str(movie)})
    except Exception:
        text = ('[red]Wrong format!😓')
        return next_plot(direct=3, text=text)

    if FilteredBboard == []:
        text = ("Couldn't find this movie in Barcelona with\n" +
                "this time disponibility. Just watch [red]Netflix")
        return next_plot(direct=3, text=text)


def next_plot(shift: int = -1,
              actual: int = -1,
              direct: int = -1,
              options: list[int] = [],
              text: str = '') -> None:
    '''funció que retorna el plot corresponent a la crida. Shift és només
    per correspondre el nombre que entre l'usuari amb els "identificadors"
    de cada plot. actual és l'identificador de la funció que ha fet la crida.
    Options són els nombres que l'usuari pot donar. Si es dona un nombre per 
    la variable direct, es retorna directament a la funció corresponent
    al nombre de direct.'''
    if text != '':
        clear()
        console.print(text)
    if direct != -1:
        num = direct
    else:
        try:
            num = int(input('Enter option number: '))
            clear()  # clear terminal
        except ValueError:
            clear()
            console.print('[red]You must introduce a number!😡💀')
            return next_plot(0, actual)
        except Exception:
            clear()
            console.print('[red]Sorry, something went wrong!😭💀🤨')
            return next_plot(0, actual)
        if num not in options:
            clear()
            console.print("[red]This option doesen't exist!😡")
            return next_plot(0, actual)
        num += shift

    if num == 0:
        console.print(Panel(f'[green]See you soon!👋😘',
                      expand=False,
                      border_style='green3'))
    if num in [4, 10, 13]:
        return plot_main_menu()  # 'Return option'
    if num == 1:
        return plot_billboard_menu()
    if num == 2:
        return plot_maps_menu()
    if num == 3:
        return plot_watch()
    if num == 5:
        return plot_full_billboard()
    if num == 6:
        return plot_cinemas()
    if num == 7:
        return plot_films()
    if num == 8:
        return plot_genres()
    if num == 9:
        return plot_filter()
    if num == 11:
        return plot_bus_map()
    if num == 12:
        return plot_city_map()
    if num == 14:
        return plot_watch()
    if num == 15:
        return plot_main_menu()


def plot_main_menu() -> None:
    options = '[cyan]1 - Billboard\n' + \
                    '2 - Maps \n' + \
                    '3 - Watch \n' + \
                    '0 - Exit'

    console.print(Panel(options, title="[magenta]Options", expand=False))
    return next_plot(shift=0, actual=15, options=[i for i in range(4)])


def get_data() -> None:
    '''Descarrega les dades necessàries per
    executar el programa.'''
    Bboard = billboard.read()
    Bboard.genres = film_genres  # (generes amb emojis)
    Bus = city.get_buses_graph()
    try:
        Streets = city.load_osmnx_graph('osmnx_Bcn.pickle')
    except Exception:
        Streets = city.get_osmnx_graph()
        city.save_osmnx_graph(Streets, 'osmnx_Bcn.pickle')
    City = city.build_city_graph(Streets, Bus)


def init_program() -> None:
    '''Inicialitza el programa'''
    clear()
    loader.start()
    get_data()
    loader.stop()
    time.sleep(2)
    clear()
    plot_main_menu()


if __name__ == "__main__":
    clear()
    loader.start()
    Bboard = billboard.read()
    Bboard.genres = film_genres  # (generes amb emojis)
    Bus = city.get_buses_graph()
    try:
        Streets = city.load_osmnx_graph('osmnx_Bcn.pickle')
    except Exception:
        Streets = city.get_osmnx_graph()
        city.save_osmnx_graph(Streets, 'osmnx_Bcn.pickle')
    City = city.build_city_graph(Streets, Bus)
    loader.stop()
    time.sleep(2)
    clear()
    plot_main_menu()
