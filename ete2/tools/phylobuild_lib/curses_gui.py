import curses
import time
from collections import deque


class CursesList():
    def __init__(self, win):
        self._win = win
        self.h, self.w = win.getmaxyx()
        self._items = deque()
        self._top = 0

    def scroll(self, n):
        pos = self._top + n
        if pos < 0:
            pos = 0
        elif pos >= len(self._items):
            pos = len(self._items) - 1

        if self._top != pos:
            self._top = pos
            self.refresh()

    def goto(self, n):
        if n >= 0 and n < len(self._items):
            self._top = pos
            self.refresh()

    def goto_end(self):
        self._top = len(self._items)-1
        self.refresh()

    def goto_start(self):
        self._top = 0
        self.refresh()

    def refresh(self):
        self._win.clear()
        start_pos = self._top
        ln = 0
        while ln < self.h and len(self._items) > ln + start_pos:
            self._win.addstr(ln, 0, self._items[ln + start_pos])
            ln += 1
        self._win.refresh()
        
    def add_item(self, txt):
        self._items.append(txt)

def main(scr):    
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_RED, curses.COLOR_WHITE)

    dbg_h = 40
    WIN = {}
    WIN[0] = scr
    h, w = WIN[0].getmaxyx()
    WIN[1] = curses.newwin(h-2, w/2, 1,1)
    WIN[2] = curses.newwin(h-dbg_h, (w/2)-1, 1, (w/2)+2)
    WIN[3] = curses.newwin(dbg_h, (w/2)-1, h-dbg_h-1, (w/2)-2)




    p = curses.newpad(1000, 1000)
    p.addstr("HOLA\n")
    p.addstr("AMIGO\n")
    p.addstr("DE VIGO")
    p.refresh(0, 0, 5, 30, 5, 35)
    key = p.getch()
    return 

    
 
    for w in WIN.values():
        w.keypad(1)
        w.idlok(True)
        w.scrollok(True)
    p.refresh(0, 0, 10, 10, 20, 20)
    return 



    C = CursesList(WIN[2])
    for line in open("/var/log/Xorg.0.log"):
        C.add_item(line.strip())
    C.refresh()
    #WIN[1].addstr("(%d)" %len(C._items))
    while 1:
        key = WIN[2].getch()
        WIN[1].addstr("%s (%d)" %(key, C._top))
        WIN[1].refresh()
        if key == 113: 
            break
        elif key == curses.KEY_UP:
            C.scroll(-1)
        elif key == curses.KEY_DOWN:
            C.scroll(1)
        elif key == curses.KEY_NPAGE:
            C.scroll(10)
        elif key == curses.KEY_PPAGE:
            C.scroll(-10)
        elif key == curses.KEY_END:
            C.goto_end()
        elif key == curses.KEY_HOME:
            C.goto_start()
        else:
            C.refresh()

curses.wrapper(main)
