try:
    from PyQt4 import QtGui, QtCore
    from PyQt4.QtCore import (Qt, QPointF, QRect, QRectF, QBuffer, QByteArray,
                              QThread, QIODevice, QMetaObject, QModelIndex, QObject, QRegExp, QSize,
                              QSizeF,QVariant )
    from PyQt4.QtGui import (QAction, QApplication, QBrush, QCheckBox, QColor,
                             QColorDialog, QComboBox, QCursor, QDialog,
                             QDialogButtonBox, QFileDialog, QFont,
                             QFontMetrics, QGraphicsEllipseItem, QGraphicsItem,
                             QGraphicsItemGroup, QGraphicsLineItem,
                             QGraphicsPathItem, QGraphicsPixmapItem,
                             QGraphicsPolygonItem, QGraphicsRectItem,
                             QGraphicsScene, QGraphicsSimpleTextItem,
                             QGraphicsTextItem, QGraphicsView, QIcon, QImage,
                             QInputDialog, QItemDelegate, QLabel, QLineEdit,
                             QListWidget, QMainWindow, QMenu, QMenuBar,
                             QMessageBox, QPainter, QPainterPath, QPen,
                             QPixmap, QPolygonF, QPrinter, QPushButton,
                             QRadialGradient, QRegExpValidator, QSplitter,
                             QStandardItemModel, QStatusBar, QTableView,
                             QTextEdit, QToolBar, QTransform, QVBoxLayout,
                             QWidget)
    from PyQt4.QtSvg import QGraphicsSvgItem, QSvgGenerator
    from PyQt4.QtOpenGL import QGLFormat, QGLWidget

except ImportError:
    from PyQt5 import QtGui, QtCore
    from PyQt5.QtCore import (Qt, QPointF, QRect, QRectF, QBuffer, QByteArray,
                              QThread, QIODevice, QMetaObject, QModelIndex, QObject, QRegExp, QSize,
                              QSizeF,  QVariant) #QString
    from PyQt5.QtSvg import QGraphicsSvgItem, QSvgGenerator
    from PyQt5.QtOpenGL import QGLFormat, QGLWidget
    from PyQt5.QtPrintSupport import QPrinter
    from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QWidget,
                                 QColorDialog, QComboBox, QDialog, QDialogButtonBox, QFileDialog,
                                 QGraphicsEllipseItem, QGraphicsItem, QGraphicsItemGroup, QGraphicsLineItem,
                                 QGraphicsPathItem, QGraphicsPixmapItem, QGraphicsPolygonItem,
                                 QGraphicsRectItem, QGraphicsScene, QGraphicsSimpleTextItem,
                                 QGraphicsTextItem, QGraphicsView, QInputDialog, QItemDelegate, QLabel,
                                 QLineEdit, QListWidget, QMainWindow, QMenu, QMenuBar, QMessageBox,
                                 QPushButton, QSplitter, QStatusBar, QTableView, QTextEdit, QToolBar,
                                 QVBoxLayout, QWidget)


    from PyQt5.QtGui import (QBrush, QColor, QCursor, QFont, QFontMetrics,
                             QIcon, QImage, QPainter, QPainterPath, QPen, QPixmap, QPolygonF,
                             QRadialGradient, QRegExpValidator, QStandardItemModel, QTransform)

    # names =  """QAction, QApplication, QBrush, QCheckBox, QColor,
    #                          QColorDialog, QComboBox, QCursor, QDialog,
    #                          QDialogButtonBox, QFileDialog, QFont,
    #                          QFontMetrics, QGraphicsEllipseItem, QGraphicsItem,
    #                          QGraphicsItemGroup, QGraphicsLineItem,
    #                          QGraphicsPathItem, QGraphicsPixmapItem,
    #                          QGraphicsPolygonItem, QGraphicsRectItem,
    #                          QGraphicsScene, QGraphicsSimpleTextItem,
    #                          QGraphicsTextItem, QGraphicsView, QIcon, QImage,
    #                          QInputDialog, QItemDelegate, QLabel, QLineEdit,
    #                          QListWidget, QMainWindow, QMenu, QMenuBar,
    #                          QMessageBox, QPainter, QPainterPath, QPen,
    #                          QPixmap, QPolygonF, QPrinter, QPushButton,
    #                          QRadialGradient, QRegExpValidator, QSplitter,
    #                          QStandardItemModel, QStatusBar, QTableView,
    #                          QTextEdit, QToolBar, QTransform, QVBoxLayout,
    #                          QWidget"""
    # widgets = []
    # gui = []
    # unk = []
    # for n in map(str.strip, names.split(",")):
    #     try:
    #         exec "from PyQt5.QtGui import %s" %n
    #     except ImportError:
    #         try:
    #             exec "from PyQt5.QtWidgets import %s" %n
    #         except:
    #             unk.append(n)
    #         else:
    #             widgets.append(n)
    #     else:
    #         gui.append(n)

    # print 'from PyQt5.QtWidgets import (%s)' %', '.join(widgets)
    # print 'from PyQt5.QtGui import (%s)' %', '.join(gui)
    # print 'from PyQt5.Unk import (%s)' %', '.join(unk)
    
    QtCore.pyqtSignature = QtCore.pyqtSlot
