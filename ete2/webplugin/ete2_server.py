#!/usr/bin/python
import socket
from SITE_CONFIG import *

HOST = socket.gethostname()
THIS_SESSION_URL = TEMP_DIR_URL
PHYLOMEDB_POINTER = None
CURRENT_USER = "public"

def hide_box(title, content, mode='block'):
        output = "<div style='border: 1px solid #777; padding: 4px; margin-top: 10px;'><div style='margin-top: -14px; position: absolute;'><span class='hide_box_title popup_bg'>" + title + "</span><span class='popup_bg popup_interactor' onClick=\"this.parentNode.parentNode.childNodes[1].style.display = 'block'\">Show</span><span class='popup_bg popup_interactor' onClick=\"this.parentNode.parentNode.childNodes[1].style.display = 'none'\">Hide</span></div><div style='padding-top: 4px; display: "+mode+"'>" + content + "</div></div>"
        return output

def treeimg(req=None, seqid=None, sid=None, rnd=None):
    # create image and map, return image, store the map
    from popen2 import Popen3

    # run tree generator as a separate process ( give as argument the work path and seqid )
    proc = Popen3("python /home/services/web/ivan.phylomedb.org/maketree.py " + str(sid) + " " + str(seqid))
    proc.tochild.close()
    add = '1'
    # read stduotput  =  image
    fromchild = proc.fromchild.readline()
    while add:
        add = proc.fromchild.readline()
        fromchild += add
    if req:
        req.content_type = 'image/png'
    return fromchild  #  send image with a header of image


###########################

def nwtree(req=None):
    if req:
        req.content_type = 'text/html'
    form = "Input the tree:<form name='listadd' method='post' action='http://ivan.phylomedb.org/ete2_server/nwtrees'><textarea name='tree' style='width: 700px; height: 200px'></textarea><br><input type='submit' value='Draw the tree'></form>"
    return form
    
def nwtrees(req=None):
    import cgi, cgitb; cgitb.enable()
    session_id = '123'
    seqid = 'usernw'
    form = cgi.FieldStorage()
    tree = form['tree'].value
    if req:
        req.content_type = 'text/html'
    return tree
    
    THIS_SESSION_PATH = TEMP_DIR_PATH + '/' + str(session_id)
    if os.path.exists(THIS_SESSION_PATH):
        pass
    else:
        os.mkdir(THIS_SESSION_PATH)
    THIS_SESSION_PATH = TEMP_DIR_PATH
    # put tree in a file in temp session directory
    TREEFILE = open(THIS_SESSION_PATH + "/" + seqid + ".tree", "w")
    TREEFILE.write(tree)
    TREEFILE.close()
    # first show loader, then load big tree
    return "<img src='"+BASE_URL+"images/loader.gif?rnd="+str(random.random())+"' id='"+seqid+"' onClick=\"mapcheck(this,'"+seqid+"')\" onLoad=\"get_map(this, '"+seqid+"', '"+session_id+"')\"><div id='scriptarea_"+seqid+"'></div>"


############################

def tree(tree, seqid, session_id, host=None , port=None, req=None):
    import random
    THIS_SESSION_PATH = TEMP_DIR_PATH + '/' + str(session_id)
    if os.path.exists(THIS_SESSION_PATH):
        pass
    else:
        os.mkdir(THIS_SESSION_PATH)

    # put tree in a file in temp session directory
    TREEFILE = open(THIS_SESSION_PATH + "/" + seqid + ".tree", "w")
    TREEFILE.write(tree)
    TREEFILE.close()
    # first show loader, then load big tree
    return "<img src='"+BASE_URL+"images/loader.gif?rnd="+str(random.random())+"' id='"+seqid+"' onClick=\"mapcheck(this,'"+seqid+"')\" onLoad=\"get_map(this, '"+seqid+"', '"+session_id+"')\"><div id='scriptarea_"+seqid+"'></div>"


def getmap(req=None, seqid=None, sid=None):
    # read a map from a file or return alert
    THIS_SESSION_PATH = TEMP_DIR_PATH + '/' + sid
    if req:
        req.content_type = 'text/javascript'
    try:
        res = open(THIS_SESSION_PATH+"/"+seqid+".map")
    except IOError:
        return "alert('no map "+THIS_SESSION_PATH+"');"
    else:
        out = res.readline()
        os.remove(THIS_SESSION_PATH+"/"+seqid+".map")
        return out


def info(req=None, dbid=None):
    # requare any info about DB   id - translation tables can be used etc.
    import os, sys, MySQLdb, ete2
    if req:
        req.content_type = 'text/html'

    ####### copy past from dbquerry.py

    def get_pointer():
        global PHYLOMEDB_POINTER
        if PHYLOMEDB_POINTER is None:
            PHYLOMEDB_POINTER = ete2.PhylomeDBConnector(host = "localhost", user="web_user", passwd="web.2009")
        if CURRENT_USER == "master":
            PHYLOMEDB_POINTER._trees_table = "trees"
            PHYLOMEDB_POINTER._algs_table = "algs"
            PHYLOMEDB_POINTER._phylomes_table = "phylomes"
        else:
            PHYLOMEDB_POINTER._trees_table = "trees_"+CURRENT_USER
            PHYLOMEDB_POINTER._algs_table = "algs_"+CURRENT_USER
            PHYLOMEDB_POINTER._phylomes_table = "phylomes_"+CURRENT_USER
        return PHYLOMEDB_POINTER

    def close_p():
        global PHYLOMEDB_POINTER
        if PHYLOMEDB_POINTER is not None:
            try:
                PHYLOMEDB_POINTER._SQL.close()
                PHYLOMEDB_POINTER._SQLconnection.close()
                PHYLOMEDB_POINTER = None
            except:
                pass

    # prepare seq for popup window
    def split_code(code):
        output = "<table style='font-family: Courier New; font-size: 8pt;'>"
        c = 1
        for i in range(len(code)/10+1):
            if c == 1:
                output += "<tr>"
            output += "<td>" + code[i*10:(i+1)*10] + "</td>"
            if c == 4:
                output += "</tr>"
                c = 0
            c += 1
        if c == 1:
            output += "</table>"
        else:
            output += "</tr></table>"
        return output

    p = get_pointer()
    # get info about DB id
    info = p.get_seqid_info(dbid)
    close_p()
    # put information in nice boxes
    res =  hide_box('Name', info['name'])
    res += hide_box('Comments', info['comments'])
    res += hide_box('Sequence', split_code(info['seq']), mode='none') # mode='none' - hide the box content by default
    
    return res # return information in the popup menu


def addrule(req=None, seqid=None, itemid=None, rule=None, sid=None, unic='0', remove='0', clear='0'):

    THIS_SESSION_PATH = TEMP_DIR_PATH + '/' + sid
    
    # function add a rule to the rules file
    # 3 possible work modes:  ADD (add new rule if it doesn't exist), REMOVE (remove rule if it exists), UNIC (add rule, after delete the rule with a same key)
    # for every mode there is javascript function:     set_rule(),     rem_rule(),     unic_rule()
    # processing of the rules file located in the script maketree.py   during tree generation
    
    if req:
        req.content_type = 'text/plain'
    done = False
    rules = set()
    if clear == '1':
        RULES = open(THIS_SESSION_PATH+"/"+seqid+".rules", "w")
        RULES.close()
    else:
        try:
            RULES = open(THIS_SESSION_PATH+"/"+seqid+".rules")
        except IOError:
            pass
        else:
            for item in RULES:
                key, value = item.strip().split('\t')
                if remove == '1' and str(key) == str(rule) and str(value) == str(itemid):
                    pass
                elif unic == '1' and key == rule:
                    pass
                else:
                    rules.add(item.strip())

        if remove == '0':
            rules.add(rule + '\t' + str(itemid))
        
        RULES = open(THIS_SESSION_PATH+"/"+seqid+".rules", "w")
        sid
        for rule in rules:
            print >> RULES, rule
    
    return 1
