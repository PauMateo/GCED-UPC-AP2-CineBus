#  import city
import billboard
import os
import rich.table as rtab
import rich.console as rcons
import rich.panel as rpan
from rich import box


Bboard: billboard.Billboard = billboard.read()


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
         '2 - Filter\n' + \
         '3 - Exit'

    console = rcons.Console()
    console.print(rpan.Panel(op, title="[magenta]Options", expand=False))


def plot_filter_options() -> None:

    console = rcons.Console()
    console.print(
        rpan.Panel('[cyan]1 - Enter filter \n2 - See genres \n' +
                   '3 - See films\n4 - See cinemas\n5 - Return',
                   title="[magenta]Filter options", expand=False))

    try:
        num = int(input('Enter option: '))
    except ValueError:
        clear()
        print('You must introduce a number!😡💀')
        return plot_filter_options()

    clear()
    if num == 1:
        return plot_filter_billboard()

    elif num == 2:
        op: str = ''
        for g in Bboard.genres:
            op = op + g + '\n'
        console = rcons.Console()
        console.print(
            rpan.Panel(op[:-1], title="[magenta]Genres", expand=False))
        return plot_filter_options()

    elif num == 3:
        op: str = ''
        for f in Bboard.films:
            op = op + f.title + '\n'
        console = rcons.Console()
        console.print(rpan.Panel(
            op[:-1], title="[magenta]Films", expand=False))
        return plot_filter_options()

    elif num == 4:
        op: str = ''
        for c in Bboard.cinemas:
            op = op + c.name + '\n'
        console = rcons.Console()
        console.print(
            rpan.Panel(op[:-1], title="[magenta]Cinemas", expand=False))
        return plot_filter_options()

    elif num == 5:
        return main()
    else:
        clear()
        print("This option doesen't exist!😡")
        return plot_filter_options()


def plot_filter_billboard() -> None:
    '''Llegeix un filtre, l'aplica a la
     cartellera i la mostra.'''
    console = rcons.Console()
    op: str = ''
    for f in Bboard.poss_filters:
        op = op + f + '\n'
    console.print(rpan.Panel(  # plot filter types available
        f'[cyan]{op[:-1]}',
        title="[magenta]Filter types",
        expand=False))

    print(f'Format: filter_type = ___ ; filter_type = ___ ; ...')
    print('(Enter 0 to go back)')
    f: str = str(input('Enter filters: '))

    clear()
    if f == '0':  # go back
        return main()

    filters: dict[str, str] = {}
    try:
        for x in f.split(';'):
            k, v = x.split('=')
            k = k.strip()
            v = v.strip()
            filters[k] = v
    except Exception:
        print('Wrong format!😓')
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
        print("Sorry, couldn't apply this filter😥💀. See filter options: ")
        return main()
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
    if num == 1:
        plot_billboard()
    elif num == 2:
        plot_filter_options()
    elif num == 3:
        console = rcons.Console()
        console.print(rpan.Panel(f'See you soon!👋😘', expand=False))
        return None
    else:
        clear()
        print("This option doesen't exist!😡")
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


if __name__ == "__main__":
    clear()
    main()
