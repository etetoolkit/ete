import types
from PyQt4 import QtGui
from PyQt4 import QtCore
from qt4_gui import _GUI, _PropertiesDialog, _BasicNodeActions

import layouts
from ete_dev import Tree, PhyloTree, ClusterTree
from main import TreeStyle, save
from qt4_render import _TreeScene, render, get_tree_img_map
from templates import _DEFAULT_STYLE, apply_template


__all__ = ["show_tree", "render_tree"]

_QApp = None

def init_scene(t, layout, ts):
    global _QApp

    if not ts:
        ts = TreeStyle()

    if layout and not ts.layout_fn: 
        ts.layout_fn  = layout
    elif not layout and not ts.layout_fn:
        cl = t.__class__
        try:
            ts_template = _DEFAULT_STYLE[cl]
        except KeyError, e:
            pass
        else:
            apply_template(ts, ts_template)

    if not _QApp:
        _QApp = QtGui.QApplication(["ETE"])

    scene  = _TreeScene()
    ts._scale = None
    return scene, ts

def show_tree(t, layout=None, tree_style=None):
    """ Interactively shows a tree."""
    scene, img = init_scene(t, layout, tree_style)
    tree_item, n2i, n2f = render(t, img)
    scene.init_data(t, img, n2i, n2f)

    tree_item.setParentItem(scene.master_item)
    scene.addItem(scene.master_item)
    
    mainapp = _GUI(scene)
    mainapp.show()
    _QApp.exec_()

def render_tree(t, imgName, w=None, h=None, layout=None, \
                    tree_style = None, header=None, units="px"):
    """ Render tree image into a file."""
    scene, img = init_scene(t, layout, tree_style)
    tree_item, n2i, n2f = render(t, img)

    scene.init_data(t, img, n2i, n2f)
    tree_item.setParentItem(scene.master_item)
    scene.master_item.setPos(0,0)
    scene.addItem(scene.master_item)
    save(scene, imgName, w=w, h=h, units=units)
    imgmap = get_tree_img_map(n2i)

    return imgmap
    


