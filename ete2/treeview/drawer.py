from __future__ import absolute_import
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
import types
import signal

from PyQt4  import QtGui
from PyQt4  import QtCore
from .qt4_gui import _GUI, _PropertiesDialog, _BasicNodeActions

from . import layouts
#from ete2 import Tree, PhyloTree, ClusterTree
from .main import save
from .qt4_render import _TreeScene, render, get_tree_img_map, init_tree_style

__all__ = ["show_tree", "render_tree"]

_QApp = None
GUI_TIMEOUT = None

def exit_gui(a,b):
    _QApp.exit(0)
    
def init_scene(t, layout, ts):
    global _QApp

    ts = init_tree_style(t, ts)
    if layout: 
        ts.layout_fn  = layout
        
    if not _QApp:
        _QApp = QtGui.QApplication(["ETE"])

    scene  = _TreeScene()
	#ts._scale = None
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
   
    _QApp.exec_()
    
def render_tree(t, imgName, w=None, h=None, layout=None, 
                tree_style = None, header=None, units="px",
                dpi=90):
    """ Render tree image into a file."""
    global _QApp
    for nid, n in enumerate(t.traverse("preorder")):
        n.add_feature("_nid", nid)
    scene, img = init_scene(t, layout, tree_style)
    tree_item, n2i, n2f = render(t, img)

    scene.init_values(t, img, n2i, n2f)
    tree_item.setParentItem(scene.master_item)
    scene.master_item.setPos(0,0)
    scene.addItem(scene.master_item)
    if imgName == "%%inline":
        imgmap = save(scene, imgName, w=w, h=h, units=units, dpi=dpi)
    else:
        x_scale, y_scale = save(scene, imgName, w=w, h=h, units=units, dpi=dpi)
        imgmap = get_tree_img_map(n2i, x_scale, y_scale)
    return imgmap
    

def get_img(t, w=None, h=None, layout=None, tree_style = None,
            header=None, units="px", dpi=90):
    global _QApp
    scene, img = init_scene(t, layout, tree_style)
    tree_item, n2i, n2f = render(t, img)
    scene.init_values(t, img, n2i, n2f)
    
    tree_item.setParentItem(scene.master_item)
    scene.master_item.setPos(0,0)
    scene.addItem(scene.master_item)
    x_scale, y_scale, imgdata = save(scene, "%%return", w=w, h=h, units=units, dpi=dpi)
    _QApp.quit()
    _QApp = None
    return imgdata, {}

 



