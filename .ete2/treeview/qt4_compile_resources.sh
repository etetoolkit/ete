#!/bin/sh 

pyrcc4  ete_resources.qrc -o ete_resources_rc.py
pyuic4 open_newick.ui > _open_newick.py
pyuic4 show_newick.ui > _show_newick.py
pyuic4 search_dialog.ui > _search_dialog.py
pyuic4 ete_qt4app.ui > _mainwindow.py
pyuic4 about.ui > _about.py

# test
python -c 'from ete_dev import Tree; Tree("(A,B,C,(D,E)F,(G,(H,I)J)K);", format=1).show();'
