.. module:: ete2.webplugin

.. currentmodule:: ete2

.. moduleauthor:: Jaime Huerta-Cepas

.. versionadded:: 2.1

Interactive web tree visualization
************************************

Starting at version 2.1, ETE provides a module to interactively
display trees within web pages. This task is not straightforward, but
ETE tries to simplify it by providing a basic
:class:`WebTreeApplication` class that can be imported in your python
web applications.

:class:`WebTreeApplication` implements a transparent connector between
ETE's functionality and web application. For this, a pre-built
`WSGI <http://wsgi.org>`_ application is provided.

Through this application, you will be able to create custom web
implementations to visualize and manipulate trees interactively. Some
examples can be found at the `PhylomeDB tree browser
<http://phylomedb.org/?q=search_tree&seqid=Phy00085K5_HUMAN>`_ or in
the `ETE's online treeviewer <http://etetoolkit.org/treeview>`_.


NO X system available? 
============================

Alternatively, a virtual X system such as XVFB `has been reported
<https://github.com/jhcepas/ete/issues/101>`_ to work in servers without a
proper X backend. Just install XVFB and preface your ETE commands with xvfb-run.

``xvfb-run python MyETEscript.py``  

Installing a X server
=========================

All modern linux desktop installations include a graphical interface
(called X server). However web servers (in which the ETE plugin is
expected to run) may not count with a X server. 

Servers
========

In order to render tree images with ETE, you will need to install, at
least, a basic X server. Note that the X server does not require a
desktop interface, such as Gnome or KDE. 

In Ubuntu, for instance, a basic X server called xdm can be installed
as follows:

``apt-get install  xserver-xorg xdm  xfonts-base xfonts-100dpi xfonts-75dpi``

Once the X server is installed, you will need to configure it to
accept connections from the web-server. 

In our example, edit the ``/etc/X11/xdm/xdm-config`` file and set
following values: ::
  
  DisplayManager*authorize:       false
  !
  DisplayManager*authComplain:    false

Do not forget to restart your xdm server. 

``/etc/init.d/xdm restart``


Desktops
==========

If you plan to use web tree application in a linux desktop computer,
then the X server is already installed. You will only need to give
permissions to the web-server (i.e. apache) to connect your
display. Usually, as simple as running the following command in a
terminal:

``xhost +``


Configuring the web sever
======================================

You will need to add support for WSGI application to your web
server. In the following steps, an Apache2 web server will be assumed.

* Install and activate the ``modwsgi`` module in Apache.

* Configure your site to support WSGI. 

Configuration will depend a lot on your specific system, but this is
an example configuration file for the default site of your Apache
server (usually at ``/ete/apache2/sites-available/default``):

::

  <VirtualHost *:80>                                                                                                                                                                                           
   ServerAdmin webmaster@localhost                                                                                                                                                                             
   
   DocumentRoot /var/www                                                                                                                                                                                       
   <Directory />                                                                                                                                                                                               
          Options +FollowSymLinks                                                                                                                                                                              
          AllowOverride None                                                                                                                                                                                   
   </Directory>                                                                                                                                                                                                
                                                                                                                                                                                                              
   ErrorLog /var/log/apache2/error.log                                                                                                                                                                         
                                                                                                                                                                                                               
   # Possible values include: debug, info, notice, warn, error, crit,                                                                                                                                          
   # alert, emerg.                                                                                                                                                                                             
   LogLevel warn                                                                                                                                                                                               
                                                                                                                                                                                                              
   CustomLog /var/log/apache2/access.log combined                                                                                                                                                              
   
   # ########################### #
   # WSGI SPECIFIC CONFIG        #
                                                                                                                                                                                                               
   WSGIDaemonProcess eteApp user=www-data group=www-data processes=1 threads=1                                                                                                                                 
   WSGIProcessGroup eteApp                                                                                                                                                                                     
   WSGIApplicationGroup %{GLOBAL}
                                                                                                                                                                                                        
   <Directory /var/www/webplugin/>                                                                                                                                                                                  
          Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch                                                                                                                                                   
          SetHandler wsgi-script                                                                                                                                                                               
          Order allow,deny                                                                                                                                                                                     
          Allow from all                                                                                                                                                                                       
          AddHandler wsgi-script .py                                                                                                                                                                          
   </Directory>                                                                                                                                                                                                
   
   # END OF WSGI SPECIFIC CONFIG # 
   # ########################### #
   
  </VirtualHost>                             

.. note::

   `/var/www/webplugin/wsgi/` is the folder in which python web
   application will be located. Make sure that the apache WSGI config
   enables this folder to run wsgi-scripts.

.. warning::
   
   Important notes: 

   `/var/www/webplugin/` is assumed to be the directory in which your
   application will run. 

   `/var/www/webplugin/tmp/` should be writable by the web-server
   (i.e. chmod 777)



Implementation of WebTreeApplications
========================================

ETE's :class:`WebTreeApplication` uses WSGI in the backend, and a
several javascript files in the frontend. Basic files are included as
an example in the `ETE installation package
<http://pypi.python.org/pypi/ete2>`_ ``examples/webplugin``. The
whole example folder is necessary, and it contains a commented copy of
a web-tree implementation
``examples/webplugin/wsgi/webplugin_example.py``.

