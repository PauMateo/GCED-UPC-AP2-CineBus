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
from PIL import Image

'''console = rich.console.Console()
Bus: city.BusesGraph
Streets: city.OsmnxGraph
City: city.CityGraph
Bboard: billboard.Billboard'''

loader = TextLoader(colour='yellow',
                    text='Loading',
                    animation='loop')
console = rich.console.Console()
Bus: city.BusesGraph
Streets: city.OsmnxGraph
City: city.CityGraph
Bboard: billboard.Billboard


def clear() -> None:
    '''Clear terminal'''
    os.system('cls' if os.name == 'nt' else 'clear')  # clear terminal


def plot_billboard_menu() -> None:
    options = '[cyan]1 - Plot full billboard\n' + \
         '2 - Cinemas \n' + \
         '3 - Films \n' + \
         '4 - Genres \n' + \
         '5 - Filter \n' + \
         '0 - Return'

    console.print(Panel(options, title="[magenta]Billboard options",
                        expand=False))
    return next_plot(4, actual=1, options=[i for i in range(6)])


def plot_full_billboard() -> None:
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
    return plot_billboard_menu()


def plot_cinemas() -> None:
    op: str = ''
    for c in Bboard.cinemas:
        op = op + c.name + '\n'
    console.print(
        Panel(op[:-1], title="[magenta]Cinemas", expand=False))
    return plot_billboard_menu()


def plot_films() -> None:
    op: str = ''
    for f in Bboard.films:
        op = op + f.title + '\n'
    console.print(Panel(
        op[:-1], title="[magenta]Films", expand=False))
    return plot_billboard_menu()


def plot_genres() -> None:
    op: str = ''
    for g in Bboard.genres:
        op = op + g + '\n'
    console.print(Panel(
        op[:-1],
        title="[magenta]Genres",
        expand=False, safe_box=True))
    return plot_billboard_menu()


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
        console.print(
            "[red]Sorry, couldn't apply this filter😥💀. See filter options:")
        return plot_filter()
    if len(filtered_billboard) == 0:
        console.print(
            '[red]No movies found with this filter. See filter options:')
        return plot_filter()
    for p in filtered_billboard:
        table.add_row(
            p.film.title,
            p.cinema.name,
            f'{p.start[0]}:{p.start[1]:02d}',
            f'{p.duration}',
            p.language)
    console.print(table)


def plot_maps_menu() -> None:
    options = '[cyan]1 - Bus map\n' + \
                    '2 - City map\n' + \
                    '0 - Return'

    console.print(Panel(options, title="[magenta]Maps", expand=False))
    return next_plot(10, 2, [0, 1, 2])


def plot_bus_map() -> None:
    try:
        image = Image.open('bus_map.png')
    except Exception:
        loader.start()
        city.plot(Bus, 'bus_map.png')
        image = Image.open('bus_map.png')
        loader.stop()
    image.show()

    return plot_maps_menu()


def plot_city_map():
    try:
        raise Exception
        image = Image.open('city_map.png')
    except Exception:
        loader.start()
        city.plot(City, 'city_map.png')
        image = Image.open('city_map.png')
        loader.stop()
    image.show()
    return plot_maps_menu()


def plot_watch() -> None:
    ...


def next_plot(shift: int,
              actual: int = -1,
              options: list[int] = []) -> None:
    '''funció que retorna el plot corresponent a la crida. Shift és només
    per correspondre el nombre que entre l'usuari amb els "identificadors"
    de cada plot. Actual és l'identificador de la funció que ha fet la crida.
    Options són els nombres que l'usuari pot donar. '''

    if len(options) == 0:
        num = actual
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
    return next_plot(0, 15, [i for i in range(4)])


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
