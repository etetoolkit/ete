import re
import time
import readline
import os

# CONVERT shell colors to the same curses palette
SHELL_COLORS = {
    "wr": '\033[1;37;41m', # white on red
    "wo": '\033[1;37;43m', # white on orange
    "wm": '\033[1;37;45m', # white on magenta
    "wb": '\033[1;37;46m', # white on blue
    "bw": '\033[1;37;40m', # black on white
    "lblue": '\033[1;34m', # light blue
    "lred": '\033[1;31m', # light red
    "lgreen": '\033[1;32m', # light green
    "yellow": '\033[1;33m', # yellow
    "cyan": '\033[36m', # cyan
    "blue": '\033[34m', # blue
    "green": '\033[32m', # green
    "orange": '\033[33m', # orange
    "red": '\033[31m', # red
    "magenta": "\033[35m", # magenta
    "white": "\033[0m", # white
    None: "\033[0m", # end
}


def color(string, color):
    return "%s%s%s" %(SHELL_COLORS[color], string, SHELL_COLORS[None])

def clear_color(string):
    return re.sub("\\033\[[^m]+m", "", string)

def print_table(items, header=None, wrap=True, max_col_width=20,
                wrap_style="wrap", row_line=False, fix_col_width=False):
    ''' Prints a matrix of data as a human readable table. Matrix
    should be a list of lists containing any type of values that can
    be converted into text strings.

    Two different column adjustment methods are supported through
    the *wrap_style* argument:

       wrap: it will wrap values to fit max_col_width (by extending cell height)
       cut: it will strip values to max_col_width

    If the *wrap* argument is set to False, column widths are set to fit all
    values in each column.

    This code is free software. Updates can be found at
    https://gist.github.com/jhcepas/5884168


    # print_table([[3,2, {"whatever":1, "bla":[1,2]}], [5,"this is a test\n             of wrapping text\n  with the new function",777], [1,1,1]],
    #            header=[ "This is column number 1", "Column number 2", "col3"],
    #            wrap=True, max_col_width=15, wrap_style='wrap',
    #            row_line=True, fix_col_width=True)


    # This is column  | Column number 2 | col3
    # number 1        |                 |
    # =============== | =============== | ===============
    # 3               | 2               | {'bla': [1, 2],
    #                 |                 |  'whatever': 1}
    # --------------- | --------------- | ---------------
    # 5               | this is a test  | 777
    #                 |              of |
    #                 |  wrapping text  |
    #                 |   with the new  |
    #                 | function        |
    # --------------- | --------------- | ---------------
    # 1               | 1               | 1
    # =============== | =============== | ===============

    '''
    def safelen(string):
        return len(clear_color(string))

    if isinstance(fix_col_width, list):
        c2maxw = dict([(i, fix_col_width[i]) for i in xrange(len(items[0]))])
        wrap = True
    elif fix_col_width == True:
        c2maxw = dict([(i, max_col_width) for i in xrange(len(items[0]))])
        wrap = True
    elif not wrap:
        c2maxw = dict([(i, max([safelen(str(e[i])) for e in items])) for i in xrange(len(items[0]))])
    else:
        c2maxw = dict([(i, min(max_col_width, max([safelen(str(e[i])) for e in items])))
                        for i in xrange(len(items[0]))])
    if header:
        current_item = -1
        row = header
        if wrap and not fix_col_width:
            for col, maxw in c2maxw.iteritems():
                c2maxw[col] = max(maxw, safelen(header[col]))
                if wrap:
                    c2maxw[col] = min(c2maxw[col], max_col_width)
    else:
        current_item = 0
        row = items[current_item]
    while row:
        is_extra = False
        values = []
        extra_line = [""]*len(row)
        for col, val in enumerate(row):
            cwidth = c2maxw[col]
            wrap_width = cwidth
            val = clear_color(str(val))
            try:
                newline_i = val.index("\n")
            except ValueError:
                pass
            else:
                wrap_width = min(newline_i+1, wrap_width)
                val = val.replace("\n", " ", 1)
            if wrap and safelen(val) > wrap_width:
                if wrap_style == "cut":
                    val = val[:wrap_width-1]+"+"
                elif wrap_style == "wrap":
                    extra_line[col] = val[wrap_width:]
                    val = val[:wrap_width]
            val = val.ljust(cwidth)
            values.append(val)
        print ' | '.join(values)
        if not set(extra_line) - set(['']):
            if header and current_item == -1:
                print ' | '.join(['='*c2maxw[col] for col in xrange(len(row)) ])
            current_item += 1
            try:
                row = items[current_item]
            except IndexError:
                row = None
        else:
            row = extra_line
            is_extra = True

        if row_line and not is_extra and not (header and current_item == 0):
            if row:
                print ' | '.join(['-'*c2maxw[col] for col in xrange(len(row)) ])
            else:
                print ' | '.join(['='*c2maxw[col] for col in xrange(len(extra_line)) ])

def ask_filename(text):
    readline.set_completer(None)
    fname = ""
    while not os.path.exists(fname):
        fname = raw_input(text)
    return fname

def ask(string,valid_values,default=-1,case_sensitive=False):
    """ Asks for a keyborad answer """
    v = None
    if not case_sensitive:
        valid_values = [value.lower() for value in valid_values]
    while v not in valid_values:
        v = raw_input("%s [%s]" % (string,','.join(valid_values) ))
        if v == '' and default>=0:
            v = valid_values[default]
        if not case_sensitive:
            v = v.lower()
    return v

def timeit(f):
    def a_wrapper_accepting_arguments(*args, **kargs):
        t1 = time.time()
        r = f(*args, **kargs)
        print "    ", f.func_name, time.time() - t1, "seconds"
        return r
    return a_wrapper_accepting_arguments

def cmp_to_key(mycmp):
    """Convert a cmp= function into a key= function
    See: https://docs.python.org/3/howto/sorting.html
    """
    class K:
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K
