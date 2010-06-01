#!/usr/bin/python
import sys, os, random
from sitesettings import *

PHYLOMEDB_POINTER = None

def rtree(req=None, tree=None, sid=None):
    from popen2 import Popen3
    proc = Popen3("python "+SCRIPT_FOLDER+"/maketree.py "+sid+" "+tree)
    proc.tochild.close()
    add = '1'
    fromchild = proc.fromchild.readline()
    while add:
        add = proc.fromchild.readline()
        fromchild += add
    if req:
        req.content_type = 'image/png'
    return fromchild

def getmap(req=None, seqid=None, sid=None):
    # read a map from a file or return alert
    THIS_SESSION_PATH = TEMP_FOLDER + '/' + sid
    if req:
        req.content_type = 'text/javascript'
    try:
        res = open(THIS_SESSION_PATH+"/"+seqid+".map")
    except IOError:
        return "alert('no map "+THIS_SESSION_PATH+"');"
    else:
        out = res.readline()
        return out

def addrule(req=None, seqid=None, itemid=None, rule=None, sid=None, unic='0', remove='0', clear='0'):
    THIS_SESSION_PATH = TEMP_FOLDER + '/' + sid
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

def hide_box(title, content, mode='block'):
        output = "<div style='border: 1px solid #777; padding: 4px; margin-top: 10px;'><div style='margin-top: -14px; position: absolute;'><span class='hide_box_title popup_bg'>" + title + "</span><span class='popup_bg popup_interactor' onClick=\"this.parentNode.parentNode.childNodes[1].style.display = 'block'\">Show</span><span class='popup_bg popup_interactor' onClick=\"this.parentNode.parentNode.childNodes[1].style.display = 'none'\">Hide</span></div><div style='padding-top: 4px; display: "+mode+"'>" + content + "</div></div>"
        return output

def info(req=None, dbid=None):
    import os, sys, MySQLdb, ete_dev
    if req:
        req.content_type = 'text/html'

    def get_pointer():
        global PHYLOMEDB_POINTER
        if PHYLOMEDB_POINTER is None:
            PHYLOMEDB_POINTER = ete_dev.PhylomeDBConnector()            
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



