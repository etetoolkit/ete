# -*- coding: utf-8 -*-
#!/usr/bin/python

import ete_dev, os
import webplugin
from sitesettings import *

head = '''<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
    <title>ETE2 - web-plugin demonstration</title>
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
</head><body background='/bg.gif'>
<div style='position: absolute; width: 700px; margin-left: -350px; top: 10px; margin-bottom:20px; left: 50%; background: #FFF; padding: 10px; text-align: center'>
<h3>Preview of <a href=http://ete.cgenomics.org/>ete2</a>-webplugin for phylogenetic tree manipulations</h3>'''

end = "</div></body></html>"



def index(req=None): 
    if req:
        req.content_type = 'text/html'
    body = '''
<div style='text-align: left;'>
Input the tree in NW format and press "Draw tree":
<form name='tree_input' method='post' action='/index/tree'>
	<textarea name='tree' style='width: 700px; height: 200px'>
(((Cne0002749_Q55RA0:0.690320,(Spb0001902_Q9UT81:1.025930,(Ror0013884_RO3G_13885.1:0.170852,Ror0013238_RO3G_13239.1:0.357725)0.979000:0.234774)0.895000:0.183391)0.356000:0.062227,(Ani0001497_XP_681497.1:0.316441,(Sno0010817_SNU11204.1:0.389108,(Ncr0001064_NCU01100.2:0.468292,Bci0007963_BC1G_07963.1:0.385452)0.991000:0.174607)0.909000:0.102127)0.996000:0.197614)0.743000:0.057995,(Yli0002312_Q6C5V3:0.675110,(Cal0009431_orf19.2549:0.551718,(Sce0006786_YBL058W{seed}:0.450450,Ago0005524_NP_983160.1:0.321873)1.000000:0.298585)0.999850:0.421397)0.999850:0.057995);
	</textarea><br>
	<input type='submit' value='Draw tree'>
</form></div>'''
    return head+body+end

def tree(req=None):
    import os, cgi, cgitb; cgitb.enable()
    if req:
        req.content_type = 'text/html'
    wp = webplugin.WebPlugin(req, temp_folder=TEMP_FOLDER, hostname=HOST_NAME)
    try:
        req.form['tree']
    except KeyError:
        body = "This page used not corretct way."
    else:
        body = wp.publishTree(req.form['tree'])
        
    return head+body+end
