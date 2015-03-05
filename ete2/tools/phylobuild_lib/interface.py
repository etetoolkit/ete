# #START_LICENSE###########################################################
#
#
# This file is part of the Environment for Tree Exploration program
# (ETE).  http://etetoolkit.org
#  
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#  
# ETE is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# 
#                     ABOUT THE ETE PACKAGE
#                     =====================
# 
# ETE is distributed under the GPL copyleft license (2008-2015).  
#
# If you make use of ETE in published work, please cite:
#
# Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon.
# ETE: a python Environment for Tree Exploration. Jaime BMC
# Bioinformatics 2010,:24doi:10.1186/1471-2105-11-24
#
# Note that extra references to the specific methods implemented in 
# the toolkit may be available in the documentation. 
# 
# More info at http://etetoolkit.org. Contact: huerta@embl.de
#
# 
# #END_LICENSE#############################################################
import sys
import os
import re
import time
from StringIO import StringIO
from signal import signal, SIGWINCH, SIGKILL, SIGTERM
from collections import deque
from textwrap import TextWrapper

import Queue
import threading

from ete2.tools.phylobuild_lib.logger import get_main_log
from ete2.tools.phylobuild_lib.utils import GLOBALS, clear_tempdir, terminate_job_launcher, pjoin, pexist
from ete2.tools.phylobuild_lib.errors import *

try:
    import curses
except ImportError: 
    NCURSES = False
else:
    NCURSES = True
    
# CONVERT shell colors to the same curses palette
SHELL_COLORS = {
    "10": '\033[1;37;41m', # white on red
    "11": '\033[1;37;43m', # white on orange
    "12": '\033[1;37;45m', # white on magenta
    "16": '\033[1;37;46m', # white on blue
    "13": '\033[1;37;40m', # black on white
    "06": '\033[1;34m', # light blue
    "05": '\033[1;31m', # light red
    "03": '\033[1;32m', # light green
    "8": '\033[1;33m', # yellow
    "7": '\033[36m', # cyan
    "6": '\033[34m', # blue
    "3": '\033[32m', # green
    "4": '\033[33m', # orange
    "5": '\033[31m', # red
    "2": "\033[35m", # magenta
    "1": "\033[0m", # white
    "0": "\033[0m", # end
}
    
def safe_int(x):
    try:
        return int(x)
    except TypeError:
        return x

def shell_colorify_match(match):
    return SHELL_COLORS[match.groups()[2]]
        
class ExcThread(threading.Thread):
    def __init__(self, bucket, *args, **kargs):
        threading.Thread.__init__(self, *args, **kargs)
        self.bucket = bucket
          
    def run(self):
        try:
            threading.Thread.run(self)
        except Exception:
            self.bucket.put(sys.exc_info())
            raise
            
class Screen(StringIO):
    # tags used to control color of strings and select buffer
    TAG = re.compile("@@((\d+),)?(\d+):", re.MULTILINE)
    def __init__(self, windows):
        StringIO.__init__(self)
        self.windows = windows
        self.autoscroll = {}
        self.pos = {}
        self.lines = {}
        self.maxsize = {}
        self.stdout = None
        self.logfile = None
        self.wrapper = TextWrapper(width=80, initial_indent="",
                                   subsequent_indent="         ",
                                   replace_whitespace=False)

        if NCURSES:
            for windex in windows:
                h, w = windows[windex][0].getmaxyx()
                self.maxsize[windex] = (h, w)
                self.pos[windex] = [0, 0]
                self.autoscroll[windex] = True
                self.lines[windex] = 0

    def scroll(self, win, vt, hz=0, refresh=True):
        line, col = self.pos[win]

        hz_pos = col + hz
        if hz_pos < 0: 
            hz_pos = 0
        elif hz_pos >= 1000:
            hz_pos = 999

        vt_pos = line + vt
        if vt_pos < 0:
            vt_pos = 0
        elif vt_pos >= 1000:
            vt_pos = 1000 - 1

        if line != vt_pos or col != hz_pos:
            self.pos[win] = [vt_pos, hz_pos]
            if refresh:
                self.refresh()

    def scroll_to(self, win, vt, hz=0, refresh=True):
        line, col = self.pos[win]

        hz_pos = hz
        if hz_pos < 0: 
            hz_pos = 0
        elif hz_pos >= 1000:
            hz_pos = 999

        vt_pos = vt
        if vt_pos < 0:
            vt_pos = 0
        elif vt_pos >= 1000:
            vt_pos = 1000 - 1

        if line != vt_pos or col != hz_pos:
            self.pos[win] = [vt_pos, hz_pos]
            if refresh:
                self.refresh()

    def refresh(self):
        for windex, (win, dim) in self.windows.iteritems():
            h, w, sy, sx = dim
            line, col = self.pos[windex]
            if h is not None: 
                win.touchwin()
                win.noutrefresh(line, col, sy+1, sx+1, sy+h-2, sx+w-2)
            else:
                win.noutrefresh()
        curses.doupdate()

    def write(self, text):
        if isinstance(text, unicode):
            #text = text.encode(self.stdout.encoding)
            text = text.encode("UTF-8")
        if NCURSES:
            self.write_curses(text)
            if self.logfile:
                text = re.sub(self.TAG, "", text)
                self.write_log(text)
        else:
            if GLOBALS["color_shell"]: 
                text = re.sub(self.TAG, shell_colorify_match, text)
            else:
                text = re.sub(self.TAG, "", text)
                
            self.write_normal(text)
            if self.logfile:
                self.write_log(text)
            
    def write_log(self, text):
        self.logfile.write(text)
        self.logfile.flush()
            
    def write_normal(self, text):
        #_text = '\n'.join(self.wrapper.wrap(text))
        #self.stdout.write(_text+"\n")
        self.stdout.write(text)
        
    def write_curses(self, text):
        formatstr = deque()
        for m in re.finditer(self.TAG, text):
            x1, x2  = m.span()
            cindex = safe_int(m.groups()[2])
            windex = safe_int(m.groups()[1])
            formatstr.append([x1, x2, cindex, windex])
        if not formatstr:
            formatstr.append([None, 0, 1, 1])

        if formatstr[0][1] == 0:
            stop, start, cindex, windex = formatstr.popleft()
            if windex is None:
                windex = 1
        else:
            stop, start, cindex, windex = None, 0, 1, 1

        while start is not None:
            if formatstr:
                next_stop, next_start, next_cindex, next_windex = formatstr.popleft()
            else:
                next_stop, next_start, next_cindex, next_windex = None, None, cindex, windex

            face = curses.color_pair(cindex)
            win, (h, w, sy, sx) = self.windows[windex]
            ln, cn = self.pos[windex]
            # Is this too inefficient?
            new_lines = text[start:next_stop].count("\n")
            self.lines[windex] += new_lines
            if self.lines[windex] > self.maxsize[windex]:
                _y, _x = win.getyx()
                
                for _i in self.lines[windex]-self.maxsize(windex):
                    win.move(0,0)
                    win.deleteln()
                win.move(_y, _x)
                
            # Visual scroll
            if self.autoscroll[windex]:
                scroll = self.lines[windex] - ln - h
                if scroll > 0:
                    self.scroll(windex, scroll, refresh=False)
                            
            try:
                win.addstr(text[start:next_stop], face)
            except curses.error: 
                win.addstr("???")
                
            start = next_start
            stop = next_stop
            cindex = next_cindex
            if next_windex is not None:
                windex = next_windex
        
        self.refresh()

    def resize_screen(self, s, frame):

        import sys,fcntl,termios,struct 
        data = fcntl.ioctl(self.stdout.fileno(), termios.TIOCGWINSZ, '1234') 
        h, w = struct.unpack('hh', data) 

        win = self.windows
        #main = curses.initscr()
        #h, w = main.getmaxyx()
        #win[0] = (main, (None, None, 0, 0))
        #curses.resizeterm(h, w)

        win[0][0].resize(h, w)
        win[0][0].clear()
        info_win, error_win, debug_win = setup_layout(h, w)
        win[1][1] = info_win
        win[2][1] = error_win
        win[3][1] = debug_win
        self.refresh()

def init_curses(main_scr):
    if not NCURSES or not main_scr:
        # curses disabled, no multi windows
        return None

    # Colors
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(11, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    curses.init_pair(12, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
    
    WIN = {}
    main = main_scr
    h, w = main.getmaxyx()
    WIN[0] = (main, (None, None, 0, 0))

    # Creates layout
    info_win, error_win, debug_win = setup_layout(h, w)
     
    WIN[1] = [curses.newpad(5000, 1000), info_win]
    WIN[2] = [curses.newpad(5000, 1000), error_win]
    WIN[3] = [curses.newpad(5000, 1000), debug_win]
    

    #WIN[1], WIN[11] = newwin(h-1, w/2, 1,1)
    #WIN[2], WIN[12] = newwin(h-dbg_h-1, (w/2)-1, 1, (w/2)+2)
    #WIN[3], WIN[13] = newwin(dbg_h-1, (w/2)-1, h-dbg_h+1, (w/2)+2)

    for windex, (w, dim) in WIN.iteritems():
        #w = WIN[i]
        #w.bkgd(str(windex))
        w.bkgd(" ")
        w.keypad(1)
        w.idlok(True)
        w.scrollok(True)
    return WIN

def clear_env():
    try:
        terminate_job_launcher()
    except:
        pass
        
    base_dir = GLOBALS["basedir"]
    lock_file = pjoin(base_dir, "alive")
    try:
        os.remove(lock_file)
    except Exception:
        print >>sys.stderr, "could not remove lock file %s" %lock_file
        
    clear_tempdir()

def app_wrapper(func, args):
    global NCURSES
    base_dir = GLOBALS.get("scratch_dir", GLOBALS["basedir"])
    lock_file = pjoin(base_dir, "alive")

    if not args.enable_ui:
        NCURSES = False
    
    if not pexist(lock_file) or args.clearall:
        open(lock_file, "w").write(time.ctime())
    else:
        clear_env()
        print >>sys.stderr, '\nThe same process seems to be running. Use --clearall or remove the lock file "alive" within the output dir'
        sys.exit(-1)
        
    try:
        if NCURSES:
            curses.wrapper(main, func, args)
        else:
            main(None, func, args)
    except ConfigError, e:
        if GLOBALS.get('_background_scheduler', None):
            GLOBALS['_background_scheduler'].terminate()

        print >>sys.stderr, "\nConfiguration Error:", e
        clear_env()
        sys.exit(-1)
    except DataError, e:
        if GLOBALS.get('_background_scheduler', None):
            GLOBALS['_background_scheduler'].terminate()

        print >>sys.stderr, "\nData Error:", e
        clear_env()
        sys.exit(-1)
    except KeyboardInterrupt:
        # Control-C is also grabbed by the back_launcher, so it is no necessary
        # to terminate from here
        print >>sys.stderr, "\nProgram was interrupted."
        if args.monitor:
            print >>sys.stderr, ("VERY IMPORTANT !!!: Note that launched"
                                 " jobs will keep running as you provided the --monitor flag")        
        clear_env()
        sys.exit(-1)
    except:
        if GLOBALS.get('_background_scheduler', None):
            GLOBALS['_background_scheduler'].terminate()
            
        clear_env()
        raise
    else:
        if GLOBALS.get('_background_scheduler', None):
            GLOBALS['_background_scheduler'].terminate()
            
        clear_env()

    
def main(main_screen, func, args):
    """ Init logging and Screen. Then call main function """

    # Do I use ncurses or basic terminal interface? 
    screen = Screen(init_curses(main_screen))

    # prints are handled by my Screen object
    screen.stdout = sys.stdout
    if args.logfile: 
        screen.logfile = open(os.path.join(GLOBALS["basedir"], "npr.log"), "w")
    sys.stdout = screen
    sys.stderr = screen
    
    # Start logger, pointing to the selected screen
    log = get_main_log(screen, [28,26,24,22,20,10][args.verbosity])

    # Call main function as lower thread
    if NCURSES:
        screen.refresh()
        exceptions = Queue.Queue()
        t = ExcThread(bucket=exceptions, target=func, args=[args])
        t.daemon = True
        t.start()
        ln = 0           
        chars = "\\|/-\\|/-"
        cbuff = 1
        try:
            while 1:
                try:
                    exc = exceptions.get(block=False)
                except Queue.Empty:
                    pass
                else:
                    exc_type, exc_obj, exc_trace = exc
                    # deal with the exception
                    #print exc_trace, exc_type, exc_obj
                    raise exc_obj
     
                mwin = screen.windows[0][0]
                key = mwin.getch()
                mwin.addstr(0, 0, "%s (%s) (%s) (%s)" %(key, screen.pos, ["%s %s" %(i,w[1]) for i,w in screen.windows.items()], screen.lines) + " "*50)
                mwin.refresh()
                if key == 113:
                    # Fixes the problem of prints without newline char
                    raise KeyboardInterrupt("Q Pressed")
                if key == 9: 
                    cbuff += 1
                    if cbuff>3: 
                        cbuff = 1
                elif key == curses.KEY_UP:
                    screen.scroll(cbuff, -1)
                elif key == curses.KEY_DOWN:
                    screen.scroll(cbuff, 1)
                elif key == curses.KEY_LEFT:
                    screen.scroll(cbuff, 0, -1)
                elif key == curses.KEY_RIGHT:
                    screen.scroll(cbuff, 0, 1)
                elif key == curses.KEY_NPAGE:
                    screen.scroll(cbuff, 10)
                elif key == curses.KEY_PPAGE:
                    screen.scroll(cbuff, -10)
                elif key == curses.KEY_END:
                    screen.scroll_to(cbuff, 999, 0)
                elif key == curses.KEY_HOME:
                    screen.scroll_to(cbuff, 0, 0)
                elif key == curses.KEY_RESIZE:
                    screen.resize_screen(None, None)
                else:
                    pass
        except:
            # fixes the problem of restoring screen when last print
            # did not contain a newline char. WTF!
            print "\n"
            raise

        #while 1: 
        #    if ln >= len(chars):
        #        ln = 0
        #    #screen.windows[0].addstr(0,0, chars[ln])
        #    #screen.windows[0].refresh()
        #    time.sleep(0.2)
        #    ln += 1
    else:
        func(args)

def setup_layout(h, w):
    # Creates layout
    header = 4
    
    start_x = 0
    start_y = header
    h -= start_y
    w -= start_x

    h1 = h/2 + h%2
    h2 = h/2 
    if w > 160:
        #  _______
        # |   |___|
        # |___|___|
        w1 = w/2 + w%2
        w2 = w/2 
        info_win = [h, w1, start_y, start_x]
        error_win = [h1, w2, start_y, w1]
        debug_win = [h2, w2, h1, w1]
    else:
        #  ___
        # |___|
        # |___|
        # |___|
        h2a = h2/2 + h2%2 
        h2b = h2/2
        info_win = [h1, w, start_y, start_x]
        error_win = [h2a, w, h1, start_x]
        debug_win = [h2b, w, h1+h2a, start_x]
   
    return info_win, error_win, debug_win


