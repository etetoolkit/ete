import types

from PyQt4  import QtGui
from qt4_gui import _GUI, _PropertiesDialog

import layouts
from ete_dev import Tree, PhyloTree, ClusterTree
from main import TreeImage
from qt4_render import _TreeScene, render

__all__ = ["show_tree", "render_tree"]

_QApp = None

def init_scene(t, layout, img):
    global _QApp

    if not img:
        img = TreeImage()

    if not layout and not img.layout_fn:
        if t.__class__ == PhyloTree:
            layout  = "phylogeny"
        elif t.__class__ == ClusterTree:
            layout = "large"
        else:
            layout = "basic"
    elif not layout:
        layout = img.layout_fn

    # Validates layout function
    if type(layout) == types.FunctionType or\
            type(layout) == types.MethodType:
        img._layout_fn = layout
    else:
        try:
            img._layout_fn = getattr(layouts, img.layout_fn)
        except Exception:
            raise ValueError ("Required layout is not a function pointer nor a valid layout name.")

    if not _QApp:
        _QApp = QtGui.QApplication(["ETE"])

    scene  = _TreeScene()
    #scene.setBspTreeDepth(24)
    return scene, img

def show_tree(t, layout=None, img_properties=None):
    """ Interactively shows a tree."""
    scene, img = init_scene(t, layout, img_properties)
    tree_item, n2i, n2f = render(t, img)
    scene.init_data(t, img, n2i, n2f)

    tree_item.setParentItem(scene.master_item)
    scene.addItem(scene.master_item)
    mainapp = _GUI(scene)
    mainapp.show()
    _QApp.exec_()

def render_tree(t, imgName, w=None, h=None, layout=None, \
                    img_properties = None, header=None):
    """ Render tree image into a file."""
    scene, img_prop = init_scene(t, layout, img_properties)

    scene.save(imgName, w=w, h=h, header=header)
    return imgmap   

