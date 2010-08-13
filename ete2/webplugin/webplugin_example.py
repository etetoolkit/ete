# You should place this file in a WSGI apache enabled directory
#
# This structure worked for me
# 
# /var/www/wsgi/webplugin_example.py 
# /var/www/tmp/                    # 777 
# /var/www/webplugin_example.html
# /var/www/jquery-1.4.2.min.js
# /var/www/ete.js
# /var/www/ete.css

# My apache config para el sitio "default":
#
# <VirtualHost *:80>
#         ServerAdmin webmaster@localhost

#        WSGIDaemonProcess site-1 user=www-data group=www-data processes=1 threads=1
#        WSGIProcessGroup site-1

#  
#         DocumentRoot /var/www
#         <Directory />
#         	Options +FollowSymLinks
#         	AllowOverride None
#         </Directory>
#  
#  
#         <Directory /var/www/wsgi/>
#         	Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
#          	SetHandler wsgi-script
#         	Order allow,deny
#         	Allow from all
#                 AddHandler wsgi-script .py  
#         </Directory>
#  
#         ErrorLog /var/log/apache2/error.log
#  
#         # Possible values include: debug, info, notice, warn, error, crit,
#         # alert, emerg.
#         LogLevel warn
#  
#         CustomLog /var/log/apache2/access.log combined
#  
#  
# </VirtualHost>
#

# Final import should be like this
# from ete2.webplugin  import WebTreeApplication
import sys
sys.path.append("/var/www/ete2-webplugin/ete2/webplugin")
from webplugin import WebTreeApplication, CONFIG

# USER PART. You can modify this part
from ete2 import PhyloTree, faces

application = WebTreeApplication()
# Set your temporal dir to allow web user to generate files
CONFIG["temp_dir"] = "/var/www/tmp/"
CONFIG["temp_url"] = "http://localhost/tmp/"
# Set the DISPLAY port that ete should use to draw pictures. web user
# (i.e. www-data must have permission on the device)
CONFIG["DISPLAY"] = ":0"

# My custom functionality for the plugin
name_face = faces.AttrFace("name", fsize=12)
text_face = faces.TextFace("__ ETE__", fsize=12)

def my_tree_loader(tree):
    t = PhyloTree(tree)
    return t

def my_collapse(node):
    node.add_feature("collapsed", 1)
    node.add_feature("bsize", 50)

def set_red(node):
    node.add_feature("fgcolor", "#ff0000")

def set_as_root(node):
    node.get_tree_root().set_outgroup(node)

def my_layout1(node):
    if hasattr(node, "collapsed"):
        if node.collapsed == 1:
            node.img_style["draw_descendants"]= False
    if hasattr(node, "fgcolor"):
        node.img_style["fgcolor"]= node.fgcolor
    else:
        node.img_style["fgcolor"]= "#00ff00"
    if hasattr(node, "bsize"):
        node.img_style["size"]= int(node.bsize)
    else:
        node.img_style["size"]= 10

    if node.is_leaf():
        faces.add_face_to_node(name_face, node, 0, False)
    faces.add_face_to_node(text_face, node, 1, False)

def my_layout2(node):
    if hasattr(node, "collapsed"):
        if node.collapsed == 1:
            node.img_style["draw_descendants"]= False
    if hasattr(node, "fgcolor"):
        node.img_style["fgcolor"]= node.fgcolor
    else:
        node.img_style["fgcolor"]= "#cccccc"
    if hasattr(node, "bsize"):
        node.img_style["size"]= int(node.bsize)
    else:
        node.img_style["size"]= 10

    if node.is_leaf():
        faces.add_face_to_node(name_face, node, 0, False)


        

def link_to_my_page(action_index, nodeid, treeid, text):
    return """<a href="#"> Example link 1: %s </a><br> """ %(text)

def link_to_my_other_page(action_index, nodeid, treeid, text):
    return """<a href="#"> Example link 2: %s </a><br> """ %(text)

application.set_tree_loader(my_tree_loader)

# register_action(action_name, target_type=node|face|style, action_handler, html_generator_handler )
application.register_action("collapse node", "node", my_collapse, None)
application.register_action("set as root", "node", set_as_root, None)
application.register_action("set red", "node", set_red, None)

application.register_action("notused", "face", None, link_to_my_page)
application.register_action("notused", "face", None, link_to_my_other_page)

application.register_action("default", "layout", None, None)
application.register_action("green", "layout", my_layout1, None)
application.register_action("grey", "layout", my_layout2, None)
