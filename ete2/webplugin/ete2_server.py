#!/usr/bin/python
import sys, os, random
from mod_python import Cookie

def generateHash():
    import sha, time
    return sha.new(str(time.time())).hexdigest()

def getCookie(req, key):
    cookies = Cookie.get_cookies(req)
    if cookies.has_key(key):
        return str(cookies[key]).split('=')[1]

def setCookie(req, key, value):
    cookie = Cookie.Cookie(key, value)
    Cookie.add_cookie(req, cookie)

class WebPlugin:
    def __init__(self, req, temp_folder='/var/tmp', hostname = '/'):
        if getCookie(req, 'sid'):
            self.sid = getCookie(req, 'sid')
        else:
            self.sid = generateHash()
            setCookie(req, 'sid', self.sid)
        self.tempFolder = temp_folder
        self.sessionFolder = os.path.join(self.tempFolder, self.sid)
        if not os.path.exists(self.sessionFolder):
            os.mkdir(self.sessionFolder)
            os.chmod(self.sessionFolder, 0777)
        self.hostname = hostname

    def publishTree(self, tree):
        TREE = open(os.path.join(self.sessionFolder, 'test.tree'), 'w')
        print >> TREE, tree
        treeid = 'test'
        return "<img src='"+self.hostname+"loader.gif?rnd="+str(random.random())+"' id='"+treeid+"' onClick=\"mapcheck(this,'"+treeid+"')\" onLoad=\"get_map(this, '"+treeid+"', '"+self.sid+"')\"><div id='scriptarea_"+treeid+"'></div>"

def form():
    return '''Input the tree in NW format and press DRAW<form name='tree_input' method='post' action='/index/tree'><textarea name='tree' style='width: 700px; height: 200px'>(Sce0008330:0.291009,Sce0012351:0.286238,((((((Sce0007182:0.007445,Sce0006845:0.000000)0.149440:0.000642,Sce0010258:0.435715)0.028000:0.000000,Sce0009286:0.000000)0.000000:0.000000,(Sce0008283:0.008074,(((Sce0011197:0.008115,((Sce0010685:0.000000,Sce0012157:0.000000)0.125038:0.000000,Sce0012332:0.016679)0.788000:0.008129)0.797000:0.008200,(Sce0009812:0.000000,Sce0010100:0.000000)0.849000:0.008096)0.000000:0.000000,((Sce0006682:0.000000,(Sce0009344:0.008122,Sce0008221:0.008223)0.000000:0.000000)0.000000:0.000000,Sce0008967:0.000000)0.000000:0.000000)0.789000:0.008262)0.821000:0.008102)0.724000:0.068767,(Sce0008579:0.000000,(Sce0010646:0.000000,((Sce0010257:0.444538,Sce0010729:0.000000)0.779000:0.008777,(((Sce0009863:0.000000,Sce0010508:0.016244)0.846000:0.008054,((Sce0012763:0.000000,Sce0013060:0.000000)0.125038:0.000000,Sce0011718:0.000000)0.000000:0.000000)0.000000:0.000000,Sce0007366:0.008050)0.974000:0.041297)0.730000:0.009072)0.959000:0.076159)0.548892:0.017476)0.999850:0.531965,(Sce0006923:0.579030,Sce0009628:0.371343)0.524000:0.080094)0.994000:0.272496);</textarea><br><input type='submit' value='DRAW'></form>'''

