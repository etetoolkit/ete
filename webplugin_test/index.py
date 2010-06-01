# -*- coding: utf-8 -*-
#!/usr/bin/python

import ete_dev, os
from ete_dev.webplugin import ete2_server
from sitesettings import *

header = '''<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
    <title>ETE2 - web plugin demonstration</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <script src="'''+HOST_NAME+'''activeete.js"></script>
<style>
.popup {
	font-family: Trebuchet MS;
	font-size: 10pt;
	border: 1px solid #777;
}
.popup_bg {
	background: #EEE;
}
.popup_title {
	background: #DDD;
	color: green;
	cursor: move;
	padding: 3px;
}
.popup_interactor {
	cursor: pointer;
	color: grey;
	padding-left: 3px;
	padding-right: 3px;
}
.hide_box_title  {
	color: green;
	padding-left: 3px;
	padding-right: 3px;
}
</style>
</head><body>'''
end = "</body></html>"


def index(req=None):        
    if req:
        req.content_type = 'text/html'
    res = ete2_server.form()
    return header+res+end

def tree(req=None):
    import os, cgi, cgitb; cgitb.enable()
    if req:
        req.content_type = 'text/html'
    wp = ete2_server.WebPlugin(req, temp_folder=TEMP_FOLDER, hostname=HOST_NAME)
    res = wp.publishTree(req.form['tree'])
    return header+res+end

    
