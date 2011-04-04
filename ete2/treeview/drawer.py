import types

from PyQt4  import QtGui
from qt4_gui import _GUI, _PropertiesDialog, _BasicNodeActions

import layouts
from ete_dev import Tree, PhyloTree, ClusterTree
from main import TreeStyle, save
from qt4_render import _TreeScene, render, get_tree_img_map

__all__ = ["show_tree", "render_tree"]

_QApp = None

def init_scene(t, layout, img):
    global _QApp

    if not img:
        img = TreeStyle()

    # if not layout and not img.layout_fn:
    #     if t.__class__ == PhyloTree:
    #         layout  = "phylogeny"
    #     elif t.__class__ == ClusterTree:
    #         layout = "large"
    #     else:
    #         layout = "basic"
        
    #     img._layout_handler = layout

    if not _QApp:
        _QApp = QtGui.QApplication(["ETE"])

    scene  = _TreeScene()
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
    scene, img = init_scene(t, layout, img_properties)
    tree_item, n2i, n2f = render(t, img)

    scene.init_data(t, img, n2i, n2f)
    tree_item.setParentItem(scene.master_item)
    scene.master_item.setPos(0,0)
    scene.addItem(scene.master_item)
    save(scene, imgName, w, h)
    imgmap = get_tree_img_map(n2i)

    return imgmap
    


