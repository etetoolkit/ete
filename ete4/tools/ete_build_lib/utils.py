# -*- coding: utf-8 -*-

# #START_LICENSE###########################################################
#
#
# This file is part of the Environment for Tree Exploration program
# (ETE).  http://etetoolkit.org
#
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ETE is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
#
#                     ABOUT THE ETE PACKAGE
#                     =====================
#
# ETE is distributed under the GPL copyleft license (2008-2015).
#
# If you make use of ETE in published work, please cite:
#
# Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon.
# ETE: a python Environment for Tree Exploration. Jaime BMC
# Bioinformatics 2010,:24doi:10.1186/1471-2105-11-24
#
# Note that extra references to the specific methods implemented in
# the toolkit may be available in the documentation.
#
# More info at http://etetoolkit.org. Contact: huerta@embl.de
#
#
# #END_LICENSE#############################################################
from __future__ import absolute_import
from __future__ import print_function

import sys
from os import kill
from os.path import join as pjoin
from os.path import split as psplit
from os.path import exists as pexist
import os
import socket
import string

import random
import hashlib
import logging
import time
import datetime
import re
import shutil
from glob import glob
import six
from six.moves import range
from six.moves import input

from .getch import Getch
from .errors import DataError

try:
    import numpy
except ImportError:
    import math
    def _mean(nums):
        return float(sum(nums)) / len(nums)

    def _std(nums):
        avg = _mean(nums)
        variance = [(x - avg)**2 for x in nums]
        std = math.sqrt(_mean(variance))
        return std

    def _median(nums):
        nums.sort()
        size = len(nums)
        midPos = size // 2
        if size % 2 == 0:
            median = (nums[midPos] + nums[midPos-1]) / 2.0
        else:
            median = nums[midPos]
        return median
    _max = max
    _min = min
else:
    _std = numpy.std
    _max = numpy.max
    _min = numpy.min
    _mean = numpy.mean
    _median = numpy.median


log = logging.getLogger("main")
DEBUG = lambda: log.level <= 10
hascontent = lambda f: pexist(f) and os.path.getsize(f) > 0
GLOBALS = {
    "running_jobs": set(), # Keeps a list of jobs consuming cpu
    "cached_status": {}, # Saves job and task statuses by id to be
                         # used them within the same get_status cycle
}

class _DataTypes(object):
    def __init__(self):
        self.msf = 100
        self.alg_fasta = 200
        self.alg_phylip = 201
        self.alg_nt_fasta = 202
        self.alg_nt_phylip = 203

        self.clean_alg_fasta = 225
        self.clean_alg_phylip = 226
        self.kept_alg_columns = 230
        self.concat_alg_fasta = 250
        self.concat_alg_phylip = 251
        self.alg_stats = 260
        self.alg_list = 290
        self.best_model = 300
        self.model_ranking = 305
        self.model_partitions = 325
        self.tree = 400
        self.tree_stats = 410
        self.constrain_tree = 425
        self.constrain_alg = 426
        self.cogs = 500
        self.cog_analysis = 550

        self.job = 1
        self.task = 2

DATATYPES = _DataTypes()


from collections import OrderedDict

# ete3 should be added to the python path by the npr script
from ...phylo import PhyloTree
from ...coretype.tree import Tree
from ...coretype.seqgroup import SeqGroup
from ...parser.fasta import read_fasta
from ...coretype import tree
from ...ncbi_taxonomy import ncbiquery as ncbi

# This default values in trees are Very important for outgroup
# selection algorithm to work:
tree.DEFAULT_SUPPORT = 1.0
tree.DEFAULT_DIST = 1.0
#from ete3.treeview import drawer
#drawer.GUI_TIMEOUT = 1

TIME_FORMAT = '%a %b %d %H:%M:%S %Y'

AA = set('ACEDGFIHKMLNQPSRTWVY*-.UOBZJX') | set('acedgfihkmlnqpsrtwvyuobzjx')
NT = set("ACGT*-.URYKMSWBDHVN") | set("acgturykmswbdhvn")
GAP_CHARS = set(".-")

GENCODE = {
    'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M',
    'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
    'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K',
    'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R',
    'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L',
    'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
    'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q',
    'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
    'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V',
    'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
    'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E',
    'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
    'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S',
    'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
    'TAC':'Y', 'TAT':'Y', 'TAA':'*', 'TAG':'*',
    'TGC':'C', 'TGT':'C', 'TGA':'*', 'TGG':'W',
    '---': '-',
    }

# Aux functions (general)
md5 = lambda x: hashlib.md5(x.encode("utf-8")).hexdigest()
encode_seqname = lambda x: md5(x)[:10]
basename = lambda path: psplit(path)[-1]
# Aux functions (task specific)
get_raxml_mem = lambda taxa,sites: (taxa-2) * sites * (80 * 8) * 9.3132e-10
del_gaps = lambda seq: seq.replace("-","").replace(".", "")
random_string = lambda N: ''.join(random.choice(string.ascii_uppercase +
                                  string.digits) for x in range(N))
generate_id = lambda items: md5(','.join(sorted(items)))
generate_runid = lambda: md5(str(time.time()*random.random()))

HOSTNAME = socket.gethostname()

def tobool(value):
    return str(value).lower() in set(["1", "true", "yes"])

def rpath(fullpath):
    'Returns relative path of a task file (if possible)'
    m = re.search("/(tasks/.+)", fullpath)
    if m:
        return m.groups()[0]
    else:
        return fullpath

def ask(string, valid_values, default=-1, case_sensitive=False):
    """ Asks for a keyborad answer """
    v = None
    if not case_sensitive:
        valid_values = [value.lower() for value in valid_values]
    while v not in valid_values:
        v = input("%s [%s]" % (string,','.join(valid_values) ))
        if v == '' and default>=0:
            v = valid_values[default]
        if not case_sensitive:
            v = v.lower()
    return v

def generate_node_ids(target_seqs, out_seqs):
    cladeid = generate_id(target_seqs)
    nodeid = md5(','.join([cladeid, generate_id(out_seqs)]))
    return nodeid, cladeid


def merge_arg_dicts(source, target, parent=""):
    for k,v in six.iteritems(source):
        if not k.startswith("_"):
            if k not in target:
                target[k] = v
            else:
                log.warning("%s: [%s] argument cannot be manually set",
                            parent,k)
    return target

def load_node_size(n):
    if n.is_leaf():
        size = 1
    else:
        size = 0
        for ch in n.children:
            size += load_node_size(ch)
    n.add_feature("_size", size)
    return size

def render_tree(tree, fname):
    # Generates tree snapshot
    npr_nodestyle = NodeStyle()
    npr_nodestyle["fgcolor"] = "red"
    for n in tree.traverse():
        if hasattr(n, "nodeid"):
            n.set_style(npr_nodestyle)
    ts = TreeStyle()
    ts.show_leaf_name = True
    ts.show_branch_length = True
    ts.show_branch_support = True
    ts.mode = "r"
    iterface = faces.TextFace("iter")
    ts.legend.add_face(iterface, 0)

    tree.dist = 0
    tree.sort_descendants()
    tree.render(fname, tree_style=ts, w=700)

def sec2time(secs):
    return str(datetime.timedelta(seconds=secs))

def read_time_file(fname):
    INFO_TIME = open(fname)

    try:
        l1 = INFO_TIME.readline().strip()
        l1 = l1.replace("CEST", "") # TEMP FIX
        l1 = l1.replace("EDT", "") # TEMP FIX
        start = time.mktime(time.strptime(l1, TIME_FORMAT))
    except Exception as e:
        start = ""
        log.warning("execution time: %s", e)

    try:
        l2 = INFO_TIME.readline().strip()
        l2 = l2.replace("CEST", "") # TEMP FIX
        l2 = l2.replace("EDT", "") # TEMP FIX
        end = time.mktime(time.strptime(l2, TIME_FORMAT))
    except Exception as e:
        end = ""
        log.warning("execution time: %s", e)

    INFO_TIME.close()
    return start, end


def dict_string(dictionary, ident = '', braces=1):
    """ Recursively prints nested dictionaries."""
    text = []
    for key in sorted(dictionary.keys()):
        value = dictionary[key]
        if isinstance(value, dict):
            text.append('%s%s%s%s' %(ident,braces*'[',key,braces*']'))
            text.append('\n')
            text.append(dict_string(value, ident+'  ', braces+1))
        else:
            if isinstance(value, set) or isinstance(value, frozenset):
                value = sorted(value)
            text.append(ident+'%s = %s' %(key, value))
            text.append('\n')
    return ''.join(text)


def checksum(*fnames):
    block_size=2**20
    hash = hashlib.md5()
    for fname in fnames:
        f = open(fname, "rb")
        while True:
            data = f.read(block_size)
            if not data:
                break
            hash.update(data)
        f.close()
    return hash.hexdigest()

def pid_up(pid):
    """ Check For the existence of a unix pid. """
    try:
        kill(int(pid), 0)
    except OSError:
        return False
    else:
        return True

def clear_tempdir():
    base_dir = GLOBALS.get("basedir", None)
    out_dir = GLOBALS["output_dir"]
    scratch_dir = GLOBALS.get("scratch_dir", GLOBALS.get("dbdir", base_dir))
    if base_dir and base_dir != out_dir:
        try:
            log.log(20, "Copying new db files to output directory %s..." %out_dir)
            if not pexist(out_dir):
                os.makedirs(out_dir)
            if os.system("cp -a %s/* %s/" %(scratch_dir, out_dir)):
                log.error("Could not copy data from scratch directory!")
            log.log(20, "Deleting temp directory %s..." %scratch_dir)
        except Exception as e:
            print(e)
            log.error("Could not copy data from scratch directory!")
            pass
        # By all means, try to remove temp data
        try: shutil.rmtree(scratch_dir)
        except OSError: pass


def terminate_job_launcher():
    back_launcher = GLOBALS.get("_background_scheduler", None)
    if back_launcher:
        #GLOBALS['_job_queue'].close()
        GLOBALS['_job_queue'].cancel_join_thread()
        back_launcher.join(120) # gives a couple of minutes to finish
        back_launcher.terminate()

def print_as_table(rows, header=None, fields=None, print_header=True, stdout=sys.stdout, wide=True):
    """ Print >>Stdout, a list matrix as a formated table. row must be a list of
    dicts or lists."""
    if header is None:
        header = []

    def _str(i):
        if isinstance(i, float):
            return "%0.2f" %i
        else:
            return str(i)

    def _safe_len(i):
        return len(re.sub('\\033\[\d+m', '',  _str(i)))

    def _safe_rjust(s, just):
        return (" " * (just - _safe_len(s))) + s

    vtype = None
    for v in rows:
        if vtype is not None and type(v) != vtype:
            raise ValueError("Mixed row types in input")
        else:
            vtype = type(v)

    lengths  = {}
    if vtype == list or vtype == tuple:
        v_len = len(fields) if fields else len(rows[0])

        if header and len(header)!=v_len:
            raise Exception("Bad header length")

        # Get max size of each field
        if not fields:
            fields = list(range(v_len))

        for i,iv in enumerate(fields):
            header_length = 0
            if header != []:
                #header_length = len(_str(header[i]))
                header_length = _safe_len(header[i])
            max_field_length = max( [_safe_len(r[iv]) for r in rows] )
            lengths[i] = max( [ header_length, max_field_length ] )

        if header and print_header:
            # Print >>Stdout, header names
            for i in range(len(fields)):
                print(_str(header[i]).rjust(lengths[i])+" | ", end=' ', file=stdout)
            print("", file=stdout)
            # Print >>Stdout, underlines
            for i in range(len(fields)):
                print("".rjust(lengths[i],"-")+" | ", end=' ', file=stdout)
            print("", file=stdout)
        # Print >>Stdout, table lines
        for r in rows:
            for i,iv in enumerate(fields):
                #print >>stdout, _str(r[iv]).rjust(lengths[i])+" | ",
                print(_safe_rjust(_str(r[iv]), lengths[i])+" | ", end=' ', file=stdout)
            print("", file=stdout)                

    elif vtype == dict:
        if header == []:
            header = list(rows[0].keys())
        for ppt in header:
            lengths[ppt] = max( [_safe_len(_str(ppt))]+[ _safe_len(_str(p.get(ppt,""))) for p in rows])
        if header:
            for ppt in header:
                print(_safe_rjust(_str(ppt), lengths[ppt])+" | ", end=' ', file=stdout)
            print("", file=stdout)
            for ppt in header:
                print("".rjust(lengths[ppt],"-")+" | ", end=' ', file=stdout)
            print("", file=stdout)

        for p in rows:
            for ppt in header:
                print(_safe_rjust(_str(p.get(ppt,""), lengths[ppt]))+" | ", end=' ', file=stdout)
            print("", file=stdout)
            page_counter +=1

def get_node2content(node, store=None):
    if not store: store = {}
    for ch in node.children:
        get_node2content(ch, store=store)

    if node.children:
        val = []
        for ch in node.children:
            val.extend(store[ch])
        store[node] = val
    else:
        store[node] = [node.name]
    return store

def iter_prepostorder(tree, is_leaf_fn=None):
        """
        EXPERIMENTAL
        """
        to_visit = [tree]
        if is_leaf_fn is not None:
            _leaf = is_leaf_fn
        else:
            _leaf = tree.__class__.is_leaf

        while to_visit:
            node = to_visit.pop(-1)
            try:
                node = node[1]
            except TypeError:
                # PREORDER ACTIONS
                yield (False, node)
                if not _leaf(node):
                    # ADD CHILDREN
                    to_visit.extend(reversed(node.children + [[1, node]]))
            else:
                #POSTORDER ACTIONS
                yield (True, node)

def send_mail_smtp(toaddrs, subject, msg):
    import smtplib

    fromaddr = "no-reply@yournprprocess.local"
    # The actual mail send
    client = smtplib.SMTP('localhost', 1025)
    client.sendmail(fromaddr, toaddrs, msg)
    client.quit()
    print("Mail sent to", toaddrs)

def send_mail(toaddrs, subject, text):
    try:
        from email.mime.text import MIMEText
        from subprocess import Popen, PIPE

        msg = MIMEText(text)
        msg["From"] = 'YourNPRprocess@hostname'
        msg["To"] = toaddrs
        msg["Subject"] = subject
        p = Popen(["/usr/sbin/sendmail", "-t"], stdin=PIPE)
        p.communicate(msg.as_string())
    except Exception as e:
        print(e)

def symlink(target, link_name):
    try:
        os.remove(link_name)
    except OSError:
        pass
    os.symlink(target, link_name)

def silent_remove(target):
    try:
        os.remove(target)
    except OSError:
        pass

def get_latest_nprdp(basedir):
    avail_dbs = []
    for fname in glob(os.path.join(basedir, "*.db")):
        m = re.search("npr\.([\d\.]+)\.db", fname)
        if m:
            avail_dbs.append([float(m.groups()[0]), fname])

    if avail_dbs:
        avail_dbs.sort()
        print(avail_dbs)
        if avail_dbs:
            last_db = avail_dbs[-1][1]
            print("Using latest db file available:", os.path.basename(last_db))
            return last_db
    else:
        #tries compressed data
        compressed_path = pjoin(basedir, "etebuild_data.tar.gz")
        if pexist(compressed_path):
            import tarfile
            tar = tarfile.open(compressed_path)
            for member in tar:
                print(member.name)
                m = re.search("npr\.([\d\.]+)\.db", member.name)
                if m:
                    print(member)
                    avail_dbs.append([float(m.groups()[0]), member])

    return None

def npr_layout(node):
    if node.is_leaf():
        name = faces.AttrFace("name", fsize=12)
        faces.add_face_to_node(name, node, 0, position="branch-right")
        if hasattr(node, "sequence"):
            seq_face = faces.SeqFace(node.sequence, [])
            faces.add_face_to_node(seq_face, node, 0, position="aligned")


    if "treemerger_type" in node.features:
        ttype=faces.AttrFace("tree_type", fsize=8, fgcolor="DarkBlue")
        faces.add_face_to_node(ttype, node, 0, position="branch-top")
        #ttype.background.color = "DarkOliveGreen"
        node.img_style["size"] = 20
        node.img_style["fgcolor"] = "red"

    if "alg_type" in node.features:
        faces.add_face_to_node(faces.AttrFace("alg_type", fsize=8), node, 0, position="branch-top")

    if "treemerger_rf" in node.features:
        faces.add_face_to_node(faces.AttrFace("treemerger_rf", fsize=8), node, 0, position="branch-bottom")

    support_radius= (1.0 - node.support) * 30
    if support_radius > 1:
        support_face = faces.CircleFace(support_radius, "red")
        faces.add_face_to_node(support_face, node, 0, position="float-behind")
        support_face.opacity = 0.25
        faces.add_face_to_node(faces.AttrFace("support", fsize=8), node, 0, position="branch-bottom")


    if "clean_alg_mean_identn" in node.features:
        identity = node.clean_alg_mean_identn
    elif "alg_mean_identn" in node.features:
        identity = node.alg_mean_identn

    if "highlighted" in node.features:
        node.img_style["bgcolor"] = "LightCyan"

    if "improve" in node.features:
        color = "orange" if float(node.improve) < 0 else "green"
        if float(node.improve) == 0:
            color = "blue"

        support_face = faces.CircleFace(200, color)
        faces.add_face_to_node(support_face, node, 0, position="float-behind")

try:
    from ... import TreeStyle, NodeStyle, faces
    from ...treeview import random_color
    NPR_TREE_STYLE = TreeStyle()
    NPR_TREE_STYLE.layout_fn = npr_layout
    NPR_TREE_STYLE.show_leaf_name = False
except ImportError:

    TreeStyle, NodeStyle, faces, random_color = [None]*4
    NPR_TREE_STYLE = None



# CONVERT shell colors to the same curses palette
COLORS = {
    "wr": '\033[1;37;41m', # white on red
    "wo": '\033[1;37;43m', # white on orange
    "wm": '\033[1;37;45m', # white on magenta
    "wb": '\033[1;37;46m', # white on blue
    "bw": '\033[1;37;40m', # black on white
    "lblue": '\033[1;34m', # light blue
    "lred": '\033[1;31m', # light red
    "lgreen": '\033[1;32m', # light green
    "yellow": '\033[1;33m', # yellow
    "cyan": '\033[36m', # cyan
    "blue": '\033[34m', # blue
    "green": '\033[32m', # green
    "orange": '\033[33m', # orange
    "red": '\033[31m', # red
    "magenta": "\033[35m", # magenta
    "white": "\033[0m", # white
    None: "\033[0m", # end
}

def colorify(string, color):
    return "%s%s%s" %(COLORS[color], string, COLORS[None])

def clear_color(string):
    return re.sub("\\033\[[^m]+m", "", string)

    
def iter_cog_seqs(cogs_file, spname_delimiter):
    cog_id = 0
    for line in open(cogs_file):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        cog_id += 1
        seq_cogs = []
        for seqname in [_ln.strip() for _ln in line.split('\t')]:
            try:
                spcode, seqcode = [_f.strip() for _f in seqname.split(spname_delimiter, 1)]
            except ValueError:
                raise DataError("Invalid sequence name in COGs file: %s" %seqname)
            else:
                seq_cogs.append((seqname, spcode, seqcode))
        yield cog_id, seq_cogs

# Added due to https://github.com/etetoolkit/ete/issues/335
def cmp(x, y):
    """cmp() exists in Python 2 but was removed in Python 3.
    This implements the same behavior on both versions.
    """
    return bool(x > y) - bool(x < y) 
