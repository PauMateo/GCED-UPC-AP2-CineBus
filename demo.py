import os

import billboard as bboard
import rich.console
import city

from rich.table import Table
from rich.panel import Panel
from rich import box
from loaders import TextLoader
from constants import film_genres
from PIL.Image import Image as ImageType
from PIL import Image as Image
from dataclasses import dataclass


console = rich.console.Console()
loader = TextLoader(colour='yellow', text='Loading', speed=.2,
                    animation='loop', complete_text='')


@dataclass
class Demo:
    '''
    A small menu system that offers an interface
    with the following functionalities:
        - View the billboard, cinemas, movies, and genres.
        - Search and filtering methods for the billboard.
        - View maps of bus lines and the city.
        - Show the way to go and see a desired movie from a given
          location at a given time.
        - Brief information about the authors of the project.
    '''

    Bus: city.BusesGraph
    Streets: city.OsmnxGraph
    City: city.CityGraph
    Bboard: bboard.Billboard

    def __init__(self) -> None:
        """Constructor of the class. Initializes the menu system."""
        return self.init_demo()

    def clear(self) -> None:
        """Clears the terminal window."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_png(self, image: ImageType) -> None:
        """
        Display the given image in a pop-up, using the PIL library.
        If it cannot be displayed, notify it in the execution terminal.
        """
        try:
            image.show()
        except Exception:
            print('Could not plot image. Check your library, ' +
                  'it should be downloaded.')

    def plot_billboard_menu(self) -> None:
        """Display the menu and options of the Billboard in the terminal."""

        options = '[cyan]1 - Plot full billboard\n' + \
                  '2 - Cinemas \n' + \
                  '3 - Films \n' + \
                  '4 - Genres \n' + \
                  '5 - Filter \n' + \
                  '0 - Return'

        console.print(Panel(options, title="[magenta]Billboard options",
                            expand=False))
        return self.next_plot(shift=5, actual=1, options=[i for i in range(6)])

    def plot_full_billboard(self) -> None:
        """Display the complete billboard in the terminal."""
        table = Table(title='BILLBOARD', border_style='blue3',
                      safe_box=False, box=box.ROUNDED)

        table.add_column("Film🎥", justify="center", style="cyan", no_wrap=True)
        table.add_column("Cinema🍿", justify='center', style="magenta")
        table.add_column("Time🕗", justify="center", style="green")
        table.add_column("Duration", justify="center", style="green")
        table.add_column("Language🔊", justify="center", style="green")

        for p in self.Bboard.projections:
            table.add_row(
                p.film.title,
                p.cinema.name,
                f'{p.start[0]}:{p.start[1]:02d}',
                f'{p.duration}',
                p.language)

        console.print(table)
        return self.next_plot(direct=1)

    def plot_cinemas(self) -> None:
        """Display the list of cinemas from the billboard in the terminal."""
        op: str = ''
        for c in self.Bboard.cinemas:
            op = op + c.name + '\n'
        console.print(
            Panel(op[:-1], title="[magenta]Cinemas", expand=False))
        return self.next_plot(direct=1)

    def plot_films(self) -> None:
        """Display the movies from the billboard in the terminal."""
        op: str = ''
        for f in self.Bboard.films:
            op = op + f.title + '\n'
        console.print(Panel(
            op[:-1], title="[magenta]Films", expand=False))
        return self.next_plot(direct=1)

    def plot_genres(self) -> None:
        """
        Display the list of genres of the movies
        in the Billboard in the terminal.
        """
        op: str = ''
        for g in self.Bboard.genres:
            op = op + g + '\n'
        console.print(Panel(
            op[:-1],
            title="[magenta]Genres",
            expand=False, safe_box=True))
        return self.next_plot(direct=1)

    def plot_filter(self) -> None:
        """
        Reads a filter, applies it to the billboard,
        and displays the filtered results in the terminal.
        """

        console.print(Panel(  # plot filter types available
            '[cyan]' +
            'genre ------ genre = name_genre\n' +
            'director --- director = name_director\n' +
            'film ------- film = film_title\n' +
            'cinema ----- cinema = cinema_name\n' +
            'time ------- time = hh:mm - hh:mm\n' +
            '               (min_start - max_end)\n' +
            'duration --- duration = duration_minutes\n' +
            '                        (max_duration)\n' +
            'language --- language = V.O. / Spanish\n' +
            'city ------- city = city_Name',
            title="[magenta]Filter types---Specific format",
            expand=False))

        print(f'Format: filter_type = ___ ; filter_type = ___ ; ...')
        print('(Enter 0 to go back)')
        f: str = str(input('Enter filters: '))

        self.clear()
        if f == '0':  # go back
            return self.next_plot(direct=1)

        filters: dict[str, str] = {}
        try:
            for x in f.split(';'):
                k, v = x.split('=')
                k = k.strip()
                v = v.strip()
                filters[k] = v
        except Exception:
            text = '[red]Wrong format!😓\n'
            return self.next_plot(direct=10, text=text)

        table = Table(title=f'BILLBOARD \n filters: {f}',
                      border_style='blue3',
                      safe_box=True, box=box.ROUNDED)

        table.add_column("Film🎥", justify="center", style="cyan")
        table.add_column("Cinema🍿", justify='center', style="magenta")
        table.add_column("Time🕗", justify="center", style="green")
        table.add_column("Duration", justify="center", style="green")
        table.add_column("Language🔊", justify="center", style="green")

        try:
            filtered_billboard = self.Bboard.filter(filters)
        except Exception:
            txt = "[red]Sorry, couldn't apply this filter😥💀. \n"
            return self.next_plot(direct=10, text=txt)
        if len(filtered_billboard) == 0:
            txt = '[red]No movies found with this filter. \n'
            return self.next_plot(direct=10, text=txt)
        for p in filtered_billboard:
            table.add_row(
                p.film.title,
                p.cinema.name,
                f'{p.start[0]}:{p.start[1]:02d}',
                f'{p.duration}',
                p.language)
        console.print(table)

        return self.next_plot(direct=10)

    def plot_maps_menu(self) -> None:
        """Displays the menu of maps in the terminal."""
        options = '[cyan]1 - Bus map\n' + \
                  '2 - City map\n' + \
                  '0 - Return'

        console.print(Panel(options, title="[magenta]Maps", expand=False))
        return self.next_plot(shift=11, actual=2, options=[0, 1, 2])

    def plot_bus_map(self) -> None:
        """Displays the bus map in a pop-up."""
        loader.start()
        try:
            image = Image.open('bus_map.png')
        except Exception:
            city.plot_buses(self.Bus, 'bus_map.png')
            image = Image.open('bus_map.png')
        self.show_png(image)
        loader.stop()

        return self.next_plot(direct=2)

    def plot_city_map(self):
        """Displays the city map in a pop-up."""
        loader.start()
        try:
            image = Image.open('city_map.png')
        except Exception:
            city.plot_city(self.City, 'city_map.png')
            image = Image.open('city_map.png')
        self.show_png(image)
        loader.stop()

        return self.next_plot(direct=2)

    def plot_watch(self) -> None:
        """
        By a given movie from the user, plots the shortest path to the
        nearest cinema where that movie is played and gives the indications.
        """
        options = '[cyan]Wanna watch a movie? Tell us \n' + \
            "wich one and we'll guide you."

        console.print(Panel(options,
                            title="[magenta]Watch movie", expand=False))
        print('(Enter 0 to Return)')
        movie = input('Enter movie: ').strip()

        if movie == '0':  # Return
            self.clear()
            return self.next_plot(direct=14)
        if movie not in [f.title for f in self.Bboard.films]:
            text = ("[red]We can't find this movie!😓\n" +
                    "Check the available movies at the billboard.")
            return self.next_plot(direct=3, text=text)
        try:
            time = input('Enter your time disponibility\n' +
                         '(Format: hh:mm-hh:mm): ')
            start_time = time.split('-')[0]
            FilteredBboard = self.Bboard.filter({'time': time,
                                                 'city': 'Barcelona',
                                                 'film': movie})
            coords = input('Enter your position coordinates\n' +
                           '(format: lat, long): ')
            x_, y_ = coords.split(',')
            x, y = float(x_.strip()), float(y_.strip())

        except Exception:
            text = ('[red]Wrong format!😓\n')
            return self.next_plot(direct=3, text=text)

        if FilteredBboard == []:
            text = "Couldn't find any reachable session of this movie " + \
                "with your disponibility.\nJust watch [red]Netflix: " + \
                "[white]https://www.netflix.com/es/ \n"
            return self.next_plot(direct=3, text=text)

        try:
            loader.start()
            result = self.find_first_movie_path(FilteredBboard,
                                                start_time, (x, y))
            loader.stop()
        except AssertionError:
            loader.stop()
            text = "It appears you are not in Barcelona. For now, " + \
                "our program only works in Barcelona, sorry!"
            return self.next_plot(direct=3, text=text)

        if result is None:
            text = "Couldn't find any reachable session of this movie" + \
                " with your disponibility.\nJust watch [red]Netflix: " + \
                "https://www.netflix.com/es/ \n"
            return self.next_plot(direct=3, text=text)

        path, projection = result

        return self.plot_found_proj(path, projection)

    def plot_found_proj(self, path: city.Path,
                        proj: bboard.Projection) -> None:
        """
        Displays the results obtained from the search for the
        movie requested by the user in the function plot_watch().
        """
        options = f'[cyan]{proj.film.title} --- {proj.cinema.name} --- ' + \
                  f'start {proj.start[0]:02d}:{proj.start[1]:02d} --- ' + \
                  f'duration {proj.duration} m'
        loader.start()
        path.get_other_data()
        loader.stop()

        indic = path.path_indications
        if indic != '':
            options += f'\n\n   [green]INDICATIONS:\n[white]{indic}\n' + \
                       f'   [green]Estimated travel time: {path.time} minutes'
        else:
            options += f'Could not substract indications from path.'

        console.print(Panel(options, title="[magenta]Movie found!",
                            expand=False))

        if indic != '':
            console.print('Check the path image;\n' +
                          '  red line --- walking\n' +
                          '  blue line --- bus\n' +
                          '  black dot --- bus stop (during bus ride)\n'
                          '  orange dot --- take / transfer bus line\n' +
                          "  pointer / green dot --- cinema's location\n" +
                          "  magenta dot --- your start location")

        loader.start()
        city.plot_path(path, 'path.png')
        image = Image.open('path.png')
        self.show_png(image)
        loader.stop()

        return self.next_plot(direct=16)

    def find_first_movie_path(
            self,
            FilteredBboard: list[bboard.Projection],
            time_: str,
            coords: city.Coord) -> tuple[city.Path, bboard.Projection] | None:
        """
        Given the filtered list of screenings, search for the first screening
        that can be reached from the specified position
        and the given initial time. Returns the path to reach that screening.
        """
        self.clear()
        h, m = time_.split(':')
        time = int(h) * 60 + int(m)  # time in minutes

        proj: bboard.Projection
        for proj in FilteredBboard:
            movie_coords: city.Coord = proj.cinema.coord
            h, m = proj.start
            movie_start = int(h) * 60 + int(m)  # time in minutes
            path: city.Path = city.find_path(self.Streets, self.City,
                                             coords, movie_coords)

            if time + path.time <= movie_start:
                return path, proj

        return None  # if could't find any path :'(

    def plot_about_us(self) -> None:
        """
        Displays a small tab with information
        about the authors of the project.
        """

        text = ('[cyan]AUTHORS: [magenta2]Pau·(Mateo ∧ Fernández)\n' +
                '[cyan]First year students of Data science and engineering\n' +
                'at UPC - Barcelona\n' +
                'Contact us: pau.mateo.bernado@estudiantat.upc.edu\n' +
                '            pau.fernandez.cester@estudiantat.upc.edu')

        console.print(Panel(text, title="[magenta]About Us", expand=False))
        return self.next_plot(direct=16)

    def plot_main_menu(self) -> None:
        options = ('[cyan]1 - Billboard\n' +
                   '2 - Maps \n' +
                   '3 - Watch \n' +
                   '4 - About us\n' +
                   '0 - Exit')

        console.print(Panel(options, title="[magenta]Options", expand=False))
        return self.next_plot(shift=0, actual=16,
                              options=[i for i in range(5)])

    def next_plot(self,
                  shift: int = -1,
                  actual: int = -1,
                  direct: int = -1,
                  options: list[int] = [],
                  text: str = '') -> None:
        """
        The function returns the corresponding plot based on the call.
        'Shift' is only used to match the number entered by the user
        with the 'identifiers' of each plot.
        'Actual' is the identifier of the function that made the call.
        'Options' are the numbers that the user can provide.
        If a number is given for the 'direct' variable,
        the corresponding function is returned directly.
        """

        if text != '':
            self.clear()
            console.print(text)
        if direct != -1:
            num = direct
        else:
            try:
                num = int(input('Enter option number: '))
                self.clear()  # clear terminal
            except ValueError:
                self.clear()
                console.print('[red]You must introduce a number!😡💀\n')
                return self.next_plot(direct=actual)
            except Exception:
                self.clear()
                console.print('[red]Sorry, something went wrong!😭💀🤨\n')
                return self.next_plot(direct=actual)

            if num not in options:
                self.clear()
                console.print("[red]This option doesen't exist!😡\n")
                return self.next_plot(direct=actual)
            num += shift  # trobar l'identificador corresponent

        if num == 0:
            console.print(Panel(f'[green]See you soon!👋😘',
                          expand=False,
                          border_style='green3'))

        if num in [5, 11, 14, 15]:
            return self.plot_main_menu()  # 'Return options'
        if num == 1:
            return self.plot_billboard_menu()
        if num == 2:
            return self.plot_maps_menu()
        if num == 3:
            return self.plot_watch()
        if num == 4:
            return self.plot_about_us()
        if num == 6:
            return self.plot_full_billboard()
        if num == 7:
            return self.plot_cinemas()
        if num == 8:
            return self.plot_films()
        if num == 9:
            return self.plot_genres()
        if num == 10:
            return self.plot_filter()
        if num == 12:
            return self.plot_bus_map()
        if num == 13:
            return self.plot_city_map()
        if num == 16:
            return self.plot_main_menu()

    def get_data(self) -> tuple[bboard.Billboard, city.BusesGraph,
                                city.OsmnxGraph, city.CityGraph]:
        """Downloads the necessary data to run the program."""
        self.Bboard = bboard.read()
        self.Bboard.genres = film_genres  # (generes amb emojis)
        self.Bus = city.get_buses_graph()
        try:
            self.Streets = city.load_osmnx_graph('osmnx_Bcn.pickle')
        except Exception:
            try:
                self.Streets = city.get_osmnx_graph()
            except Exception:
                loader.stop()
                console.print('[red]Could not get data from OpenStreepMap.')
                exit(1)
            try:
                city.save_osmnx_graph(self.Streets, 'osmnx_Bcn.pickle')
            except Exception:
                self.clear()
                console.print('[red]Could not save Osmnx graph.')
        try:
            self.City: city.CityGraph = city.build_city_graph(self.Streets,
                                                              self.Bus)
            return self.Bboard, self.Bus, self.Streets, self.City
        except Exception:
            console.print('[red]Sorry, something went wrong!😭💀🤨')
            exit(1)

    def init_demo(self) -> None:
        self.clear()
        loader.start()
        self.get_data()
        loader.stop()
        self.clear()
        self.plot_main_menu()


if __name__ == "__main__":
    Demo()
