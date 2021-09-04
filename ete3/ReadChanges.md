This file was created for an easy lookup of the changes made in the commit
Feel free to delete it afterwards

# Treeview

## Qt GUI changes

1.	Added the ability to ladderize a specific node (and it's children) both top to bottom and bottom to top
2.	Created better dialog to save the tree view (as PDF file)
3.	Added .newick and .nwk in the save newick dialog
4.	Changed the QApplication widget to QMainWindow widget (explain below)

#### references: 

1. 		top to bottom: node_gui_actions.py: lines 154, 270 - 272
		bottom to top: node_gui_actions.py: lines 155, 274 - 276
2.		qt4_gui.py: lines 386 - 394 & lines 401 - 409 
3.		qt4_gui.py: lines 372, 374
4.		drawer.py: lines 67, 68, 95, 156, 157
		
	When embedding the tree.show() function inside another GUI application (as I am trying to do for a project of mine) the following error occurs.
	`QCoreApplication::exec: The event loop is already running`
	since an application is getting called by another application and this is fatal for the main loop.  
	Exiting the first application will ***not*** close the second application, which will therefore consume system resources until manually killed. For this reason the QApplication widget can be changed with a QMainWindow widget, since the ete GUI uses only one primary window. As far as I have read the scripts there is no need for an event loop when displaying the window.  
	If you think that this change is not good feel free to discuss.

## Leaf name color attribute

1. Created function to add leaf text color
2. Fixed code to not add default (black) text face as leaf label if one is already specified. The user may want to add a custom color on leaf labels

#### references:
1.		tree.py: lines 2590 - 2596
2. 		qt4_render.py: lines 263 - 268
