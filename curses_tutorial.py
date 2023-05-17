import curses
from curses import wrapper


def main(stdscr):
    # Initialize color pair
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    current_row = 0
    menu = ['912', '914', '915']

    while True:
        print_menu(stdscr, current_row, menu)
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1

        elif key == curses.KEY_DOWN and current_row < len(menu) - 1:
            current_row += 1

        elif key == curses.KEY_ENTER or key in [10, 13]:
            stdscr.addstr(0, 0, "You selected '{}'".format(menu[current_row]))
            stdscr.refresh()
            stdscr.getch()

        stdscr.clear()


def print_menu(stdscr, selected_row_idx, menu):
    stdscr.addstr(0, 0, "Choose an option: ")
    for idx, row in enumerate(menu):
        x = 0
        y = idx
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y + 1, x, "> " + row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y + 1, x, "  " + row)

    stdscr.refresh()

# import curses

# classes = ["The sneaky thief", "The smarty wizard", "The proletariat"]


# def character(stdscr):
#     attributes = {}
#     curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
#     attributes['normal'] = curses.color_pair(1)

#     curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
#     attributes['highlighted'] = curses.color_pair(2)

#     c = 0  # last character read
#     option = 0  # the current option that is marked
#     while c != 10:  # Enter in ascii
#         stdscr.erase()
#         stdscr.addstr("What is your class?\n", curses.A_UNDERLINE)
#         for i in range(len(classes)):
#             if i == option:
#                 attr = attributes['highlighted']
#             else:
#                 attr = attributes['normal']
#             stdscr.addstr("{0}. ".format(i + 1))
#             stdscr.addstr(classes[i] + '\n', attr)
#         c = stdscr.getch()
#         if c == curses.KEY_UP and option > 0:
#             option -= 1
#         elif c == curses.KEY_DOWN and option < len(classes) - 1:
#             option += 1

#     stdscr.addstr("You chose {0}".format(classes[option]))
#     stdscr.getch()

# curses.wrapper(character)
