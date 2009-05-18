import sys
import time
import re
import math
import random   
import types
import copy
import string 

import numpy
from PyQt4  import QtCore
from PyQt4  import QtGui 
from PyQt4.QtGui import QPrinter

from pygenomics.coretype import tree
DEBUG = 1

import layouts 
import __mainwindow__

__all__ = ["show_tree", "render_tree", "TreeImageProperties"]
_QApp = None

_MIN_NODE_STYLE = {
"fgcolor":        "#FFAA55",
"bgcolor":       "#FFFFFF",
"vt_line_color":    "#000000",
"hz_line_color":    "#000000",
"line_type":     0,
"vlwidth":       1,
"hlwidth":       1,
"size":          4,
"shape":         "square",
"faces":         None, 
"draw_descendants": 1, 
}

def logger(level,*msg):
    """ Just to manage how to print messages """
    msg = map(str, msg)
    # critrical error
    if level == -1:
        print >>sys.stderr,"* Error:     ", " ".join(msg)
    # warning
    elif level == 0:
        print >>sys.stderr,"* Warning:   ", " ".join(msg)
    # info
    elif level == 1:
        print >>sys.stdout,"* Info:      ", " ".join(msg)
    # debug
    elif level == 2:
        if DEBUG == 1:
            print >>sys.stderr,"* Debug:     ", " ".join(msg)
    else:
        print >>sys.stderr,"* NoCategory:", " ".join(msg)
    return


def show_tree(t, style="basic"):
    """ Interactively shows a tree."""
    global _QApp
   
    if not _QApp:
        _QApp = QtGui.QApplication(["ETE"])

    scene  = _TreeScene()
    mainapp = _MainApp(scene)

    scene.initialize_tree_scene(t, style, None)
    scene.draw()

    mainapp.show()
    _QApp.exec_()
    
def render_tree(t, w, h, imgName, style="basic"):
    """ Render tree image into a PNG file."""
    global _QApp
    if not _QApp:
        _QApp = QtGui.QApplication(["ETE"])

    scene  = _TreeScene()
    scene.initialize_tree_scene(t, style, None)
    scene.draw()
    scene.save(w, h, imgName)

class TreeImageProperties:
    def __init__(self):
        self.branch_pixels_correction   = 0
        self.force_topology             = False
        self.draw_branch_length         = False
        self.align_leaf_faces           = False
        self.orientation                = 0
        self.style                      = 0
        self.general_font_type          = "Verdana"
        self.branch_length_font_color   = "#222"
        self.branch_length_font_size    = 6
        self.branch_support_font_color  = "red"
        self.branch_support_font_size   = 9 
        self.tree_width                 = 200
	self.min_branch_separation      = 1

# #################
# NON PUBLIC STUFF
# #################

class _MainApp(QtGui.QMainWindow):
    def __init__(self,scene,*args):
        QtGui.QMainWindow.__init__(self, *args)
	self.scene = scene
	self.view  = _MainView(scene)
	scene.view = self.view 
	__mainwindow__.Ui_MainWindow().setupUi(self)
        scene.view = self.view
        self.view.centerOn(0,0)
        splitter = QtGui.QSplitter()
        splitter.addWidget(self.view)
        splitter.addWidget(scene.propertiesTable)
        self.setCentralWidget(splitter)

    @QtCore.pyqtSignature("")
    def on_actionETE_triggered(self):

	QtGui.QMessageBox.information(self, "About ETE",\
                           "Environment for Tree Exploration.\nby Jaime Huerta-Cepas\n%s\n" % __version__)

    @QtCore.pyqtSignature("")
    def on_actionZoomOut_triggered(self):
	self.view.scale(0.8,0.8)

    @QtCore.pyqtSignature("")
    def on_actionZoomIn_triggered(self):
	if self.scene.highlighter.isVisible():
	    R = self.scene.highlighter.rect()
	else:
	    R = self.scene.selector.rect()
	if R.width()>0 or R.height()>0:
	    self.view.fitInView(R.x(),R.y(),R.width(),\
				    R.height(),QtCore.Qt.KeepAspectRatio)
	else:
	    self.view.scale(1.2,1.2)

    @QtCore.pyqtSignature("")
    def on_actionKK_triggered(self):
	self.scene.props.draw_branch_length ^= True
	self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionBranchLength_triggered(self):
	self.scene.props.draw_branch_length ^= True
	self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionForceTopology_triggered(self):
	#pixels, ok = QtGui.QInputDialog.getInteger(None,"Force branch length","Number of extra pixels:",0,0,100)
	#if ok:
	self.scene.props.force_topology ^= True
	self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionChange_orientation_triggered(self):
	self.scene.props.orientation ^= 1
	self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionShow_phenogram_triggered(self):
	self.scene.props.style = 0
	self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionShowCladogram_triggered(self):
	self.scene.props.style = 1
	self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionOpen_triggered(self):
	F = QtGui.QFileDialog(self)
	if F.exec_():
	    try:
		t = tree.Tree(str(F.selectedFiles()[0]))
	    except Exception,e:
		pass
	    else:
		self.scene.initialize_tree_scene(t,"basic",None)
		self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionSave_newick_triggered(self):
	F = QtGui.QFileDialog(self)
	if F.exec_():
	    try:
		fname = F.selectedFiles()[0]
		nw = self.scene.startNode.get_newick()
		OUT = open(fname,"w")
	    except Exception,e:
		print e
	    else:
		OUT.write(nw)
		OUT.close()

    @QtCore.pyqtSignature("")
    def on_actionSave_image_triggered(self):
	F = QtGui.QFileDialog(self)
	if F.exec_():
	    imgName = str(F.selectedFiles()[0])
	    self.scene.save(500,500,imgName)

    @QtCore.pyqtSignature("")
    def on_actionSave_region_triggered(self):
	dim = self.scene.selector.rect()
	if (dim.height() * dim.width() )*4 / 1024 / 1024 > 1000: 
	    print "Image too large"
	    return
	F = QtGui.QFileDialog(self)
	if F.exec_():
	    imgName = str(F.selectedFiles()[0])
	    self.scene.save(imgName, self.scene.selector.rect() )

    def on_actionPaste_newick_triggered(self):
        text,ok = QtGui.QInputDialog.getText(self,\
						 "Paste Newick",\
						 "Newick:")
	if ok:
	    try:
		t = readNewick.read_newick_string(str(text))
	    except Exception,e:
		pass
	    else:
		self.scene.initialize_tree_scene(t,"basic",None)
		self.scene.draw()

	
class _TableItem(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)
	self.propdialog = parent

    def paint(self, painter, option, index):
        QtGui.QItemDelegate.paint(self, painter, option, index)
        
    def createEditor(self, parent, option, index):
        # Edit only values, not property names
        if index.column() != 1:
            logger(2, "NOT EDITABLE COLUMN")
            return None
            
        originalValue = index.model().data(index)
        if not self.isSupportedType(originalValue.type()):
            logger(2, "data type not suppoerted for editting")
            return None

	if re.search("^#[0-9ABCDEFabcdef]{6}$",str(originalValue.toString())):
	    origc = QtGui.QColor(str(originalValue.toString()))
	    color = QtGui.QColorDialog.getColor(origc)
	    if color.isValid():
		self.propdialog._edited_indexes.add( (index.row(), index.column()) )
		index.model().setData(index,QtCore.QVariant(color.name()))
		self.propdialog.apply_changes()
		
	    return None
	else:
      	    editField = QtGui.QLineEdit(parent)
	    editField.setFrame(False)
	    validator = QtGui.QRegExpValidator(QtCore.QRegExp(".+"), editField)
	    editField.setValidator(validator)
	    self.connect(editField, QtCore.SIGNAL("returnPressed()"),
			 self.commitAndCloseEditor)
	    self.connect(editField, QtCore.SIGNAL("returnPressed()"),
			 self.propdialog.apply_changes)
	    self.propdialog._edited_indexes.add( (index.row(), index.column()) )
	    return editField

    def setEditorData(self, editor, index):
        value = index.model().data(index)
        if editor is not None:
            editor.setText(self.displayText(value))
       
    def isSupportedType(valueType):
        return True

    isSupportedType = staticmethod(isSupportedType)
    def displayText(self,value):
        return value.toString()
    
    def commitAndCloseEditor(self):
        editor = self.sender()
        self.emit(QtCore.SIGNAL("commitData(QWidget *)"), editor)
        self.emit(QtCore.SIGNAL("closeEditor(QWidget *)"), editor)

class _PropModeChooser(QtGui.QWidget):
    def __init__(self,scene, *args):
        QtGui.QWidget.__init__(self,*args)

class _PropertiesDialog(QtGui.QWidget):
    def __init__(self,scene, *args):
        QtGui.QWidget.__init__(self,*args)
        self.scene = scene
	self._mode = 0
        self.layout =  QtGui.QVBoxLayout()
        self.tableView = QtGui.QTableView()
	self.tableView.setVerticalHeader(None)
        self.layout.addWidget(self.tableView)
        self.setLayout(self.layout)

    def update_properties(self, node):
	self.node = node
	self._edited_indexes =  set([])
	self._style_indexes = set([])
	self._prop_indexes = set([])

        self.get_prop_table(node)

    def get_props_in_nodes(self, nodes):
        # sorts properties and faces of selected nodes
        self.prop2nodes = {}
        self.prop2values = {}
        self.style2nodes = {}
        self.style2values = {}

        for n in nodes:
            for pname in n.features:
                pvalue = getattr(n,pname)
                if type(pvalue) == int or \
                   type(pvalue) == float or \
                   type(pvalue) == str :
                    self.prop2nodes.setdefault(pname,[]).append(n)
                    self.prop2values.setdefault(pname,[]).append(pvalue)

            for pname,pvalue in n.img_style.iteritems():
                if type(pvalue) == int or \
                   type(pvalue) == float or \
                   type(pvalue) == str :
                    self.style2nodes.setdefault(pname,[]).append(n)
                    self.style2values.setdefault(pname,[]).append(pvalue)

    def get_prop_table(self, node):
	if self._mode == 0: # node
	    self.get_props_in_nodes([node])
	elif self._mode == 1: # childs
	    self.get_props_in_nodes(node.get_leaves())
	elif self._mode == 2: # partition
	    self.get_props_in_nodes([node]+node.get_descendants())

	total_props = len(self.prop2nodes) + len(self.style2nodes.keys())
        self.model = QtGui.QStandardItemModel(total_props, 2)
        # self.tableView = QtGui.QTableView()
        self.tableView.setModel(self.model)
        self.delegate = _TableItem(self)
        self.tableView.setItemDelegate(self.delegate)

        row = 0
        for name,nodes in self.prop2nodes.iteritems():
            value= getattr(nodes[0],name)

            index1 = self.model.index(row, 0, QtCore.QModelIndex())
            index2 = self.model.index(row, 1, QtCore.QModelIndex())

            self.model.setData(index1, QtCore.QVariant(name))
            v = QtCore.QVariant(value)
            self.model.setData(index2, v)

	    self._prop_indexes.add( (index1, index2) )
            row +=1

        for name in self.style2nodes.iterkeys():
            value= self.style2values[name][0]

            index1 = self.model.index(row, 0, QtCore.QModelIndex())
            index2 = self.model.index(row, 1, QtCore.QModelIndex())

            self.model.setData(index1, QtCore.QVariant(name))
            v = QtCore.QVariant(value)
            self.model.setData(index2, v)
            # Creates a variant element
	    self._style_indexes.add( (index1, index2) )
            row +=1
        return 

    def apply_changes(self):
	# Apply changes on styles
	for i1, i2 in self._style_indexes:
	    if (i2.row(), i2.column()) not in self._edited_indexes: 
		continue
	    name = str(self.model.data(i1).toString())
	    value = str(self.model.data(i2).toString())
	    for n in self.style2nodes[name]:
		typedvalue = type(n.img_style[name])(value)
		try:
		    n.img_style[name] = typedvalue
		except:
		    logger(-1, "Wrong format for attribute:", name)
		    break

	# Apply changes on properties
	for i1, i2 in self._prop_indexes:
	    if (i2.row(), i2.column()) not in self._edited_indexes: 
		continue
	    name = str(self.model.data(i1).toString())
	    value = str(self.model.data(i2).toString())
	    for n in self.prop2nodes[name]:
		typedvalue = type(getattr(n,name))(value)
		try:
		    print "CHANGE", name
		    n.set_property(name,type(getattr(n,name))(value))
		except:
		    logger(-1, "Wrong format for attribute:", name)
		    break
	self.update_properties(self.node)
        self.scene.draw()
        return

class _TextItem(QtGui.QGraphicsSimpleTextItem):
    """ Manage faces on Scene"""
    def __init__(self,face,node,*args):
        QtGui.QGraphicsSimpleTextItem.__init__(self,*args)
        self.node = node
        self.face = face

    def hoverEnterEvent (self,e):
#	if self.scene().selector.isVisible():
#	    self.scene().mouseMoveEvent(e)

	R = self.node.fullRegion.getRect()
	if self.scene().props.orientation == 0:
	    width = self.scene().i_width-self.node._x
	    self.scene().highlighter.setRect(QtCore.QRectF(self.node._x,self.node._y,width,R[3]))
	elif self.scene().props.orientation == 1:
	    width = self.node._x-self.scene().i_width
	    self.scene().highlighter.setRect(QtCore.QRectF(width,self.node._y,width,R[3]))
	self.scene().highlighter.setVisible(True)

    def hoverLeaveEvent (self,e):
	self.scene().highlighter.setVisible(False)

    def mousePressEvent(self,e):
	pass

    def mouseReleaseEvent(self,e):
        logger(2,"released in scene", e.button)
        if e.button() == QtCore.Qt.RightButton:
            self.node._QtItem_.showActionPopup()
        elif e.button() == QtCore.Qt.LeftButton:
	    self.scene().propertiesTable.update_properties(self.node)


class _FaceItem(QtGui.QGraphicsPixmapItem):
    """ Manage faces on Scene"""
    def __init__(self,face,node,*args):
        QtGui.QGraphicsPixmapItem.__init__(self,*args)
        self.node = node
        self.face = face

    def hoverEnterEvent (self,e):
#	if self.scene().selector.isVisible():
#	    self.scene().mouseMoveEvent(e)

	R = self.node.fullRegion.getRect()
	if self.scene().props.orientation == 0:
	    width = self.scene().i_width-self.node._x
	    self.scene().highlighter.setRect(QtCore.QRectF(self.node._x,self.node._y,width,R[3]))
	elif self.scene().props.orientation == 1:
	    width = self.node._x-self.scene().i_width
	    self.scene().highlighter.setRect(QtCore.QRectF(width,self.node._y,width,R[3]))
	self.scene().highlighter.setVisible(True)

    def hoverLeaveEvent (self,e):
	self.scene().highlighter.setVisible(False)

    def mousePressEvent(self,e):
	pass

    def mouseReleaseEvent(self,e):
        logger(2,"released in scene", e.button)
        if e.button() == QtCore.Qt.RightButton:
            self.node._QtItem_.showActionPopup()
        elif e.button() == QtCore.Qt.LeftButton:
	    self.scene().propertiesTable.update_properties(self.node)


class _NodeItem(QtGui.QGraphicsRectItem):
    def __init__(self,node):
        self.node = node
        self.radius = node.img_style["size"]/2
        QtGui.QGraphicsRectItem.__init__(self,0,0,self.radius*2,self.radius*2)

    def paint(self, p, option, widget):
	if self.node.img_style["shape"] == "sphere":
	    r = self.radius
	    gradient = QtGui.QRadialGradient(r, r, r,(r*2)/3,(r*2)/3)
	    gradient.setColorAt(0.05, QtCore.Qt.white);
	    gradient.setColorAt(0.9, QtGui.QColor(self.node.img_style["fgcolor"]));
	    p.setBrush(QtGui.QBrush(gradient))
	    p.setPen(QtCore.Qt.NoPen)
	    p.drawEllipse(self.rect())
	elif self.node.img_style["shape"] == "square":
	    p.fillRect(self.rect(),QtGui.QBrush(QtGui.QColor(self.node.img_style["fgcolor"])))

    def hoverEnterEvent (self,e):
	R = self.node.fullRegion.getRect()
	if self.scene().props.orientation == 0:
	    width = self.scene().i_width-self.node._x
	    self.scene().highlighter.setRect(QtCore.QRectF(self.node._x,self.node._y,width,R[3]))
	elif self.scene().props.orientation == 1:
	    width = self.node._x-self.scene().i_width
	    self.scene().highlighter.setRect(QtCore.QRectF(width,self.node._y,width,R[3]))
	self.scene().highlighter.setVisible(True)
        
    def hoverLeaveEvent (self,e):
	self.scene().highlighter.setVisible(False)

    def mousePressEvent(self,e):
        logger(2,"Pressed in scene", e.button)

    def mouseReleaseEvent(self,e):
        logger(2,"released in scene", e.button)
        if e.button() == QtCore.Qt.RightButton:
            self.showActionPopup()
        elif e.button() == QtCore.Qt.LeftButton:
	    self.scene().propertiesTable.update_properties(self.node)

    def showActionPopup(self):
        contextMenu = QtGui.QMenu()
        if self.node.collapsed:
            contextMenu.addAction( "Expand"           , self.toggle_collapse)
        else:
            contextMenu.addAction( "Collapse"         , self.toggle_collapse)
        contextMenu.addAction( "Set as outgroup"      , self.set_as_outgroup)
        contextMenu.addAction( "Swap branches"        , self.node.swap_childs)
        contextMenu.addAction( "Delete node"          , self.node.delete)
        contextMenu.addAction( "Delete partition"     , self.node.detach)
        contextMenu.addAction( "Add childs"           , self.add_childs)
        contextMenu.addAction( "Populate partition"   , self.populate_partition)

	if self.node.up is not None and\
		self.scene().startNode == self.node:
	    contextMenu.addAction( "Back to parent", self.back_to_parent_node)
	else:
	    contextMenu.addAction( "Extract"              , self.set_start_node)

        if self.scene().buffer_node:
            contextMenu.addAction( "Paste partition"  , self.paste_partition)
        contextMenu.addAction( "Cut partition"        , self.cut_partition)
        if contextMenu.exec_( QtGui.QCursor.pos() ):
	    self.scene().draw()

    def add_childs(self):
        n,ok = QtGui.QInputDialog.getInteger(None,"Add childs","Number of childs to add:",1,1)
        if ok:
            for i in xrange(n):
                ch = self.node.add_child()
            self.scene().set_style_from(self.scene().startNode,self.scene().layout_func)

    def void(self):
        logger(0,"Not implemented yet")
        return True

    def set_as_outgroup(self):
        self.scene().startNode.set_outgroup(self.node)
        self.scene().set_style_from(self.scene().startNode, self.scene().layout_func)
        
    def toggle_collapse(self):
        self.node.collapsed ^= True

    def cut_partition(self):
        self.scene().buffer_node = self.node
        self.node.detach()

    def paste_partition(self):
        if self.scene().buffer_node:
            print self.scene().buffer_node
            self.node.add_child(self.scene().buffer_node)
            self.scene().set_style_from(self.scene().startNode,self.scene().layout_func)
            self.scene().buffer_node= None

    def populate_partition(self):
        n,ok = QtGui.QInputDialog.getInteger(None,"Populate partition","Number of nodes to add:",2,1)
        if ok:
            self.node.populate(n)
            self.scene().set_style_from(self.scene().startNode,self.scene().layout_func)

    def set_start_node(self):
        self.scene().startNode = self.node

    def back_to_parent_node(self):
        self.scene().startNode = self.node.up


class _SelectorItem(QtGui.QGraphicsRectItem):
    def __init__(self):
        self.Color = QtGui.QColor("blue")
        self._active = False
        QtGui.QGraphicsRectItem.__init__(self,0,0,0,0)

    def paint(self, p, option, widget):
        p.setPen(self.Color)
        p.drawRect(self.rect().x(),self.rect().y(),self.rect().width(),self.rect().height())
        return
        # Draw info text   
        font = QtGui.QFont("Arial",13)
        text = "%d selected."  % len(self.get_selected_nodes())
        textR = QtGui.QFontMetrics(font).boundingRect(text)
        if  self.rect().width() > textR.width() and \
                self.rect().height() > textR.height()/2 and 0: # OJO !!!!
            p.setPen(QtGui.QPen(self.Color))
            p.setFont(QtGui.QFont("Arial",13))
            p.drawText(self.rect().bottomLeft().x(),self.rect().bottomLeft().y(),text)

    def get_selected_nodes(self):
        selPath = QtGui.QPainterPath()
        selPath.addRect(self.rect())
        self.scene().setSelectionArea(selPath)
        return [i.node for i in self.scene().selectedItems()]
   
    def setActive(self,bool):
        self._active = bool

    def isActive(self):
        return self._active


class _HighlighterItem(QtGui.QGraphicsRectItem):
    def __init__(self):
        self.Color = QtGui.QColor("red")
        self._active = False
        QtGui.QGraphicsRectItem.__init__(self,0,0,0,0)

    def paint(self, p, option, widget):
        p.setPen(self.Color)
        p.drawRect(self.rect().x(),self.rect().y(),self.rect().width(),self.rect().height())
        return



class _MainView(QtGui.QGraphicsView):
    def __init__(self,*args):
        QtGui.QGraphicsView.__init__(self,*args)

        #self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        self.setViewportUpdateMode(QtGui.QGraphicsView.SmartViewportUpdate)
        #self.setViewportUpdateMode(QtGui.QGraphicsView.MinimalViewportUpdate)
        self.setOptimizationFlag (QtGui.QGraphicsView.DontAdjustForAntialiasing)
        #self.setOptimizationFlag (QtGui.QGraphicsView.DontSavePainterState)

    def resizeEvent(self, e):
	QtGui.QGraphicsView.resizeEvent(self, e)
	logger(2, "RESIZE VIEW!!")
	self.scene().draw()
	self.update()

    def wheelEvent(self,e):
        factor =  (-e.delta() / 360.0) 
        # Ctrl+Shift -> Zoom in X
        if  (e.modifiers() & QtCore.Qt.ControlModifier) and (e.modifiers() & QtCore.Qt.ShiftModifier):
            self.scale(1+factor,1)
        # Ctrl+Alt -> Zomm in Y 
        elif  (e.modifiers() & QtCore.Qt.ControlModifier) and (e.modifiers() & QtCore.Qt.AltModifier):
            self.scale(1,1+factor)
        # Ctrl -> Zoom X,Y
        elif e.modifiers() & QtCore.Qt.ControlModifier:
            s_pos = self.mapToScene(e.pos().x(), e.pos().y())
            self.scale(1-factor,1-factor)
            self.centerOn(e.pos().x()*(1-factor), e.pos().y()*(1-factor))

        # Shift -> Horizontal scroll
        elif e.modifiers() &  QtCore.Qt.ShiftModifier:
            if e.delta()>0:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()-20 )
            else:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()+20 )
        # No modifiers ->  Vertival scroll
        else:
            if e.delta()>0:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value()-20 )
            else:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value()+20 )

    def keyPressEvent(self,e):
        key = e.key()
        logger(2, "****** Pressed key: ", key, QtCore.Qt.LeftArrow)
        if key == 90: # z
            R = self.scene().selector.rect()
            if R.width()>0 or R.height()>0:
                self.fitInView(R.x(),R.y(),R.width(),R.height(),QtCore.Qt.KeepAspectRatio)
            else:
                self.scale(1.2,1.2)
        elif key == 73: # I
            self.scene().props.orientation ^= 1
            self.scene().draw()
        elif key == 49: # 1
            self.scene().props.style ^= 1
            self.scene().draw()

        elif key == 65: # 1
            self.scene().props.align_leaf_faces ^= 1
            self.scene().draw()

        elif key == 83 and (e.modifiers() & QtCore.Qt.ControlModifier): # Ctrl+S
            text,ok = QtGui.QInputDialog.getText(None,"Search","Search for leaf name:")
            if ok:
                for l in self.scene().startNode.get_leaves():
                    t = text.toStdString()

                    if re.search(t,l.name):
                        self.horizontalScrollBar().setValue(l._x)
                        self.verticalScrollBar().setValue(l._y)

        elif key == 68: # d
            self.scene().props.draw_branch_length ^= 1
            self.scene().draw()

        elif key == 88: # x
            self.scale(0.8,0.8)

        elif key  == QtCore.Qt.Key_Left:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()-20 )
            self.update()
        elif key  == QtCore.Qt.Key_Right:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()+20 )
            self.update()
        elif key  == QtCore.Qt.Key_Up:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value()-20 )
            self.update()
        elif key  == QtCore.Qt.Key_Down:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value()+20 )
            self.update()
        QtGui.QGraphicsView.keyPressEvent(self,e)

class _TreeScene(QtGui.QGraphicsScene):
    def __init__(self, rootnode=None, style=None, properties=None, *args):
        QtGui.QGraphicsScene.__init__(self,*args)

	self.view = None
	# Config variables
        self.buffer_node = None        # Used to copy and paste
        self.layout_func = None        # Layout function
        self.startNode   = rootnode    # Node to start drawing
	self.scale       = 0           # Tree branch scale used to draw
        self.max_w_aligned_face = 0    # Stores the max width of aligned faces 

	# Qt items
	self.selector = None 
        self.mainItem = None        # Qt Item which is parent of all other items
        self.propertiesTable = _PropertiesDialog(self)

    def initialize_tree_scene(self, tree, style, properties):
        self.tree        = tree        # Pointer to original tree
        self.startNode   = tree        # Node to start drawing

        # Load image attributes
        if not properties:
            self.props = TreeImageProperties()
        else:
            self.props = properties
	    
	# Validates layout function 
        if type(style) == types.FunctionType or\
                type(style) == types.MethodType:
            self.layout_func = style
        else:
            try:
                self.layout_func = getattr(layouts,style)
            except: 
               raise ValueError, "Required layout is not a function pointer nor a valid layout name."

	# Set the scene background 
        self.setBackgroundBrush(QtGui.QColor("white"))
        
	# Set nodes style
        self.set_style_from(self.startNode,self.layout_func)

	self.propertiesTable.update_properties(self.startNode)

    def mousePressEvent(self,e):
        logger(2, "Press en view")
        self.selector.setRect(e.scenePos().x(),e.scenePos().y(),0,0)
        self.selector.startPoint = QtCore.QPointF(e.scenePos().x(),e.scenePos().y())
        self.selector.setActive(True)
        self.selector.setVisible(True)
        QtGui.QGraphicsScene.mousePressEvent(self,e)

    def mouseReleaseEvent(self,e):
        logger(2, "Release en view")
        curr_pos = e.scenePos()
        x = min(self.selector.startPoint.x(),curr_pos.x())
        y = min(self.selector.startPoint.y(),curr_pos.y())
        w = max(self.selector.startPoint.x(),curr_pos.x()) - x
        h = max(self.selector.startPoint.y(),curr_pos.y()) - y
        if self.selector.startPoint == curr_pos:
            self.selector.setVisible(False)
        else:
            logger(2, self.selector.get_selected_nodes())
        self.selector.setActive(False)
        QtGui.QGraphicsScene.mouseReleaseEvent(self,e)

    def mouseMoveEvent(self,e):

        curr_pos = e.scenePos()
        if self.selector.isActive():
            x = min(self.selector.startPoint.x(),curr_pos.x())
            y = min(self.selector.startPoint.y(),curr_pos.y())
            w = max(self.selector.startPoint.x(),curr_pos.x()) - x
            h = max(self.selector.startPoint.y(),curr_pos.y()) - y
            self.selector.setRect(x,y,w,h)
	QtGui.QGraphicsScene.mouseMoveEvent(self, e)

    def mouseDoubleClickEvent(self,e):
        logger(2, "Double click")
        QtGui.QGraphicsScene.mouseDoubleClickEvent(self,e)

    def save(self, w, h, imgName):
	ext = imgName.split(".")[-1].upper()
	if ext == "PDF" or ext == "PS":
	    format = QPrinter.PostScriptFormat if ext == "PS" else QPrinter.PdfFormat
	    printer = QPrinter() 
	    printer.setResolution(100)
	    printer.setOutputFormat(format)
	    printer.setPageSize(QPrinter.A4)
	    
	    pageTopLeft = printer.pageRect().topLeft()
	    paperTopLeft = printer.paperRect().topLeft()

	    # print paperTopLeft.x(), paperTopLeft.y()    
	    # print pageTopLeft.x(), pageTopLeft.y()
	    # print  printer.paperRect().height(),  printer.pageRect().height()
	    topleft =  pageTopLeft - paperTopLeft
	    targetRect =  QtCore.QRectF(topleft.x(), topleft.y()*2, w, h)

	    printer.setFullPage(True);
	    printer.setOutputFileName(imgName);
	    pp = QtGui.QPainter(printer)
	    self.render(pp, targetRect, self.sceneRect())
	    pp.end()
	    return 
	else: 
	    targetRect = QtCore.QRectF(0, 0, w, h)
	    ii= QtGui.QImage(w, \
				 h, \
				 QtGui.QImage.Format_ARGB32)
	    pp = QtGui.QPainter(ii)

	    pp.setRenderHint(QtGui.QPainter.Antialiasing )
	    pp.setRenderHint(QtGui.QPainter.TextAntialiasing)
	    pp.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
	    self.render(pp, targetRect, self.sceneRect())
	    pp.end()
	    ii.save(imgName)


    def save_by_chunks(self,imgName="img.out",rect=None):
	max_width = 10000
	max_height = 10000
	if imgName.endswith(".png"):
	    imgName = ''.join(imgName.split('.')[:-1])

	if rect is None:
	    rect = self.sceneRect()

	width = int(rect.width())
	height = int(rect.height())
	
	start_x = 0
	missing_width = width
	counter_column = 1
	for w in xrange(start_x, width, max_width):
	    start_y = 0
	    missing_height = height
	    counter_row = 1
	    for h in xrange(start_y, height, max_height):
		chunk_width = min( missing_width, max_width )
		chunk_height = min( missing_height, max_height )
		temp_rect = QtCore.QRectF( rect.x()+w, \
					rect.y()+h, 
					chunk_width, \
					chunk_height    )
	        if chunk_height<=0 or chunk_width <=0: 
		    break
		ii= QtGui.QImage(chunk_width, \
				     chunk_height, \
				     QtGui.QImage.Format_RGB32)
		pp = QtGui.QPainter(ii)
		targetRect = QtCore.QRectF(0, 0, temp_rect.width(), temp_rect.height())
		self.render(pp, targetRect, temp_rect)
		ii.saves("%s-%s_%s.png" %(imgName,counter_row,counter_column))
		print "Created: %s-%s_%s.png" %(imgName,counter_row,counter_column)
		counter_row += 1
		
		missing_height -= chunk_height
		pp.end()
	    counter_column += 1
	    missing_width -= chunk_width

    def draw(self):
        # Clean previous items from scene by removing the main parent
        if self.mainItem:
            self.removeItem(self.mainItem)
	    
	# Recreates main parent and add it to scene
        self.mainItem = QtGui.QGraphicsRectItem()
	self.addItem(self.mainItem)
	# Recreates selector item (used to zoom etc...)
        self.selector   = _SelectorItem()
        self.selector.setParentItem(self.mainItem)
        self.selector.setVisible(True)
        self.selector.setZValue(2)

        self.highlighter   = _HighlighterItem()
        self.highlighter.setParentItem(self.mainItem)
        self.highlighter.setVisible(True)
        self.highlighter.setZValue(2)

	# Get branch scale
	fnode, max_dist = self.startNode.get_farthest_leaf(\
	    topology_only=self.props.force_topology)

	if max_dist>0:
	    self.scale =  self.props.tree_width / max_dist
	else:
	    self.scale =  1

        # Updates all nodes regions and their faces
        t1 = time.time()
        self.update_node_areas(self.startNode)
        logger(2, "Ellapsed time for updating node areas:",time.time()-t1)
        # Get picture dimensions
        self.i_width  = self.startNode.fullRegion.width() 
        self.i_height = self.startNode.fullRegion.height()


	# Adjust tree to window?
	if self.view is not None and 0:
	    cwidth = self.view.width()
	    fixwidth = self.i_width + self.max_w_aligned_face - (self.scale * max_dist)
	    print fixwidth, self.view.width()
	    if cwidth > fixwidth:
		self.scale =  (cwidth - fixwidth) / max_dist 
		# Load nodes regions and update their face pixmaps
		t1 = time.time()
		self.update_node_areas(self.startNode)
		logger(2, "Ellapsed time for updating node areas:",time.time()-t1)
		# Get picture dimensions
		self.i_width  = self.startNode.fullRegion.width() + self.max_w_aligned_face
		self.i_height = self.startNode.fullRegion.height()

	mem_size = ((self.i_width*self.i_height*4)/1024)/1024
        logger(1, "IMAGE dimension=",self.i_width,"x",self.i_height,"~mem cosumption: %0.2f Mb" %mem_size)
        # Render tree on scene
        t2 = time.time()
        self.render_node(self.startNode,0,0)
        logger(2, "Time for rendering", time.time()-t2)


        # size correcton for aligned faces
        self.i_width += self.max_w_aligned_face
	print self.max_w_aligned_face
        # New pos for tree when inverse orientation
        if self.props.orientation == 1:
            self.startNode._QtItem_.moveBy(self.max_w_aligned_face,0)

        # Tree border
        #border = self.addRect(0,0,self.i_width, self.i_height)
        #border = self.addRect(0,0,self.i_width-self.max_w_aligned_face,self.i_height)  
	#border = self.addRect(0,0, self.sceneRect().width(), self.sceneRect().height())
        #border.setParentItem(self.mainItem)
	self.add_scale(1 ,self.i_height+4)

        self.setSceneRect(-2,-2,self.i_width+4,self.i_height+50)
        logger(2, "Number of items in scene:", len(self.items()))


    def add_scale(self,x,y):
	size = 50
	customPen  = QtGui.QPen(QtGui.QColor("black"),1)

        line = QtGui.QGraphicsLineItem(self.mainItem)
        line2 = QtGui.QGraphicsLineItem(self.mainItem)
        line3 = QtGui.QGraphicsLineItem(self.mainItem)
        line.setPen(customPen)
        line2.setPen(customPen)
        line3.setPen(customPen)

        line.setLine(x,y+20,size,y+20)
        line2.setLine(x,y+15,x,y+25)
        line3.setLine(size,y+15,size,y+25)

	scale_text = "%0.2f" % float(size/ self.scale)
	scale = QtGui.QGraphicsSimpleTextItem(scale_text)
	scale.setParentItem(self.mainItem)
	scale.setPos(x,y+20) 

	if self.props.force_topology:
	    wtext = "Force topology is enabled!\nBranch lengths does not represent original values." 
	    warning_text = QtGui.QGraphicsSimpleTextItem(wtext)
            warning_text.setFont( QtGui.QFont("Arial", 8))
	    warning_text.setBrush( QtGui.QBrush(QtGui.QColor("darkred")))
	    warning_text.setPos(x, y+32) 
	    warning_text.setParentItem(self.mainItem)

    def set_style_from(self,node,layout_func):
        for n in [node]+node.get_descendants():
	    n.img_style = copy.copy(_MIN_NODE_STYLE)
	    n.img_style["faces"] = []
            layout_func(n)
            
    def update_node_areas(self,node):
        """ This recursive function scans all nodes hunging from the given
        root node and calculates the coordinates and room necessary to
        draw a rectangular tree. IT reads the face content of each
        node, which ones have to be drawn, and how much room they
        use. """
        child_rects = []
        # First, go for childs
        if not node.is_leaf() and node.img_style["draw_descendants"]==1:
            for ch in node.children:
                # Recursivity 
                rect = self.update_node_areas(ch)
                child_rects.append(rect)
            
        # This is the node region covered by column faces and the
        # horizontal line drawn using the branch length and scale.

	if self.props.force_topology:
	    node.dist_xoffset = self.scale
	else:
	    node.dist_xoffset = float(node.dist * self.scale) 

        min_node_height = max(node.img_style["size"], node.img_style["hlwidth"]*2) 
        max_w         = 0
        max_aligned_w = 0
        max_h         = 0
        # Each stack is drawn as a different column
        for stack in node.img_style["faces"]:
            stack_h = 0
            stack_w = 0
            aligned_f_w = 0
            aligned_f_h = 0
            for f in stack:
                # If pixmap face, updates image
                if f.type == "pixmap":
                    f.update_pixmap()
                    
                if node.is_leaf() and f.aligned:
		    print aligned_f_w
                    aligned_f_w = max(aligned_f_w, f._width())
                    aligned_f_h += f._height()
	    
                else:
                    stack_w = max(stack_w, f._width())
                    stack_h += f._height()

            max_aligned_w += aligned_f_w
            max_w += stack_w
            max_h = numpy.max([aligned_f_h,stack_h,max_h])

        # Updates the max width spend by aligned faces
        if max_aligned_w > self.max_w_aligned_face:
            self.max_w_aligned_face = max_aligned_w

            
        # Dist a and faces region
        node.facesRegion = QtCore.QRectF(0,0,max_w,max_h)
        w = node.dist_xoffset + max_w + node.img_style["size"] 
        h = max(max_h, min_node_height, self.props.min_branch_separation)
        node.nodeRegion = QtCore.QRectF(0,0,w,h)
        # This is the node region covered in total 
        sum_child_h = 0
        max_child_w = 0
        # Get width and height covered by childs
        for ch_r in child_rects:
            sum_child_h += ch_r.height()
            if ch_r.width()>max_child_w:
                max_child_w = ch_r.width()
        # takes max height: childs or faces
        if sum_child_h > h:
            h = sum_child_h
        w += max_child_w
        # Sets the total room needed for this node
        node.fullRegion = QtCore.QRectF(0,0,w,h)
        return node.fullRegion

    def rotate_node(self,node,angle,x=None,y=None):
        if x and y:
            x = node.fullRegion.width()/2
            y = node.fullRegion.height()/2
            node._QtItem_.setTransform(QtGui.QTransform().translate(x, y).rotate(angle).translate(-x, -y));
        else:
            node._QtItem_.rotate(angle)

    def render_node(self,node , x, y,level=0):
	""" Traverse the tree structure and render each node using the
	regions, sizes, and faces previously loaded. """

        # Node's stuff
        orientation = self.props.orientation
        r = node.img_style["size"]/2
        fh = node.facesRegion.width()

	node._QtItem_ = _NodeItem(node)
	node._QtItem_.setAcceptsHoverEvents(True)

        # RIGHT TO LEFT
        if orientation == 1:
            if node == self.startNode:
                x = self.i_width-x

        # Add main node QGItem. Each node item has as parent the
        # parent node item
        if node==self.startNode:
            node._QtItem_.setParentItem(self.mainItem)

        # node x,y starting positions
        node._x = x
        node._y = y

        # colour rect as node background 
        if  node.img_style["bgcolor"].upper() != "#FFFFFF":
            background = QtGui.QGraphicsRectItem(self.mainItem)
            background.setZValue(-1000+level)
            color = QtGui.QColor(node.img_style["bgcolor"])
            background.setBrush(color)
            background.setPen(color)
            if orientation == 0:
                background.setRect(node._x,node._y,self.i_width-node._x+self.max_w_aligned_face,node.fullRegion.height())
            elif orientation == 1:
                background.setRect(node._x-node.fullRegion.width(),node._y,self.i_width,node.fullRegion.height())
        # Draw node and lines
        if not node.is_leaf() and node.img_style["draw_descendants"]==1:
            # Corrections ... say something else, don't you think?
            node_height = 0    
            for ch in node.get_childs():
                node_height += ch.fullRegion.height()
            if node.fullRegion.height() >= node_height:
                y_correction = node.fullRegion.height() - node_height
            else:
                y_correction = 0

            # recursivity: call render function for every child
            next_y = y + y_correction/2
            for ch in node.get_childs():
                dist_to_child = ch.dist * self.scale
                if orientation == 0:
                    next_x = x+node.nodeRegion.width() 
                elif orientation == 1:
                    next_x = x-node.nodeRegion.width() 

                self.render_node(ch,next_x, next_y,level+1)
                next_y += ch.fullRegion.height()

            node._centered_y = (node.children[0]._centered_y + node.children[-1]._centered_y)/2
            # Draw an internal node. Take global pos. 

            # Place node at the correct pos in Scene
            ch._QtItem_.setParentItem(node._QtItem_)
            if orientation == 0:
                node._QtItem_.setPos(x+node.dist_xoffset,node._centered_y-node.img_style["size"]/2)
            elif orientation == 1:
                node._QtItem_.setPos(x-node.dist_xoffset-node.img_style["size"],node._centered_y-node.img_style["size"]/2)
            for ch in node.children:
                scene_pos = ch._QtItem_.pos()
                ch._QtItem_.setParentItem(node._QtItem_)
                ch._QtItem_.setPos(node._QtItem_.mapFromScene(scene_pos) )

	    # Draws the startNode branch when it is not the absolute root
	    if node == self.startNode:
		y = node._QtItem_.pos().y()+ node.img_style["size"]/2
		self.add_branch(self.mainItem,0,y,node.dist_xoffset,y,node.dist,node.support, node.img_style["hz_line_color"], node.img_style["hlwidth"], node.img_style["line_type"])

            # RECTANGULAR STYLE
            if self.props.style == 0:
                vt_line = QtGui.QGraphicsLineItem(node._QtItem_)
		customPen = QtGui.QPen(QtGui.QBrush(QtGui.QColor(node.img_style["vt_line_color"])), node.img_style["vlwidth"])
		if node.img_style["line_type"]==1:
		    customPen.setStyle(QtCore.Qt.DashLine)
                vt_line.setPen(customPen)

                ch1_y = node._QtItem_.mapFromScene(0,node.children[0]._centered_y).y()
                ch2_y = node._QtItem_.mapFromScene(0,node.children[-1]._centered_y).y()

                # Draw hz lines of childs
                for ch in node.children:
                    ch_pos = node._QtItem_.mapFromScene(ch._x, ch._centered_y)
                    if orientation == 0:
                        self.add_branch(node._QtItem_,fh+r*2,ch_pos.y(),fh+r*2+ch.dist_xoffset ,ch_pos.y(),ch.dist, ch.support, ch.img_style["hz_line_color"], ch.img_style["hlwidth"], ch.img_style["line_type"])
                    elif orientation == 1:
                        self.add_branch(node._QtItem_,-fh,ch_pos.y(),-fh-ch.dist_xoffset ,ch_pos.y(),ch.dist,ch.support,ch.img_style["hz_line_color"], ch.img_style["hlwidth"], ch.img_style["line_type"])
                # Draw vertical line
                if orientation == 0:
                    vt_line.setLine(fh+r*2,ch1_y,fh+(r*2),ch2_y)
                elif orientation == 1:
                    vt_line.setLine(-fh,ch1_y,-fh,ch2_y)

            # DIAGONAL STYLE
            elif self.props.style == 1:
                # Draw lines from node to childs
                for ch in node.children:
                    if orientation == 0:
                        ch_x = ch._QtItem_.x()
                        ch_y = ch._QtItem_.y()+ch.img_style["size"]/2
                        self.add_branch(node._QtItem_,fh+node.img_style["size"],r,ch_x,ch_y,ch.dist,ch.support, ch.img_style["hz_line_color"], 1, ch.img_style["line_type"])
                    elif orientation == 1:
                        ch_x = ch._QtItem_.x()
                        ch_y = ch._QtItem_.y()+ch.img_style["size"]/2
                        self.add_branch(node._QtItem_,-fh,r,ch_x+(r*2),ch_y,ch.dist,ch.support, ch.img_style["hz_line_color"], 1, ch.img_style["line_type"])
                   
            self.add_faces(node,orientation)

        else:
            # Draw terminal node
            node._centered_y = y+node.fullRegion.height()/2
            if orientation == 0:
                node._QtItem_.setPos(x+node.dist_xoffset, node._centered_y-r)
            elif orientation == 1:
                node._QtItem_.setPos(x-node.dist_xoffset-node.img_style["size"], node._centered_y-r)

            self.add_faces(node,orientation)

    def add_branch(self,parent_item,x1,y1,x2,y2,dist,support,color,width,line_type):
        hz_line = QtGui.QGraphicsLineItem(parent_item)
	customPen  = QtGui.QPen(QtGui.QBrush(QtGui.QColor(color)), width)
	if line_type == 1:
	    customPen.setStyle(QtCore.Qt.DashLine)
        hz_line.setPen(customPen)
        hz_line.setLine(x1,y1,x2,y2)

        if self.props.draw_branch_length:
            distText = "%0.3f" % dist
	    if support is not None:
		distText += "(%0.2f)" % support
            font = QtGui.QFont(self.props.general_font_type,self.props.branch_length_font_size)
            rect = QtGui.QFontMetrics(font).boundingRect(0,0,0,0,QtCore.Qt.AlignTop,distText)
            b_length = QtGui.QGraphicsSimpleTextItem(distText)	    
            b_length.setFont(font)
            b_length.setBrush(QtGui.QColor(self.props.branch_length_font_color))
            b_length.setParentItem(hz_line)
            b_length.setPos(x1,y1) 
            if y1 != y2:
                offset = 0
                angle = math.atan((y2-y1)/(x2-x1))*360/ (2*math.pi)
                if y1>y2:
                    offset = rect.height()
                b_length.setTransform(QtGui.QTransform().translate(0, y1-offset).rotate(angle).translate(0,-y1));

    def add_faces(self,node,orientation):
        # sphere radius
        r = node.img_style["size"]/2

        # ...
        if orientation==0:
            aligned_start_x = node._QtItem_.mapFromScene(self.i_width,0).x()
            start_x = node.img_style["size"]
        elif orientation==1:
            start_x = 0
            aligned_start_x = node._QtItem_.mapFromScene(0,0).x()

        
        for stack in node.img_style["faces"]:
            # get each stack's height and width
            stack_h         = 0
            stack_w         = 0
            aligned_stack_w = 0
            aligned_stack_h = 0
            # Extract height and width of al faces in this stack
            # Get max width and cumulated height
            for f in stack:
                if node.is_leaf() and f.aligned:
                    aligned_stack_w = max(aligned_stack_w , f._width())
                    aligned_stack_h += f._height()
                else:
                    stack_w = max(stack_w ,f._width() )
                    stack_h += f._height()

            # Creates a GGraphicsItem object for each face
            cumulated_y         = 0
            cumulated_aligned_y = 0
            for f in stack:
                # add each face of this stack into the correct position We
                # hace middle_y, so start_y is set to place face at such
                # middle_y possition.
                if node.is_leaf() and f.aligned:
                    start_y = cumulated_aligned_y + (-aligned_stack_h/2)+r
                else:
                    start_y = cumulated_y + (-stack_h/2)+r
                # If face is text type, add it as an QGraphicsTextItem
                if f.type == "text":
		    obj = _TextItem(f, node, f.get_text())
                    obj.setParentItem(node._QtItem_)
                    obj.setBrush(QtGui.QBrush(f.fgcolor))
                    obj.setFont(f.font)
		    obj.setAcceptsHoverEvents(True)
#		    start_y += f._height()
                else:
                    obj = _FaceItem(f,node,f.pixmap)
		    obj.setAcceptsHoverEvents(True)
                    obj.setParentItem(node._QtItem_)

                # If face is aligned and node is terminal, place face
                # at aligned margin
                if node.is_leaf() and f.aligned:
                    # Set face position
                    if orientation ==0:
                        obj.setPos(aligned_start_x, start_y)
                    elif orientation ==1:
                        obj.setPos(aligned_start_x-f._width(),start_y)
                    cumulated_aligned_y += f._height()
                # If face has to be draw within the node room 
                else:
                    # Set face position
                    if orientation ==0:
                        obj.setPos(start_x, start_y)
                    elif orientation ==1:
                        obj.setPos(start_x-f._width(),start_y)
                    cumulated_y += f._height()
                
            # next stack will start with this x_offset
            if orientation == 0:
                start_x += stack_w
                aligned_start_x += aligned_stack_w
            elif orientation ==1:
                start_x -= stack_w
                aligned_start_x -= aligned_start_x





__version__="1.0rev95"
__author__="Jaime Huerta-Cepas"
