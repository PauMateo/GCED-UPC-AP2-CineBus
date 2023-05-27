#  import city
import billboard
import os
import rich.table as rtab
import rich.console as rcons
import rich.panel as rpan
from rich import box


def clear() -> None:
    '''Clear terminal'''
    os.system('cls' if os.name == 'nt' else 'clear')  # clear terminal


def plot_billboard() -> None:
    table = rtab.Table(title='BILLBOARD', border_style='blue3',
                       safe_box=False, box=box.ROUNDED)
    console = rcons.Console()

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
    main()


def plot_options() -> None:
    op = '[cyan]1 - Plot Billboard\n' + \
         '2 - Info & filter\n' + \
         '3 - Exit'

    console = rcons.Console()
    console.print(rpan.Panel(op, title="[magenta]Options", expand=False))


def plot_filter_options() -> None:

    console = rcons.Console()
    console.print(
        rpan.Panel('[red]' +
                   '1 - Enter filter\n' +
                   '2 - See genres \n' +
                   '3 - See films\n' +
                   '4 - See cinemas\n' +
                   '5 - Return',
                   title="[magenta]Filter options",
                   expand=False,
                   border_style='blue3'))

    try:
        num = int(input('Enter option: '))
    except ValueError:
        clear()
        console.print('[red] You must introduce a number!😡💀')
        return plot_filter_options()

    clear()
    if num == 1:
        return plot_filter_billboard()

    elif num == 2:
        op: str = ''
        for g in Bboard.genres:
            op = op + g + '\n'
        console.print(rpan.Panel(
            op[:-1],
            title="[magenta]Genres",
            expand=False, safe_box=True))
        return plot_filter_options()

    elif num == 3:
        op: str = ''
        for f in Bboard.films:
            op = op + f.title + '\n'
        console.print(rpan.Panel(
            op[:-1], title="[magenta]Films", expand=False))
        return plot_filter_options()

    elif num == 4:
        op: str = ''
        for c in Bboard.cinemas:
            op = op + c.name + '\n'
        console.print(
            rpan.Panel(op[:-1], title="[magenta]Cinemas", expand=False))
        return plot_filter_options()

    elif num == 5:
        return main()
    else:
        clear()
        console.print("[red]This option doesen't exist!😡")
        return plot_filter_options()


def plot_filter_billboard() -> None:
    '''Llegeix un filtre, l'aplica a la
     cartellera i la mostra.'''
    console = rcons.Console()
    # op: str = ''
    '''for f in Bboard.poss_filters:
        op = op + f + '\n' --> ['cyan]{op[:-1]} '''

    console.print(rpan.Panel(  # plot filter types available
        '[cyan]' +
        'genre ------ genre = name_genre\n\n' +
        'director --- director = name_director\n' +
        'film ------- film = film_title\n' +
        'cinema ----- cinema = cinema_name\n' +
        'time ------- time = hh:mm - hh:mm\n' +
        'duration --- duration = duration_minutes\n' +
        'language --- language = V.O. / Spanish',
        title="[magenta]Filter types---Specific format",
        expand=False))

    print(f'Format: filter_type = ___ ; filter_type = ___ ; ...')
    print('(Enter 0 to go back)')
    f: str = str(input('Enter filters: '))

    clear()
    if f == '0':  # go back
        return plot_filter_options()

    filters: dict[str, str] = {}
    try:
        for x in f.split(';'):
            k, v = x.split('=')
            k = k.strip()
            v = v.strip()
            filters[k] = v
    except Exception:
        console.print('[red]Wrong format!😓')
        return plot_filter_billboard()

    table = rtab.Table(title=f'BILLBOARD \n filters: {f}',
                       border_style='blue3',
                       safe_box=True, box=box.ROUNDED)
    console = rcons.Console()

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
        return plot_filter_billboard()
    if len(filtered_billboard) == 0:
        console.print(
            '[red]No movies found with this filter. See filter options:')
        return plot_filter_billboard()
    for p in filtered_billboard:
        table.add_row(
            p.film.title,
            p.cinema.name,
            f'{p.start[0]}:{p.start[1]:02d}',
            f'{p.duration}',
            p.language)
    console.print(table)

    main()


def next_plot(num: int) -> None:
    console = rcons.Console()
    if num == 1:
        plot_billboard()
    elif num == 2:
        plot_filter_options()
    elif num == 3:
        console = rcons.Console()
        console.print(rpan.Panel(f'[green]See you soon!👋😘',
                                 expand=False,
                                 border_style='green3'))
        return None
    else:
        clear()
        console.print("[red]This option doesen't exist!😡")
        return main()


def main():
    plot_options()

    try:
        num = int(input('Enter option number: '))
        clear()  # clear terminal
        next_plot(num)
    except ValueError:
        clear()
        print('You must introduce a number!😡💀')
        main()
    except Exception:
        clear()
        print('Sorry, something went wrong!😭💀🤨')
        main()


genres = {"Romántico \U0001F339 \U0001F496",
          "Western \U0001F920 \U0001F335 \U0001F40E",
          "Biografía \U0001F4DC",
          "Drama \U0001F494",
          "Comedia dramática \U0001F604 \U0001F62D",
          "Histórico \U0001F3FA \U0001F30F",
          "Crimen \U0001F52A \U0001FA78 \U0001F480",
          "Guerra \U0001F9E8",
          "Suspense \U0001F575",
          "Documental \U0001F418 \U0001F992",
          "Aventura \U0001F30D \U0001F920",
          "Ciencia ficción \U0001F680 \U0001F9EC",
          "Terror \U0001F47B \U0001F62C",
          "Erótico \U0001F525 \U0001F60F",
          "Acción \U0001F4A5",
          "Familia \U0001F46A",
          "Fantasía \U0001F9D9 \U0001F3F0",
          "Comedia \U0001F3AD \U0001F604",
          "Judicial \U00002696 \U0001F3DB",
          "Animación \U0000270F"}

if __name__ == "__main__":
    Bboard: billboard.Billboard = billboard.read()
    Bboard.genres = genres
    clear()
    main()
