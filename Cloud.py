

from functools import reduce, partial

def compose(*funcs):
 

  return reduce(lambda a,e: lambda x: a(e(x)), funcs, lambda x: x)



base = int(input("Choose a base. (2 for normal 2048)\n> "))



def addn(board):

  from random import randrange, sample

  inds    = range(base**2)
  empties = [(y,x) for y in inds for x in inds if not board[y][x]]
  for y,x in sample(empties,2**(base-2)):
    board[y][x] = base if randrange(10) else base**2
  return board



from itertools import count, groupby, starmap

def squish(row):

  r = []
  for n,x in starmap(lambda n, a: (n, sum(map(bool,a))),
                     groupby(filter(bool, row))):
    r += ([n*base] * (x//base)) + ([n] * (x%base))
  return r + ([None] * (base**2 - len(r)))


def transpose(l): return [list(x) for x in zip(*l)]



flip = partial(map, reversed)



thunk = compose(list, partial(map, list))


moveLeft  = compose(thunk, partial(map, squish), thunk)
moveRight = compose(thunk, flip, moveLeft, flip)
moveUp    = compose(transpose, moveLeft, transpose)
moveDown  = compose(transpose, moveRight, transpose)


try:
    import curses

    screen = curses.initscr()
    curses.noecho()           
    curses.cbreak()           
    screen.keypad(True)
    curses.curs_set(False)    



    moves = {curses.KEY_RIGHT: moveRight,
            curses.KEY_LEFT : moveLeft ,
            curses.KEY_UP   : moveUp   ,
            curses.KEY_DOWN : moveDown }


    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, -1) 

    def colorfac():

        for i,c in zip(count(2),(c for c in count(1) if c!=curses.COLOR_BLACK)):
            curses.init_pair(i, c, -1)
            yield curses.color_pair(i)

    colorgen = colorfac()

    from collections import defaultdict


    colors = defaultdict(lambda: next(colorgen))



    size = max(11 - base*2, 3) 

    def printBoard(board):

        def line(b,c): return b + b.join([c*(size)]*len(board)) + b
        border, gap = line("+","-"), line("|"," ")
        pad = "\n" + "\n".join([gap]*((size-2)//4)) if size > 5 else ""
        screen.addstr(0, 0, border, curses.color_pair(1))
        for row in board:
            screen.addstr(pad + "\n|", curses.color_pair(1))
            for e in row:
                if e: screen.addstr(str(e).center(size), colors[e])
                else: screen.addstr(" " * size)
                screen.addstr("|", curses.color_pair(1))
            screen.addstr(pad + "\n" + border, curses.color_pair(1))
    board = addn([[None for _ in range(base**2)] for _ in range(base**2)])
    printBoard(board)



    for char in filter(moves.__contains__, iter(screen.getch, ord("q"))):
        moved = moves[char](board)
        if sum(not n for r in moved for n in r) < 2**(base-2): break
        if moved != board: board = addn(moved)
        printBoard(board)

finally:
    curses.nocbreak()     
    screen.keypad(0)      
    curses.echo()       
    curses.curs_set(True) 
    curses.endwin() 
          
