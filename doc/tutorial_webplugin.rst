************************************
Interactive web tree applications
************************************

.. versionadded:: 2.1

Starting at version 2.1, ETE provides a module to interactively
display trees in web pages.

The :mod:`ete2.webplugin` module implements a transparent connector
between ETE's functionality and python web application. For this, a
`Web Server Gateway Interface (WSGI)
<http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface>`_
application is provided.

Through this application, you will be able to create custom web
implementations to visualize and manipulate trees interactively. Some
examples can be found at the `PhylomeDB tree browser
<http://phylomedb.org/?q=search_tree&seqid=Phy00085K5_HUMAN>`_ or in
the `ETE's online treeviewer <http://ete.cgenomics.org/treeview>`_.


======================================
Configuring your web sever
======================================

You will need to add support for WSGI application to your web
server. In the following steps, an Apache2 web server will be assumed.

* Install and activate the ``modwsgi`` module in Apache.

* Configure your site to support WSGI. 

This is an example configuration file for the default site of your
Apache server (usually at ``/ete/apache2/sites-available/default``):

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


======================================
Creating your web tree application
======================================

ETE's web tree application uses WSGI in the backend, and a several
javascript files in the frontend. 

The best way to start creating your web application is to make use of
the ETE's webplugin examples. They can be found within the
installation package (``examples/webplugin``) or downloaded from
`XXXXXXXXX`_

Copy the *webplugin* directory to the document root path of your
site. Remember that *webplugin* directory path must be configured to
execute WSGI applications in Apache config files.

==========================================
Adding functionality to your application
==========================================

blah blah

::

  webplugin/tmp/    # chmod 777 
  webplugin/wsgi/   # WSGI Apache enabled

