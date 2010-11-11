import re

try:
    from PyQt4  import QtCore, QtGui
    from PyQt4.QtGui import QPrinter
except ImportError:
    import QtCore, QtGui
    from QtGui import QPrinter

try:
    from PyQt4 import QtOpenGL
    #USE_GL = True
    USE_GL = False # Temporarily disabled
except ImportError:
    USE_GL = False


import _mainwindow, _search_dialog, _show_newick, _open_newick, _about

class _MainApp(QtGui.QMainWindow):
    def __init__(self, scene, *args):
        QtGui.QMainWindow.__init__(self, *args)
        self.scene = scene
        self.view  = _MainView(scene)
        scene.view = self.view
        _mainwindow.Ui_MainWindow().setupUi(self)
        scene.view = self.view
        self.view.centerOn(0,0)
        splitter = QtGui.QSplitter()
        splitter.addWidget(self.view)
        splitter.addWidget(scene.propertiesTable)
        self.setCentralWidget(splitter)

        # I create a single dialog to keep the last search options
        self.searchDialog =  QtGui.QDialog()
        # Don't know if this is the best way to set up the dialog and
        # its variables
        self.searchDialog._conf = _search_dialog.Ui_Dialog()
        self.searchDialog._conf.setupUi(self.searchDialog)


    @QtCore.pyqtSignature("")
    def on_actionETE_triggered(self):
        try:
            __VERSION__
        except:
            __VERSION__= "developmnet branch"

        d = QtGui.QDialog()
        d._conf = _about.Ui_About()
        d._conf.setupUi(d)
        d._conf.version.setText("Version: %s" %__VERSION__)
        d._conf.version.setAlignment(QtCore.Qt.AlignHCenter)
        d.exec_()

    @QtCore.pyqtSignature("")
    def on_actionZoomOut_triggered(self):
        self.view.safe_scale(0.8,0.8)

    @QtCore.pyqtSignature("")
    def on_actionZoomIn_triggered(self):
        self.view.safe_scale(1.2,1.2)

    @QtCore.pyqtSignature("")
    def on_actionZoomInX_triggered(self):
        self.scene.props.tree_width += 20
        self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionZoomOutX_triggered(self):
        if self.scene.props.tree_width >20:
            self.scene.props.tree_width -= 20
            self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionZoomInY_triggered(self):
        if self.scene.props.min_branch_separation < \
                self.scene.min_real_branch_separation:
            self.scene.props.min_branch_separation = \
                self.scene.min_real_branch_separation
        self.scene.props.min_branch_separation += 5
        self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionZoomOutY_triggered(self):
        if self.scene.props.min_branch_separation > 5:
            self.scene.props.min_branch_separation -= 5
            self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionFit2tree_triggered(self):
        self.view.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

    @QtCore.pyqtSignature("")
    def on_actionFit2region_triggered(self):
        if self.scene.highlighter.isVisible():
            R = self.scene.highlighter.rect()
        else:
            R = self.scene.selector.rect()
        if R.width()>0 and R.height()>0:


            self.view.fitInView(R.x(), R.y(), R.width(),\
                                    R.height(), QtCore.Qt.KeepAspectRatio)

    @QtCore.pyqtSignature("")
    def on_actionSearchNode_triggered(self):
        ok = self.searchDialog.exec_()
        if ok:
            setup = self.searchDialog._conf
            mType = setup.attrType.currentIndex()
            aName = str(setup.attrName.text())
            if mType >= 2 and mType <=6:
                try:
                    aValue =  float(setup.attrValue.text())
                except ValueError:
                    QtGui.QMessageBox.information(self, "!",\
                                              "A numeric value is expected")
                    return
            elif mType == 7:
                aValue = re.compile(str(setup.attrValue.text()))
            elif mType == 0 or mType == 1:
                aValue =  str(setup.attrValue.text())

            if mType == 0 or mType == 2:
                cmpFn = lambda x,y: x == y
            elif mType == 1:
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

            for n in self.scene.startNode.traverse():
                if setup.leaves_only.isChecked() and not n.is_leaf():
                    continue
                if hasattr(n, aName) \
                        and cmpFn(getattr(n, aName), aValue ):
                    self.scene.highlight_node(n)

    @QtCore.pyqtSignature("")
    def on_actionClear_search_triggered(self):
        # This could be much more efficient
        for n in self.scene._highlighted_nodes.keys():
            self.scene.unhighlight_node(n)

    @QtCore.pyqtSignature("")
    def on_actionBranchLength_triggered(self):
        self.scene.props.draw_branch_length ^= True
        self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionForceTopology_triggered(self):
        self.scene.props.force_topology ^= True
        self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionShow_newick_triggered(self):
        d = NewickDialog(self.scene.startNode)
        d._conf = _show_newick.Ui_Newick()
        d._conf.setupUi(d)
        d.update_newick()
        d.exec_()

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

        d = QtGui.QFileDialog()
        d._conf = _open_newick.Ui_OpenNewick()
        d._conf.setupUi(d)
        d.exec_()
        return


        fname = QtGui.QFileDialog.getOpenFileName(self ,"Open File",
                                                 "/home",
                                                 )


        try:
            t = Tree(str(fname))
        except Exception, e:
            print e
        else:
            self.scene.initialize_tree_scene(t, "basic", TreeImageProperties())
            self.scene.draw()

    @QtCore.pyqtSignature("")
    def on_actionSave_newick_triggered(self):
        fname = QtGui.QFileDialog.getSaveFileName(self ,"Save File",
                                                 "/home",
                                                 "Newick (*.nh *.nhx *.nw )")
        nw = self.scene.startNode.write()
        try:
            OUT = open(fname,"w")
        except Exception, e:
            print e
        else:
            OUT.write(nw)
            OUT.close()

    @QtCore.pyqtSignature("")
    def on_actionRenderPDF_triggered(self):
        F = QtGui.QFileDialog(self)
        if F.exec_():
            imgName = str(F.selectedFiles()[0])
            if not imgName.endswith(".pdf"):
                imgName += ".pdf"
            self.scene.save(imgName)


    @QtCore.pyqtSignature("")
    def on_actionRender_selected_region_triggered(self):
        if not self.scene.selector.isVisible():
            return QtGui.QMessageBox.information(self, "!",\
                                              "You must select a region first")

        F = QtGui.QFileDialog(self)
        if F.exec_():
            imgName = str(F.selectedFiles()[0])
            if not imgName.endswith(".pdf"):
                imgName += ".pdf"
            self.scene.save(imgName, take_region=True)


    @QtCore.pyqtSignature("")
    def on_actionPaste_newick_triggered(self):
        text,ok = QtGui.QInputDialog.getText(self,\
                                                 "Paste Newick",\
                                                 "Newick:")
        if ok:
            try:
                t = Tree(str(text))
            except Exception,e:
                print e
            else:
                self.scene.initialize_tree_scene(t,"basic", TreeImageProperties())
                self.scene.draw()

# This function should be reviewed. Probably there are better ways to
# do de same, or at least less messy ways... So far this is what I
# have :)
class _TableItem(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)
        self.propdialog = parent

    def paint(self, painter, option, index):
        self.propdialog.tableView.setRowHeight(index.row(), 18)
        QtGui.QItemDelegate.paint(self, painter, option, index)

    def createEditor(self, parent, option, index):
        # Edit only values, not property names
        if index.column() != 1:
            return None

        originalValue = index.model().data(index)
        if not self.isSupportedType(originalValue.type()):
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
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.horizontalHeader().setVisible(False)
        self.tableView.setVerticalHeader(None)
        self.layout.addWidget(self.tableView)
        self.setLayout(self.layout)
        self.tableView.setGeometry ( 0, 0, 200,200 )


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
                    #logger(-1, "Wrong format for attribute:", name)
                    break

        # Apply changes on properties
        for i1, i2 in self._prop_indexes:
            if (i2.row(), i2.column()) not in self._edited_indexes:
                continue
            name = str(self.model.data(i1).toString())
            value = str(self.model.data(i2).toString())
            for n in self.prop2nodes[name]:
                try:
                    setattr(n, name, type(getattr(n,name))(value))
                except Exception, e:
                    #logger(-1, "Wrong format for attribute:", name)
                    print e
                    break
        self.update_properties(self.node)
        self.scene.draw()
        return

class NewickDialog(QtGui.QDialog):
    def __init__(self, node, *args):
        QtGui.QDialog.__init__(self, *args)
        self.node = node

    def update_newick(self):
        f= int(self._conf.nwFormat.currentText())
        self._conf.features_list.selectAll()
        if self._conf.useAllFeatures.isChecked():
            features = []
        elif self._conf.features_list.count()==0:
            features = None
        else:
            features = set()
            for i in self._conf.features_list.selectedItems():
                features.add(str(i.text()))

        nw = self.node.write(format=f, features=features)
        self._conf.newickBox.setText(nw)

    def add_feature(self):
        aName = str(self._conf.attrName.text()).strip()
        if aName != '':
            self._conf.features_list.addItem( aName)
            self.update_newick()
    def del_feature(self):
        r = self._conf.features_list.currentRow()
        self._conf.features_list.takeItem(r)
        self.update_newick()

    def set_custom_features(self):
        state = self._conf.useAllFeatures.isChecked()
        self._conf.features_list.setDisabled(state)
        self._conf.attrName.setDisabled(state)
        self.update_newick()

class _MainView(QtGui.QGraphicsView):
    def __init__(self,*args):
        QtGui.QGraphicsView.__init__(self,*args)

        #self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        #self.setViewportUpdateMode(QtGui.QGraphicsView.MinimalViewportUpdate)
        #self.setOptimizationFlag (QtGui.QGraphicsView.DontAdjustForAntialiasing)
        #self.setOptimizationFlag (QtGui.QGraphicsView.DontSavePainterState)

        if USE_GL:
            F = QtOpenGL.QGLFormat()
            F.setSampleBuffers(True)
            print F.sampleBuffers()
            self.setViewport(QtOpenGL.QGLWidget(F))
            self.setRenderHints(QtGui.QPainter.Antialiasing)
        else:
            self.setRenderHints(QtGui.QPainter.Antialiasing or QtGui.QPainter.SmoothPixmapTransform )
            self.setViewportUpdateMode(QtGui.QGraphicsView.SmartViewportUpdate)


    def resizeEvent(self, e):
        QtGui.QGraphicsView.resizeEvent(self, e)


    def safe_scale(self, xfactor, yfactor):
        self.setTransformationAnchor(self.AnchorUnderMouse)

        xscale = self.matrix().m11()
        yscale = self.matrix().m22()
        srect = self.sceneRect()

        if (xfactor>1 and xscale>200000) or \
                (yfactor>1 and yscale>200000):
            QtGui.QMessageBox.information(self, "!",\
                                              "Hey! I'm not an electron microscope?")
            return

        # Do not allow to reduce scale to a value producing height or with smaller than 20 pixels
        # No restrictions to zoomin
        if (yfactor<1 and  srect.width() * yscale < 20):
            pass
        elif (xfactor<1 and  srect.width() * xscale < 20):
            pass
        else:
            self.scale(xfactor, yfactor)


    def wheelEvent(self,e):
        factor =  (-e.delta() / 360.0)

        # Ctrl+Shift -> Zoom in X
        if  (e.modifiers() & QtCore.Qt.ControlModifier) and (e.modifiers() & QtCore.Qt.ShiftModifier):
            self.safe_scale(1+factor, 1)

        # Ctrl+Alt -> Zomm in Y
        elif  (e.modifiers() & QtCore.Qt.ControlModifier) and (e.modifiers() & QtCore.Qt.AltModifier):
            self.safe_scale(1,1+factor)

        # Ctrl -> Zoom X,Y
        elif e.modifiers() & QtCore.Qt.ControlModifier:
            self.safe_scale(1-factor, 1-factor)

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
        #print >>sys.stderr, "****** Pressed key: ", key, QtCore.Qt.LeftArrow
        if key  == QtCore.Qt.Key_Left:
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


class _NodeActions(object):
    """ Used to extend QGraphicsItem features """
    def hoverEnterEvent (self,e):

        #width = self..mapFromScene(self.scene().i_width, 0).x()
        #height = self.rect().height()
        if self.node: 
            node_partition = self.scene().node2item[self.node]
            self.scene().highlighter.setRect(node_partition.rect())
            self.scene().highlighter.setParentItem(node_partition)
            self.scene().highlighter.setVisible(True)

    def hoverLeaveEvent (self,e):
        self.scene().highlighter.setVisible(False)

    def mousePressEvent(self,e):
        pass

    def mouseReleaseEvent(self,e):
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
        contextMenu.addAction( "Swap branches"        , self.swap_branches)
        contextMenu.addAction( "Delete node"          , self.delete_node)
        contextMenu.addAction( "Delete partition"     , self.detach_node)
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
        contextMenu.addAction( "Show newick"        , self.show_newick)
        contextMenu.exec_(QtGui.QCursor.pos())

    def show_newick(self):
        d = NewickDialog(self.node)
        d._conf = _show_newick.Ui_Newick()
        d._conf.setupUi(d)
        d.update_newick()
        d.exec_()
        return False

    def delete_node(self):
        self.node.delete()
        self.scene().draw()

    def detach_node(self):
        self.node.detach()
        self.scene().draw()

    def swap_branches(self):
        self.node.swap_childs()
        self.scene().draw()

    def add_childs(self):
        n,ok = QtGui.QInputDialog.getInteger(None,"Add childs","Number of childs to add:",1,1)
        if ok:
            for i in xrange(n):
                ch = self.node.add_child()
            self.scene().set_style_from(self.scene().startNode,self.scene().layout_func)

    def void(self):
        return True

    def set_as_outgroup(self):
        self.scene().startNode.set_outgroup(self.node)
        self.scene().set_style_from(self.scene().startNode, self.scene().layout_func)
        self.scene().draw()

    def toggle_collapse(self):
        self.node.collapsed ^= True
        self.scene().draw()

    def cut_partition(self):
        self.scene().buffer_node = self.node
        self.node.detach()
        self.scene().draw()

    def paste_partition(self):
        if self.scene().buffer_node:
            self.node.add_child(self.scene().buffer_node)
            self.scene().set_style_from(self.scene().startNode,self.scene().layout_func)
            self.scene().buffer_node= None
            self.scene().draw()

    def populate_partition(self):
        n, ok = QtGui.QInputDialog.getInteger(None,"Populate partition","Number of nodes to add:",2,1)
        if ok:
            self.node.populate(n)
            self.scene().set_style_from(self.scene().startNode,self.scene().layout_func)
            self.scene().draw()

    def set_start_node(self):
        self.scene().startNode = self.node
        self.scene().draw()

    def back_to_parent_node(self):
        self.scene().startNode = self.node.up
        self.scene().draw()
