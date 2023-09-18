import os
import re
import time
import random
import colorsys

try:
    import numpy
except ImportError:
    mean = lambda v: sum(v)/len(v)
else:
    mean = numpy.mean


# CONVERT shell colors to the same curses palette
SHELL_COLORS = {
    "wr": '\033[1;37;41m',  # white on red
    "wo": '\033[1;37;43m',  # white on orange
    "wm": '\033[1;37;45m',  # white on magenta
    "wb": '\033[1;37;46m',  # white on blue
    "bw": '\033[1;37;40m',  # black on white
    "lblue": '\033[1;34m',  # light blue
    "lred": '\033[1;31m',   # light red
    "lgreen": '\033[1;32m', # light green
    "yellow": '\033[1;33m', # yellow
    "cyan": '\033[36m',     # cyan
    "blue": '\033[34m',     # blue
    "green": '\033[32m',    # green
    "orange": '\033[33m',   # orange
    "red": '\033[31m',      # red
    "magenta": "\033[35m",  # magenta
    "white": "\033[0m",     # white
    None: "\033[0m",        # end
}


def color(string, color):
    return "%s%s%s" % (SHELL_COLORS[color], string, SHELL_COLORS[None])


def clear_color(string):
    return re.sub("\\033\[[^m]+m", "", string)


def print_table(items, header=None, wrap=True, max_col_width=20,
                wrap_style="wrap", row_line=False, fix_col_width=False, title=None):
    """Print a matrix of data as a human readable table.

    :param items: List of lists containing any type of values that can
        be converted into text strings.
    :param wrap: If False, column widths are set to fit all values in
        each column.
    :param wrap_style: Column adjustment method. It can be "wrap" to
        wrap values to fit `max_col_width` (by extending cell height),
        or "cut": to strip values to `max_col_width`.

    Example::

      print_table([[3, 2, {"whatever": 1, "bla": [1,2]}],
                   [5,"this is a test\n             of wrapping text\n"
                      "with the new function", 777], [1, 1, 1]],
                  header=["This is column number 1", "Column number 2", "col3"],
                  wrap=True, max_col_width=15, wrap_style='wrap',
                  row_line=True, fix_col_width=True)

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

    """
    # See https://gist.github.com/jhcepas/5884168
    def safelen(string):
        return len(clear_color(string))

    if isinstance(fix_col_width, list):
        c2maxw = {i: fix_col_width[i] for i in range(len(items[0]))}
        wrap = True
    elif fix_col_width == True:
        c2maxw = {i: max_col_width for i in range(len(items[0]))}
        wrap = True
    elif not wrap:
        c2maxw = {i: max([safelen(str(e[i])) for e in items]) for i in range(len(items[0]))}
    else:
        c2maxw = {i: min(max_col_width, max([safelen(str(e[i])) for e in items]))
                        for i in range(len(items[0]))}

    if header:
        current_item = -1
        row = header
        if wrap and not fix_col_width:
            for col, maxw in c2maxw.items():
                c2maxw[col] = max(maxw, safelen(header[col]))
                if wrap:
                    c2maxw[col] = min(c2maxw[col], max_col_width)
    else:
        current_item = 0
        row = items[current_item]

    if title:
        table_width = sum(c2maxw.values()) + (3*(len(c2maxw)-1))
        print("-" *table_width)
        print(title.center(table_width))
        print("-" *table_width)

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
        print(' | '.join(values))
        if not set(extra_line) - set(['']):
            if header and current_item == -1:
                print(' | '.join(['='*c2maxw[col] for col in range(len(row)) ]))
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
                print(' | '.join(['-'*c2maxw[col] for col in range(len(row)) ]))
            else:
                print(' | '.join(['='*c2maxw[col] for col in range(len(extra_line)) ]))



def ask(string, valid_values, default=-1, case_sensitive=False):
    """Keep asking until we get a valid answer and return it."""
    while True:
        answer = input('%s [%s] ' % (string, ','.join(valid_values)))

        if not answer and default >= 0:
            return valid_values[default]

        if case_sensitive and answer in valid_values:
            return answer
        elif (not case_sensitive and
              answer.lower() in [v.lower() for v in valid_values]):
            return answer.lower()


def timeit(f):
    def a_wrapper_accepting_arguments(*args, **kargs):
        t1 = time.time()
        r = f(*args, **kargs)
        print("    ", f.__name__, time.time() - t1, "seconds")
        return r
    return a_wrapper_accepting_arguments


SVG_COLORS = {
    "indianred",       #        CD5C5C  2059292
    "lightcoral",      #        F08080  240128128
    "salmon",          #        FA8072  250128114
    "darksalmon",      #        E9967A  233150122
    "lightsalmon",     #        FFA07A  255160122
    "crimson",         #        DC143C  2202060
    "red",             #        FF0000  25500
    "firebrick",       #        B22222  1783434
    "darkred",         #        8B0000  13900
    "pink",            #        FFC0CB  255192203
    "lightpink",       #        FFB6C1  255182193
    "hotpink",         #        FF69B4  255105180
    "deeppink",        #        FF1493  25520147
    "mediumvioletred", #        C71585  19921133
    "palevioletred",   #        DB7093  219112147
    "lightsalmon",     #        FFA07A  255160122
    "coral",           #        FF7F50  25512780
    "tomato",          #        FF6347  2559971
    "orangered",       #        FF4500  255690
    "darkorange",      #        FF8C00  2551400
    "orange",          #        FFA500  2551650
    "gold",            #        FFD700  2552150
    "yellow",          #        FFFF00  2552550
    "lightyellow",     #        FFFFE0  255255224
    "lemonchiffon",    #        FFFACD  255250205
    "lightgoldenrodyellow", #   FAFAD2  250250210
    "papayawhip",      #        FFEFD5  255239213
    "moccasin",        #        FFE4B5  255228181
    "peachpuff",       #        FFDAB9  255218185
    "palegoldenrod",   #        EEE8AA  238232170
    "khaki",           #        F0E68C  240230140
    "darkkhaki",       #        BDB76B  189183107
    "lavender",        #        E6E6FA  230230250
    "thistle",         #        D8BFD8  216191216
    "plum",            #        DDA0DD  221160221
    "violet",          #        EE82EE  238130238
    "orchid",          #        DA70D6  218112214
    "fuchsia",         #        FF00FF  2550255
    "magenta",         #        FF00FF  2550255
    "mediumorchid",    #        BA55D3  18685211
    "mediumpurple",    #        9370DB  147112219
    "amethyst",        #        9966CC  153102204
    "blueviolet",      #        8A2BE2  13843226
    "darkviolet",      #        9400D3  1480211
    "darkorchid",      #        9932CC  15350204
    "darkmagenta",     #        8B008B  1390139
    "purple",          #        800080  1280128
    "indigo",          #        4B0082  750130
    "slateblue",       #        6A5ACD  10690205
    "darkslateblue",   #        483D8B  7261139
    "mediumslateblue", #        7B68EE  123104238
    "greenyellow",     #        ADFF2F  17325547
    "chartreuse",      #        7FFF00  1272550
    "lawngreen",       #        7CFC00  1242520
    "lime",            #        00FF00  02550
    "limegreen",       #        32CD32  5020550
    "palegreen",       #        98FB98  152251152
    "lightgreen",      #        90EE90  144238144
    "mediumspringgreen", #      00FA9A  0250154
    "springgreen",     #        00FF7F  0255127
    "mediumseagreen",  #        3CB371  60179113
    "seagreen",        #        2E8B57  4613987
    "forestgreen",     #        228B22  3413934
    "green",           #        008000  01280
    "darkgreen",       #        006400  01000
    "yellowgreen",     #        9ACD32  15420550
    "olivedrab",       #        6B8E23  10714235
    "olive",           #        808000  1281280
    "darkolivegreen",  #        556B2F  8510747
    "mediumaquamarine", #       66CDAA  102205170
    "darkseagreen",    #        8FBC8F  143188143
    "lightseagreen"    #        20B2AA  32178170
    "darkcyan",        #        008B8B  0139139
    "teal",            #        008080  0128128
    "aqua",            #        00FFFF  0255255
    "cyan",            #        00FFFF  0255255
    "lightcyan",       #        E0FFFF  224255255
    "paleturquoise",   #        AFEEEE  175238238
    "aquamarine",      #        7FFFD4  127255212
    "turquoise",       #        40E0D0  64224208
    "mediumturquoise", #        48D1CC  72209204
    "darkturquoise",   #        00CED1  0206209
    "cadetblue",       #        5F9EA0  95158160
    "steelblue",       #        4682B4  70130180
    "lightsteelblue",  #        B0C4DE  176196222
    "powderblue",      #        B0E0E6  176224230
    "lightblue",       #        ADD8E6  173216230
    "skyblue",         #        87CEEB  135206235
    "lightskyblue",    #        87CEFA  135206250
    "deepskyblue",     #        00BFFF  0191255
    "dodgerblue",      #        1E90FF  30144255
    "cornflowerblue",  #        6495ED  100149237
    "mediumslateblue", #        7B68EE  123104238
    "royalblue",       #        4169E1  65105225
    "blue",            #        0000FF  00255
    "mediumblue",      #        0000CD  00205
    "darkblue",        #        00008B  00139
    "navy",            #        000080  00128
    "midnightblue",    #        191970  2525112
    "cornsilk",        #        FFF8DC  255248220
    "blanchedalmond",  #        FFEBCD  255235205
    "bisque",          #        FFE4C4  255228196
    "navajowhite",     #        FFDEAD  255222173
    "wheat",           #        F5DEB3  245222179
    "burlywood",       #        DEB887  222184135
    "tan",             #        D2B48C  210180140
    "rosybrown",       #        BC8F8F  188143143
    "sandybrown",      #        F4A460  24416496
    "goldenrod",       #        DAA520  21816532
    "darkgoldenrod",   #        B8860B  18413411
    "peru",            #        CD853F  20513363
    "chocolate",       #        D2691E  21010530
    "saddlebrown",     #        8B4513  1396919
    "sienna",          #        A0522D  1608245
    "brown",           #        A52A2A  1654242
    "maroon",          #        800000  12800
    "white",           #        FFFFFF  255255255
    "snow",            #        FFFAFA  255250250
    "honeydew",        #        F0FFF0  240255240
    "mintcream",       #        F5FFFA  245255250
    "azure",           #        F0FFFF  240255255
    "aliceblue",       #        F0F8FF  240248255
    "ghostwhite",      #        F8F8FF  248248255
    "whitesmoke",      #        F5F5F5  245245245
    "seashell",        #        FFF5EE  255245238
    "beige",           #        F5F5DC  245245220
    "oldlace",         #        FDF5E6  253245230
    "floralwhite",     #        FFFAF0  255250240
    "ivory",           #        FFFFF0  255255240
    "antiquewhite",    #        FAEBD7  250235215
    "linen",           #        FAF0E6  250240230
    "lavenderblush",   #        FFF0F5  255240245
    "mistyrose",       #        FFE4E1  255228225
    "gainsboro",       #        DCDCDC  220220220
    "lightgrey",       #        D3D3D3  211211211
    "silver",          #        C0C0C0  192192192
    "darkgray",        #        A9A9A9  169169169
    "gray",            #        808080  128128128
    "dimgray",         #        696969  105105105
    "lightslategray",  #        778899  119136153
    "slategray",       #        708090  112128144
    "darkslategray",   #        2F4F4F  477979
    "black"}           #        000000  000


COLOR_SCHEMES = {
    'accent': [
        '#7fc97f',
        '#beaed4',
        '#fdc086',
        '#ffff99',
        '#386cb0',
        '#f0027f',
        '#bf5b17',
        '#666666'],
    'blues': [
        '#f7fbff',
        '#deebf7',
        '#c6dbef',
        '#9ecae1',
        '#6baed6',
        '#4292c6',
        '#2171b5',
        '#08519c',
        '#08306b'],
    'brbg': [
        '#543005',
        '#8c510a',
        '#bf812d',
        '#dfc27d',
        '#f6e8c3',
        '#f5f5f5',
        '#c7eae5',
        '#80cdc1',
        '#35978f',
        '#01665e',
        '#003c30'],
    'bugn': [
        '#f7fcfd',
        '#e5f5f9',
        '#ccece6',
        '#99d8c9',
        '#66c2a4',
        '#41ae76',
        '#238b45',
        '#006d2c',
        '#00441b'],
    'bupu': [
        '#f7fcfd',
        '#e0ecf4',
        '#bfd3e6',
        '#9ebcda',
        '#8c96c6',
        '#8c6bb1',
        '#88419d',
        '#810f7c',
        '#4d004b'],
    'dark2': [
        '#1b9e77',
        '#d95f02',
        '#7570b3',
        '#e7298a',
        '#66a61e',
        '#e6ab02',
        '#a6761d',
        '#666666'],
    'gnbu': [
        '#f7fcf0',
        '#e0f3db',
        '#ccebc5',
        '#a8ddb5',
        '#7bccc4',
        '#4eb3d3',
        '#2b8cbe',
        '#0868ac',
        '#084081'],
    'greens': [
        '#f7fcf5',
        '#e5f5e0',
        '#c7e9c0',
        '#a1d99b',
        '#74c476',
        '#41ab5d',
        '#238b45',
        '#006d2c',
        '#00441b'],
    'greys': [
        '#ffffff',
        '#f0f0f0',
        '#d9d9d9',
        '#bdbdbd',
        '#969696',
        '#737373',
        '#525252',
        '#252525',
        '#000000'],
    'orrd': [
        '#fff7ec',
        '#fee8c8',
        '#fdd49e',
        '#fdbb84',
        '#fc8d59',
        '#ef6548',
        '#d7301f',
        '#b30000',
        '#7f0000'],
    'oranges': [
        '#fff5eb',
        '#fee6ce',
        '#fdd0a2',
        '#fdae6b',
        '#fd8d3c',
        '#f16913',
        '#d94801',
        '#a63603',
        '#7f2704'],
    'prgn': [
        '#40004b',
        '#762a83',
        '#9970ab',
        '#c2a5cf',
        '#e7d4e8',
        '#f7f7f7',
        '#d9f0d3',
        '#a6dba0',
        '#5aae61',
        '#1b7837',
        '#00441b'],
    'paired': [
        '#a6cee3',
        '#1f78b4',
        '#b2df8a',
        '#33a02c',
        '#fb9a99',
        '#e31a1c',
        '#fdbf6f',
        '#ff7f00',
        '#cab2d6',
        '#6a3d9a',
        '#ffff99',
        '#b15928'],
    'pastel1': [
        '#fbb4ae',
        '#b3cde3',
        '#ccebc5',
        '#decbe4',
        '#fed9a6',
        '#ffffcc',
        '#e5d8bd',
        '#fddaec',
        '#f2f2f2'],
    'pastel2': [
        '#b3e2cd',
        '#fdcdac',
        '#cbd5e8',
        '#f4cae4',
        '#e6f5c9',
        '#fff2ae',
        '#f1e2cc',
        '#cccccc'],
    'piyg': [
        '#8e0152',
        '#c51b7d',
        '#de77ae',
        '#f1b6da',
        '#fde0ef',
        '#f7f7f7',
        '#e6f5d0',
        '#b8e186',
        '#7fbc41',
        '#4d9221',
        '#276419'],
    'pubu': [
        '#fff7fb',
        '#ece7f2',
        '#d0d1e6',
        '#a6bddb',
        '#74a9cf',
        '#3690c0',
        '#0570b0',
        '#045a8d',
        '#023858'],
    'pubugn': [
        '#fff7fb',
        '#ece2f0',
        '#d0d1e6',
        '#a6bddb',
        '#67a9cf',
        '#3690c0',
        '#02818a',
        '#016c59',
        '#014636'],
    'puor': [
        '#7f3b08',
        '#b35806',
        '#e08214',
        '#fdb863',
        '#fee0b6',
        '#f7f7f7',
        '#d8daeb',
        '#b2abd2',
        '#8073ac',
        '#542788',
        '#2d004b'],
    'purd': [
        '#f7f4f9',
        '#e7e1ef',
        '#d4b9da',
        '#c994c7',
        '#df65b0',
        '#e7298a',
        '#ce1256',
        '#980043',
        '#67001f'],
    'purples': [
        '#fcfbfd',
        '#efedf5',
        '#dadaeb',
        '#bcbddc',
        '#9e9ac8',
        '#807dba',
        '#6a51a3',
        '#54278f',
        '#3f007d'],
    'rdbu': [
        '#67001f',
        '#b2182b',
        '#d6604d',
        '#f4a582',
        '#fddbc7',
        '#f7f7f7',
        '#d1e5f0',
        '#92c5de',
        '#4393c3',
        '#2166ac',
        '#053061'],
    'rdgy': [
        '#67001f',
        '#b2182b',
        '#d6604d',
        '#f4a582',
        '#fddbc7',
        '#ffffff',
        '#e0e0e0',
        '#bababa',
        '#878787',
        '#4d4d4d',
        '#1a1a1a'],
    'rdpu': [
        '#fff7f3',
        '#fde0dd',
        '#fcc5c0',
        '#fa9fb5',
        '#f768a1',
        '#dd3497',
        '#ae017e',
        '#7a0177',
        '#49006a'],
    'rdylbu': [
        '#a50026',
        '#d73027',
        '#f46d43',
        '#fdae61',
        '#fee090',
        '#ffffbf',
        '#e0f3f8',
        '#abd9e9',
        '#74add1',
        '#4575b4',
        '#313695'],
    'rdylgn': [
        '#a50026',
        '#d73027',
        '#f46d43',
        '#fdae61',
        '#fee08b',
        '#ffffbf',
        '#d9ef8b',
        '#a6d96a',
        '#66bd63',
        '#1a9850',
        '#006837'],
    'reds': [
        '#fff5f0',
        '#fee0d2',
        '#fcbba1',
        '#fc9272',
        '#fb6a4a',
        '#ef3b2c',
        '#cb181d',
        '#a50f15',
        '#67000d'],
    'set1': [
        '#e41a1c',
        '#377eb8',
        '#4daf4a',
        '#984ea3',
        '#ff7f00',
        '#ffff33',
        '#a65628',
        '#f781bf',
        '#999999'],
    'set2': [
        '#66c2a5',
        '#fc8d62',
        '#8da0cb',
        '#e78ac3',
        '#a6d854',
        '#ffd92f',
        '#e5c494',
        '#b3b3b3'],
    'set3': [
        '#8dd3c7',
        '#ffffb3',
        '#bebada',
        '#fb8072',
        '#80b1d3',
        '#fdb462',
        '#b3de69',
        '#fccde5',
        '#d9d9d9',
        '#bc80bd',
        '#ccebc5',
        '#ffed6f'],
    'spectral': [
        '#9e0142',
        '#d53e4f',
        '#f46d43',
        '#fdae61',
        '#fee08b',
        '#ffffbf',
        '#e6f598',
        '#abdda4',
        '#66c2a5',
        '#3288bd',
        '#5e4fa2'],
    'ylgn': [
        '#ffffe5',
        '#f7fcb9',
        '#d9f0a3',
        '#addd8e',
        '#78c679',
        '#41ab5d',
        '#238443',
        '#006837',
        '#004529'],
    'ylgnbu': [
        '#ffffd9',
        '#edf8b1',
        '#c7e9b4',
        '#7fcdbb',
        '#41b6c4',
        '#1d91c0',
        '#225ea8',
        '#253494',
        '#081d58'],
    'ylorbr': [
        '#ffffe5',
        '#fff7bc',
        '#fee391',
        '#fec44f',
        '#fe9929',
        '#ec7014',
        '#cc4c02',
        '#993404',
        '#662506'],
    'ylorrd': [
        '#ffffcc',
        '#ffeda0',
        '#fed976',
        '#feb24c',
        '#fd8d3c',
        '#fc4e2a',
        '#e31a1c',
        '#bd0026',
        '#800026']}


def random_color(h=None, l=None, s=None, num=None, sep=None, seed=None):
    """Return the RGB code of a random color.

    Hue (h), Lightness (l) and Saturation (s) of the generated color
    can be specified as arguments.
    """
    def rgb2hex(rgb):
        return '#%02x%02x%02x' % rgb

    def hls2hex(h, l, s):
        return rgb2hex( tuple([int(x*255) for x in colorsys.hls_to_rgb(h, l, s)]))

    if not h:
        if seed:
            random.seed(seed)
        color = 1.0 / random.randint(1, 360)
    else:
        color = h

    if not num:
        n = 1
        sep = 1
    else:
        n = num

    if not sep:
        n = num
        sep = (1.0/n)

    evenly_separated_colors =  [color + (sep*n) for n in range(n)]

    rcolors = []
    for h in evenly_separated_colors:
        if not s:
            s = 0.5
        if not l:
            l = 0.5
        rcolors.append(hls2hex(h, l, s))

    if num:
        return rcolors
    else:
        return rcolors[0]
