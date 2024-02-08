import re
import time

from ete4 import Tree
from ete4.treeview import TreeStyle

from .qt import *
from . import _mainwindow, _search_dialog, _show_newick, _open_newick, _about
from .main import save, _leaf
from ..utils import random_color
from .qt_render import render
from .node_gui_actions import NewickDialog


class _SelectorItem(QGraphicsRectItem):
    def __init__(self, parent=None):
        self.Color = QColor("blue")
        self._active = False
        QGraphicsRectItem.__init__(self, 0, 0, 0, 0)
        if parent:
            self.setParentItem(parent)

    def paint(self, p, option, widget):
        p.setPen(self.Color)
        p.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        p.drawRect(QRectF(self.rect().x(),self.rect().y(),self.rect().width(),self.rect().height()))
        return
        # Draw info text
        font = QFont("Arial", 13)
        text = "%d selected."  % len(self.get_selected_nodes())
        textR = QFontMetrics(font).boundingRect(text)
        if  self.rect().width() > textR.width() and \
                self.rect().height() > textR.height()/2 and 0: # OJO !!!!
            p.setPen(QPen(self.Color))
            p.setFont(QFont("Arial",13))
            p.drawText(self.rect().bottomLeft().x(),self.rect().bottomLeft().y(),text)

    def get_selected_nodes(self):
        selPath = QPainterPath()
        selPath.addRect(self.rect())
        self.scene().setSelectionArea(selPath)
        return [i.node for i in self.scene().selectedItems()]

    def setActive(self,bool):
        self._active = bool

    def isActive(self):
        return self._active

def etime(f):
    def a_wrapper_accepting_arguments(*args, **kargs):
        global TIME
        t1 = time.time()
        f(*args, **kargs)
        print(time.time() - t1)
    return a_wrapper_accepting_arguments

class _GUI(QMainWindow):
    def _updatestatus(self, msg):
        self.main.statusbar.showMessage(msg)

    def redraw(self):
        self.scene.draw()
        self.view.init_values()

    def __init__(self, scene, *args):
        QMainWindow.__init__(self, *args)
        self.main = _mainwindow.Ui_MainWindow()
        self.main.setupUi(self)
        self.setWindowTitle("ETE Tree Browser")

        self.scene = scene
        self.scene.GUI = self
        self.view = _TreeView(scene)
        scene.view = self.view
        self.node_properties = _PropertiesDialog(scene)
        self.view.prop_table = self.node_properties

        #self.view.centerOn(0,0)
        if scene.img.show_branch_length:
            self.main.actionBranchLength.setChecked(True)
        if scene.img.show_branch_support:
            self.main.actionBranchSupport.setChecked(True)
        if scene.img.show_leaf_name:
            self.main.actionLeafName.setChecked(True)
        if scene.img.force_topology:
            self.main.actionForceTopology.setChecked(True)

        splitter = QSplitter()
        splitter.addWidget(self.view)
        splitter.addWidget(self.node_properties)
        self.setCentralWidget(splitter)
        # I create a single dialog to keep the last search options
        self.searchDialog =  QDialog()
        # Don't know if this is the best way to set up the dialog and
        # its variables
        self.searchDialog._conf = _search_dialog.Ui_Dialog()
        self.searchDialog._conf.setupUi(self.searchDialog)

        self.scene.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)

        # Shows the whole tree by default
        #self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        splitter.setCollapsible(1, True)
        splitter.setSizes([int(self.scene.sceneRect().width()), 10])

        self.view.fitInView(0, 0, self.scene.sceneRect().width(), 200, Qt.AspectRatioMode.KeepAspectRatio)

    @QtCore.pyqtSlot()
    def on_actionETE_triggered(self):
        try:
            __version__
        except:
            __version__= "development branch"

        d = QDialog()
        d._conf = _about.Ui_About()
        d._conf.setupUi(d)
        d._conf.version.setText("Version: %s" %__version__)
        d._conf.version.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        d.exec()

    @QtCore.pyqtSlot()
    def on_actionZoomOut_triggered(self):
        self.view.safe_scale(0.8,0.8)

    @QtCore.pyqtSlot()
    def on_actionZoomIn_triggered(self):
        self.view.safe_scale(1.2,1.2)

    @QtCore.pyqtSlot()
    def on_actionZoomInX_triggered(self):
        self.scene.img._scale += self.scene.img._scale * 0.05
        self.redraw()

    @QtCore.pyqtSlot()
    def on_actionZoomOutX_triggered(self):
        self.scene.img._scale -= self.scene.img._scale * 0.05
        self.redraw()

    @QtCore.pyqtSlot()
    def on_actionZoomInY_triggered(self):
        self.scene.img.branch_vertical_margin += 5
        self.scene.img._scale = None
        self.redraw()

    @QtCore.pyqtSlot()
    def on_actionZoomOutY_triggered(self):
        if self.scene.img.branch_vertical_margin > 0:
            margin = self.scene.img.branch_vertical_margin - 5
            if margin > 0:
                self.scene.img.branch_vertical_margin = margin
            else:
                self.scene.img.branch_vertical_margin = 0.0
            self.scene.img._scale = None
            self.redraw()

    @QtCore.pyqtSlot()
    def on_actionFit2tree_triggered(self):
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    @QtCore.pyqtSlot()
    def on_actionFit2region_triggered(self):
        R = self.view.selector.rect()
        if R.width()>0 and R.height()>0:
            self.view.fitInView(R.x(), R.y(), R.width(),\
                                    R.height(), Qt.AspectRatioMode.KeepAspectRatio)

    @QtCore.pyqtSlot()
    def on_actionSearchNode_triggered(self):
        setup = self.searchDialog._conf
        setup.attrValue.setFocus()
        ok = self.searchDialog.exec()
        if ok:
            mType = setup.attrType.currentIndex()
            aName = str(setup.attrName.text())
            if mType >= 2 and mType <=6:
                try:
                    aValue =  float(setup.attrValue.text())
                except ValueError:
                    QMessageBox.information(self, "!",\
                                              "A numeric value is expected")
                    return
            elif mType == 7:
                aValue = re.compile(str(setup.attrValue.text()))
            elif mType == 0 or mType == 1:

                aValue =  str(setup.attrValue.text())

            if mType == 1 or mType == 2: #"is or =="
                cmpFn = lambda x,y: x == y
            elif mType == 0: # "contains"
                cmpFn = lambda x,y: y in x
            elif mType == 3:
                cmpFn = lambda x,y: x >= y
            elif mType == 4:
                cmpFn = lambda x,y: x > y
            elif mType == 5:
                cmpFn = lambda x,y: x <= y
            elif mType == 6:
                cmpFn = lambda x,y: x < y
            elif mType == 7:
                cmpFn = lambda x,y: re.search(y, x)

            last_match_node = None
            for n in self.scene.tree.traverse(is_leaf_fn=_leaf):
                if setup.leaves_only.isChecked() and not _leaf(n):
                    continue
                if hasattr(n, aName) \
                        and cmpFn(getattr(n, aName), aValue ):
                    self.scene.view.highlight_node(n)
                    last_match_node = n

            if last_match_node:
                item = self.scene.n2i[last_match_node]
                R = item.mapToScene(item.fullRegion).boundingRect()
                R.adjust(-60, -60, 60, 60)
                self.view.fitInView(R.x(), R.y(), R.width(),\
                                    R.height(), Qt.AspectRatioMode.KeepAspectRatio)


    @QtCore.pyqtSlot()
    def on_actionClear_search_triggered(self):
        # This could be much more efficient
        for n in list(self.view.n2hl.keys()):
            self.scene.view.unhighlight_node(n)

    @QtCore.pyqtSlot()
    def on_actionBranchLength_triggered(self):
        self.scene.img.show_branch_length ^= True
        self.scene.img._scale = None
        self.redraw()
        self.view.centerOn(0,0)

    @QtCore.pyqtSlot()
    def on_actionBranchSupport_triggered(self):
        self.scene.img.show_branch_support ^= True
        self.scene.img._scale = None
        self.redraw()
        self.view.centerOn(0,0)

    @QtCore.pyqtSlot()
    def on_actionLeafName_triggered(self):
        self.scene.img.show_leaf_name ^= True
        self.scene.img._scale = None
        self.redraw()
        self.view.centerOn(0,0)

    @QtCore.pyqtSlot()
    def on_actionForceTopology_triggered(self):
        self.scene.img.force_topology ^= True
        self.scene.img._scale = None
        self.redraw()
        self.view.centerOn(0,0)

    @QtCore.pyqtSlot()
    def on_actionShow_newick_triggered(self):
        d = NewickDialog(self.scene.tree)
        d._conf = _show_newick.Ui_Newick()
        d._conf.setupUi(d)
        d.update_newick()
        d.exec()

    @QtCore.pyqtSlot()
    def on_actionChange_orientation_triggered(self):
        self.scene.props.orientation ^= 1
        self.redraw()

    @QtCore.pyqtSlot()
    def on_actionShow_phenogram_triggered(self):
        self.scene.props.style = 0
        self.redraw()

    @QtCore.pyqtSlot()
    def on_actionShowCladogram_triggered(self):
        self.scene.props.style = 1
        self.redraw()

    @QtCore.pyqtSlot()
    def on_actionOpen_triggered(self):
        d = QFileDialog()
        d._conf = _open_newick.Ui_OpenNewick()
        d._conf.setupUi(d)
        d.exec()
        return
        fname = QFileDialog.getOpenFileName(self ,"Open File",
                                                 "/home",
                                                 )
        try:
            t = Tree(str(fname))
        except Exception as e:
            print(e)
        else:
            self.scene.tree = t
            self.img = TreeStyle()
            self.redraw()

    @QtCore.pyqtSlot()
    def on_actionSave_newick_triggered(self):
        fname = QFileDialog.getSaveFileName(self ,"Save File",
                                                 "/home",
                                                 "Newick (*.nh *.nhx *.nw )")
        nw = self.scene.tree.write()
        try:
            OUT = open(fname,"w")
        except Exception as e:
            print(e)
        else:
            OUT.write(nw)
            OUT.close()

    @QtCore.pyqtSlot()
    def on_actionRenderPDF_triggered(self):
        F = QFileDialog(self)
        if F.exec():
            imgName = str(F.selectedFiles()[0])
            if not imgName.endswith(".pdf"):
                imgName += ".pdf"
            save(self.scene, imgName)


    @QtCore.pyqtSlot()
    def on_actionRender_selected_region_triggered(self):
        if not self.scene.selector.isVisible():
            return QMessageBox.information(self, "!",\
                                              "You must select a region first")

        F = QFileDialog(self)
        if F.exec():
            imgName = str(F.selectedFiles()[0])
            if not imgName.endswith(".pdf"):
                imgName += ".pdf"
            save(imgName, take_region=True)


    @QtCore.pyqtSlot()
    def on_actionPaste_newick_triggered(self):
        text,ok = QInputDialog.getText(self,\
                                                 "Paste Newick",\
                                                 "Newick:")
        if ok:
            try:
                t = Tree(str(text))
            except Exception as e:
                print(e)
            else:
                self.scene.tree = t
                self.redraw()
                self.view.centerOn(0,0)

    def keyPressEvent(self,e):
        key = e.key()
        control = e.modifiers() & Qt.KeyboardModifier.ControlModifier
        if key == 77:
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()
        elif key >= 49 and key <= 58:
            key = key - 48
            m = self.view.transform()
            m.reset()
            self.view.setTransform(m)
            self.view.scale(key, key)


# This function should be reviewed. Probably there are better ways to
# do de same, or at least less messy ways... So far this is what I
# have
class _TableItem(QItemDelegate):
    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)
        self.propdialog = parent

    def paint(self, painter, style, index):
        self.propdialog.tableView.setRowHeight(index.row(), 18)
        val = index.data()
        if getattr(val, "background", None):
            painter.fillRect(style.rect, QColor(val.background))
        QItemDelegate.paint(self, painter, style, index)

    def createEditor(self, parent, option, index):
        # Edit only values, not property names
        if index.column() != 1:
            return None

        originalValue = index.model().data(index)

        value = str(originalValue)

        if re.search("^#[0-9ABCDEFabcdef]{6}$", value):
            origc = QColor(value)
            color = QColorDialog.getColor(origc)
            if color.isValid():
                self.propdialog._edited_indexes.add( (index.row(), index.column()) )
                index.model().setData(index, color.name())
                self.propdialog.apply_changes()

            return None
        else:
            editField = QLineEdit(parent)
            editField.setFrame(False)
            validator = QRegularExpression(".+")
            editField.setValidator(validator)
            editField.returnPressed.connect(self.commitAndCloseEditor)
            editField.returnPressed.connect(self.propdialog.apply_changes)
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
        return str(value)

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)

class _PropModeChooser(QWidget):
    def __init__(self,scene, *args):
        QWidget.__init__(self,*args)

class _PropertiesDialog(QWidget):
    def __init__(self, scene, *args):
        QWidget.__init__(self,*args)
        self.scene = scene
        self._mode = 0
        self.layout =  QVBoxLayout()

        # Display an estimated bL, w, dN and dS for a given evolutionary model
        if hasattr(self.scene.tree, '_models'):
            from ..evol.control import AVAIL
            global AVAIL

            self.model_lbl = QLabel('Showing model: ', self)
            self.layout.addWidget(self.model_lbl)
            self.combo = QComboBox()
            self.layout.addWidget(self.combo)
            try:
                models = sorted(list(self.scene.tree._models.keys()))
            except AttributeError:
                return
            models = []
            for model in sorted(list(self.scene.tree._models.keys())):
                models.append(self.tr(model))
            self.combo.clear()
            if models:
                self.combo.addItems(models)
            else:
                self.combo.addItems([self.tr('None')])


            #self.connect(self.combo, SIGNAL(
            #    "currentIndexChanged(const QString&)"), self.handleModelButton)

            self.combo.currentIndexChanged.connect(self.handleModelButton)

            self.model_lbl = QLabel('Available models: ', self)
            self.layout.addWidget(self.model_lbl)

            if hasattr(next(self.scene.tree.leaves()), 'nt_sequence'):
                self.combo_run = QComboBox()
                self.layout.addWidget(self.combo_run)
                avail_models = sorted(list(AVAIL.keys()))
                self.combo_run.clear()
                self.combo_run.addItems(['%s (%s)' % (m, AVAIL[m]['typ'])
                                         for m in avail_models])
                self.modelButton = QPushButton('Run', self)
                self.modelButton.clicked.connect(self.runModelButton)
                self.layout.addWidget(self.modelButton)

        self.tableView = QTableView()
        self.tableView.move(5,60)
        self.tableView.verticalHeader().setVisible(False)
        #self.tableView.horizontalHeader().setVisible(True)
        #self.tableView.setVerticalHeader(None)
        self.layout.addWidget(self.tableView)
        self.setLayout(self.layout)
        self.tableView.setGeometry (0, 0, 200,200)

    def handleModelButton(self):
        model = sorted(list(self.scene.tree._models.keys()))[self.combo.currentIndex()]
        self.scene.tree.change_dist_to_evol(
            'bL', self.scene.tree._models[model], fill=True)
        self.scene.GUI.redraw()

    def runModelButton(self):
        model = sorted(list(AVAIL.keys()))[self.combo_run.currentIndex()]
        print('Running model %s from GUI...' % model)
        if AVAIL[model]['allow_mark']:
            # TODO if allow mark model and no mark => popup window
            marks = [str(n.node_id) for n in self.scene.tree.descendants()
                     if n.mark]
            if not marks:
                QMessageBox.information(
                    self, "ERROR",
                    "This model requires tree to be marked\nUse right click on "
                    "nodes to mark branches")
                return
            model += '.' + '_'.join(marks)
        self.scene.tree.run_model(model)
        print('Done.')
        try:
            models = sorted(list(self.scene.tree._models.keys()))
        except AttributeError:
            return
        models = []
        for model in sorted(list(self.scene.tree._models.keys())):
            models.append(self.tr(model))
        self.combo.clear()
        if models:
            self.combo.addItems(models)
        else:
            self.combo.addItems([self.tr('None')])

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
            for pname, pvalue in n.props.items():
                if type(pvalue) == int or \
                   type(pvalue) == float or \
                   type(pvalue) == str :
                    self.prop2nodes.setdefault(pname,[]).append(n)
                    self.prop2values.setdefault(pname,[]).append(pvalue)

            for pname,pvalue in n._img_style.items():
                if type(pvalue) == int or \
                   type(pvalue) == float or \
                   type(pvalue) == str :
                    self.style2nodes.setdefault(pname,[]).append(n)
                    self.style2values.setdefault(pname,[]).append(pvalue)

    def get_prop_table(self, node):
        if self._mode == 0: # node
            self.get_props_in_nodes([node])
        elif self._mode == 1: # childs
            self.get_props_in_nodes(list(node.leaves()))
        elif self._mode == 2: # partition
            self.get_props_in_nodes(list(node.traverse()))

        total_props = len(self.prop2nodes) + len(list(self.style2nodes.keys()))
        self.model = QStandardItemModel(total_props, 2)
        self.model.setHeaderData(0, Qt.Orientation.Horizontal, "Feature")
        self.model.setHeaderData(1, Qt.Orientation.Horizontal, "Value")
        self.tableView.setModel(self.model)
        self.delegate = _TableItem(self)
        self.tableView.setItemDelegate(self.delegate)

        row = 0
        items = list(self.prop2nodes.items())
        for name, nodes in sorted(items):
            value= getattr(nodes[0],name)

            index1 = self.model.index(row, 0, QModelIndex())
            index2 = self.model.index(row, 1, QModelIndex())
            f = name#QVariant(str(name))
            v = value#QVariant(value)
            self.model.setData(index1, f)
            self.model.setData(index2, v)
            self._prop_indexes.add( (index1, index2) )
            row +=1

        keys = list(self.style2nodes.keys())
        for name in sorted(keys):
            value= self.style2values[name][0]
            index1 = self.model.index(row, 0, QModelIndex())
            index2 = self.model.index(row, 1, QModelIndex())

            #self.model.setData(index1, QVariant(name))
            self.model.setData(index1, name)
            v = value #QVariant(value)
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

            name = self.model.data(i1)
            value = self.model.data(i2)
            if isinstance(name, QVariant):
                name = str(name.toString())
                value = str(value.toString())
            else:
                name = str(name)
                value = str(value)

            for n in self.style2nodes[name]:
                typedvalue = type(n._img_style[name])(value)
                try:
                    n._img_style[name] = typedvalue
                except:
                    #logger(-1, "Wrong format for attribute:", name)
                    break

        # Apply changes on properties
        for i1, i2 in self._prop_indexes:
            if (i2.row(), i2.column()) not in self._edited_indexes:
                continue

            name = self.model.data(i1)
            value = self.model.data(i2)
            if isinstance(name, QVariant):
                name = str(name.toString())
                value = str(value.toString())
            else:
                name = str(name)
                value = str(value)


            for n in self.prop2nodes[name]:
                try:
                    setattr(n, name, type(getattr(n,name))(value))
                except Exception as e:
                    #logger(-1, "Wrong format for attribute:", name)
                    print(e)
                    break
        self.update_properties(self.node)
        self.scene.img._scale = None
        self.scene.GUI.redraw()
        return

class _TreeView(QGraphicsView):
    def __init__(self,*args):
        QGraphicsView.__init__(self,*args)
        self.buffer_node = None
        self.init_values()

        # NOTE: If in the future we want to use OpenGL or similar, see:
        # https://doc.qt.io/qt-6/qtgui-overview.html#opengl-and-opengl-es-integration
        self.setRenderHints(QPainter.RenderHint.Antialiasing or QPainter.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)
        self.setRenderHints(QPainter.RenderHint.Antialiasing or QPainter.RenderHint.SmoothPixmapTransform )
        #self.setViewportUpdateMode(QGraphicsView.NoViewportUpdate)
        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        #self.setOptimizationFlag (QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing)
        self.setOptimizationFlag (QGraphicsView.OptimizationFlag.DontSavePainterState)
        #self.setOptimizationFlag (QGraphicsView.OptimizationFlag.DontClipPainter)
        #self.scene().setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)
        #self.scene().setBspTreeDepth(24)

    def init_values(self):
        master_item = self.scene().master_item
        self.n2hl = {}
        self.focus_highlight = QGraphicsRectItem(master_item)
        #self.buffer_node = None
        self.focus_node = None
        self.selector = _SelectorItem(master_item)

    def resizeEvent(self, e):
        QGraphicsView.resizeEvent(self, e)

    def safe_scale(self, xfactor, yfactor):
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        xscale = self.transform().m11()
        yscale = self.transform().m22()
        srect = self.sceneRect()

        if ((xfactor > 1 and xscale > 200000) or
            (yfactor > 1 and yscale > 200000)):
            QMessageBox.information(self, "!",
                                    "I will take the microscope!")
            return

        # Do not allow to reduce scale to a value producing height or with smaller than 20 pixels
        # No restrictions to zoom in
        if yfactor < 1 and srect.width() * yscale < 20:
            pass
        elif xfactor < 1 and srect.width() * xscale < 20:
            pass
        else:
            self.scale(xfactor, yfactor)

    def highlight_node(self, n, fullRegion=False, fg="red", bg="gray", permanent=False):
        self.unhighlight_node(n)
        item = self.scene().n2i[n]
        hl = QGraphicsRectItem(item.content)
        if fullRegion:
            hl.setRect(item.fullRegion)
        else:
            hl.setRect(item.nodeRegion)
        hl.setPen(QColor(fg))
        hl.setBrush(QColor(bg))
        hl.setOpacity(0.2)
        # save info in Scene
        self.n2hl[n] = hl
        if permanent:
            item.highlighted = True

    def unhighlight_node(self, n, reset=False):
        if n in self.n2hl:
            item = self.scene().n2i[n]
            if not item.highlighted:
                self.scene().removeItem(self.n2hl[n])
                del self.n2hl[n]
            elif reset:
                self.scene().removeItem(self.n2hl[n])
                del self.n2hl[n]
                item.highlighted = False
            else:
                pass

    def wheelEvent(self,e):
        delta = float(e.angleDelta().y())

        factor =  (-delta / 360.0)

        if abs(factor) >= 1:
            factor = 0.0

        # Ctrl+Shift -> Zoom in X
        if  (e.modifiers() & Qt.KeyboardModifier.ControlModifier) and (e.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.safe_scale(1+factor, 1)

        # Ctrl+Alt -> Zomm in Y
        elif  (e.modifiers() & Qt.KeyboardModifier.ControlModifier) and (e.modifiers() & Qt.KeyboardModifier.AltModifier):
            self.safe_scale(1,1+factor)

        # Ctrl -> Zoom X,Y
        elif e.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.safe_scale(1-factor, 1-factor)

        # Shift -> Horizontal scroll
        elif e.modifiers() &  Qt.KeyboardModifier.ShiftModifier:
            if delta > 0:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()-20 )
            else:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()+20 )
        # No modifiers ->  Vertival scroll
        else:
            if delta > 0:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value()-20 )
            else:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value()+20 )

    def set_focus(self, node):
        i = self.scene().n2i[node]
        self.focus_highlight.setPen(QColor("red"))
        self.focus_highlight.setBrush(QColor("SteelBlue"))
        self.focus_highlight.setOpacity(0.2)
        self.focus_highlight.setParentItem(i.content)
        self.focus_highlight.setRect(i.fullRegion)
        self.focus_highlight.setVisible(True)
        self.prop_table.update_properties(node)
        #self.focus_highlight.setRect(i.nodeRegion)
        self.focus_node = node
        self.update()

    def hide_focus(self):
        return
        #self.focus_highlight.setVisible(False)

    def keyPressEvent(self,e):
        key = e.key()
        control = e.modifiers() & Qt.KeyboardModifier.ControlModifier
        if control:
            if key  == Qt.Key.Key_Left:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()-20 )
                self.update()
            elif key  == Qt.Key.Key_Right:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()+20 )
                self.update()
            elif key  == Qt.Key.Key_Up:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value()-20 )
                self.update()
            elif key  == Qt.Key.Key_Down:
                self.verticalScrollBar().setValue(self.verticalScrollBar().value()+20 )
                self.update()
        else:
            if not self.focus_node:
                self.focus_node = self.scene().tree

            if key == Qt.Key.Key_Left:
                if self.focus_node.up:
                    new_focus_node = self.focus_node.up
                    self.set_focus(new_focus_node)
            elif key == Qt.Key.Key_Right:
                if self.focus_node.children:
                    new_focus_node = self.focus_node.children[0]
                    self.set_focus(new_focus_node)
            elif key == Qt.Key.Key_Up:
                if self.focus_node.up:
                    i = self.focus_node.up.children.index(self.focus_node)
                    if i>0:
                        new_focus_node = self.focus_node.up.children[i-1]
                        self.set_focus(new_focus_node)
                    elif self.focus_node.up:
                        self.set_focus(self.focus_node.up)

            elif key == Qt.Key.Key_Down:
                if self.focus_node.up:
                    i = self.focus_node.up.children.index(self.focus_node)
                    if i < len(self.focus_node.up.children)-1:
                        new_focus_node = self.focus_node.up.children[i+1]
                        self.set_focus(new_focus_node)
                    elif self.focus_node.up:
                        self.set_focus(self.focus_node.up)

            elif key == Qt.Key.Key_Escape:
                self.hide_focus()
            elif key == Qt.Key.Key_Enter or\
                    key == Qt.Key.Key_Return:
                self.prop_table.tableView.setFocus()
            elif key == Qt.Key.Key_Space:
                self.highlight_node(self.focus_node, fullRegion=True,
                                    bg=random_color(l=0.5, s=0.5),
                                    permanent=True)
        QGraphicsView.keyPressEvent(self,e)

    def mouseReleaseEvent(self, e):
        self.scene().view.hide_focus()
        curr_pos = self.mapToScene(e.pos())
        if hasattr(self.selector, "startPoint"):
            x = min(self.selector.startPoint.x(),curr_pos.x())
            y = min(self.selector.startPoint.y(),curr_pos.y())
            w = max(self.selector.startPoint.x(),curr_pos.x()) - x
            h = max(self.selector.startPoint.y(),curr_pos.y()) - y
            if self.selector.startPoint == curr_pos:
                self.selector.setVisible(False)
            self.selector.setActive(False)
        QGraphicsView.mouseReleaseEvent(self,e)

    def mousePressEvent(self,e):
        pos = self.mapToScene(e.pos())
        x, y = pos.x(), pos.y()
        self.selector.setRect(x, y, 0,0)
        self.selector.startPoint = QPointF(x, y)
        self.selector.setActive(True)
        self.selector.setVisible(True)
        QGraphicsView.mousePressEvent(self,e)

    def mouseMoveEvent(self,e):
        curr_pos = self.mapToScene(e.pos())
        if self.selector.isActive():
            x = min(self.selector.startPoint.x(),curr_pos.x())
            y = min(self.selector.startPoint.y(),curr_pos.y())
            w = max(self.selector.startPoint.x(),curr_pos.x()) - x
            h = max(self.selector.startPoint.y(),curr_pos.y()) - y
            self.selector.setRect(x,y,w,h)
        QGraphicsView.mouseMoveEvent(self, e)


class _BasicNodeActions:
    """ Should be added as ActionDelegator """

    @staticmethod
    def init(obj):
        obj.setCursor(Qt.CursorShape.PointingHandCursor)
        obj.setAcceptHoverEvents(True)

    @staticmethod
    def hoverEnterEvent (obj, e):
        print("HOLA")

    @staticmethod
    def hoverLeaveEvent(obj, e):
        print("ADIOS")

    @staticmethod
    def mousePressEvent(obj, e):
        print("Click")

    @staticmethod
    def mouseReleaseEvent(obj, e):
        if e.button() == Qt.MouseButton.RightButton:
            obj.showActionPopup()
        elif e.button() == Qt.MouseButton.LeftButton:
            obj.scene().view.set_focus(obj.node)
            #obj.scene().view.prop_table.update_properties(obj.node)

    @staticmethod
    def hoverEnterEvent (self, e):
        self.scene().view.highlight_node(self.node, fullRegion=True)

    @staticmethod
    def hoverLeaveEvent(self,e):
        self.scene().view.unhighlight_node(self.node)
