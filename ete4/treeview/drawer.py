import types
import signal

from .qt import *

from .qt_gui import _GUI, _PropertiesDialog, _BasicNodeActions

from . import layouts
from .main import save
from .qt_render import _TreeScene, render, get_tree_img_map, init_tree_style

__all__ = ["show_tree", "render_tree"]

_QApp = None
GUI_TIMEOUT = None

def exit_gui(a, b):
    _QApp.exit(0)

def init_scene(t, layout, ts):
    global _QApp

    ts = init_tree_style(t, ts)
    if layout:
        ts.layout_fn  = layout

    if not _QApp:
        _QApp = QApplication(["ETE"])

    scene = _TreeScene()

    return scene, ts

def show_tree(t, layout=None, tree_style=None, win_name=None):
    """ Interactively shows a tree."""
    scene, img = init_scene(t, layout, tree_style)
    tree_item, n2i, n2f = render(t, img)
    scene.init_values(t, img, n2i, n2f)

    tree_item.setParentItem(scene.master_item)
    scene.addItem(scene.master_item)

    mainapp = _GUI(scene)
    if win_name:
        mainapp.setObjectName(win_name)

    mainapp.show()
    mainapp.on_actionFit2tree_triggered()
    # Restore Ctrl-C behavior
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    if GUI_TIMEOUT is not None:
        signal.signal(signal.SIGALRM, exit_gui)
        signal.alarm(GUI_TIMEOUT)

    _QApp.exec()

def render_tree(t, imgName, w=None, h=None, layout=None,
                tree_style = None, header=None, units="px",
                dpi=90):
    """ Render tree image into a file."""
    global _QApp
    for nid, n in enumerate(t.traverse("preorder")):
        n.add_prop("_nid", nid)
    scene, img = init_scene(t, layout, tree_style)
    tree_item, n2i, n2f = render(t, img)

    scene.init_values(t, img, n2i, n2f)
    tree_item.setParentItem(scene.master_item)
    scene.master_item.setPos(0,0)
    scene.addItem(scene.master_item)
    if imgName.startswith("%%inline"):
        imgmap = save(scene, imgName, w=w, h=h, units=units, dpi=dpi)
    else:
        x_scale, y_scale = save(scene, imgName, w=w, h=h, units=units, dpi=dpi)
        imgmap = get_tree_img_map(n2i, x_scale, y_scale)
    return imgmap


class RenderThread(QThread):
    def __init__(self, tree, layout, tree_style, w, h, dpi, units, rformat):
        self.tree = tree
        self.layout = layout
        self.tree_style = tree_style
        self.w = w
        self.h = h
        self.dpi = dpi
        self.units = units
        self.return_format = rformat
        self.result = None

        QThread.__init__(self)

    def run(self):
        scene, img = init_scene(self.tree, self.layout, self.tree_style)
        tree_item, n2i, n2f = render(self.tree, img)

        scene.init_values(self.tree, img, n2i, n2f)

        tree_item.setParentItem(scene.master_item)
        scene.master_item.setPos(0, 0)
        scene.addItem(scene.master_item)
        x_scale, y_scale, imgdata = save(scene, self.return_format, w=self.w,
                                         h=self.h, units=self.units, dpi=self.dpi)
        if 'PNG' in self.return_format:
            img_map = get_tree_img_map(n2i, x_scale, y_scale)
        else:
            img_map = {}

        self.result = [imgdata, img_map]


def get_img(t, w=None, h=None, layout=None, tree_style = None,
            header=None, units="px", dpi=90, return_format="%%return"):
    global _QApp
    if not _QApp:
        _QApp = QApplication(["ETE"])

    r = RenderThread(t, layout, tree_style, w, h, dpi, units, return_format)
    r.start()
    r.wait()
    return r.result
