# This is a flag used to build ete2 standalone package.
in_ete_pkg=True
from PIL import Image, ImageDraw 
import numpy

def new_image(w, h, bg_color):
    return Image.new("RGB",(w,h), bg_color)

def new_drawer(i):
    return ImageDraw.Draw(i)

def save_image(i, fname):
    i.save(fname)

def draw_line(drawer, x1, y1, x2, y2, color="#000000", ltype="solid"):
    drawer.line( ((x1,y1), (x2,y2)), color)

def draw_ellipse(drawer, x1, y1, x2, y2, color="#000000"):
    drawer.ellipse( ((x1,y1), (x2,y2)), color)

def draw_text(drawer, x1, y1, text):
    drawer.text( (x1,y1), text, "black")

def draw_rectangle(drawer, x1, y1):
    pass


