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
import time
from collections import defaultdict
import sqlite3
import six.moves.cPickle
import base64
import zlib
import gzip
import logging
from .utils import md5, pexist, pjoin, GLOBALS
import six
from six.moves import map
from six.moves import range
from six.moves import zip

log = logging.getLogger("main")

conn = None
cursor = None
seqconn = None
seqcursor = None
dataconn = None
datacursor = None

AUTOCOMMIT = False
def autocommit(targetconn = conn):
    if AUTOCOMMIT:
        targetconn.commit()

def encode(x):
    return bytes.decode(base64.encodestring(six.moves.cPickle.dumps(x, 2)))

def decode(x):
    if six.PY3:
        x = str.encode(x)
        
    return six.moves.cPickle.loads(base64.decodestring(x))

# SQLITE_MAX_LENGTH issue: files larger than ~1GB cannot be stored. limit cannot
# be changed at runtime. Big files are then stored in disk instead
# def zencode(x):
#     return base64.encodestring(zlib.compress(cPickle.dumps(x)))

# def zdecode(x):
#     return cPickle.loads(zlib.decompress(base64.decodestring(x)))

MAX_SQLITE_SIZE = 500000000
MAX_SQLITE_SIZE = 5

def zencode(x, data_id):
    pdata = six.moves.cPickle.dumps(x)
    if sys.getsizeof(pdata) > MAX_SQLITE_SIZE:
        # using protocol 2 fails because of the integer overflow python bug
        # i.e. http://bugs.python.org/issue13555
        six.moves.cPickle.dump(x, open(pjoin(GLOBALS['db_dir'], data_id+".pkl"), "wb"), protocol=1)
        return "__DBDIR__:%s" %data_id
    else:
        return base64.encodestring(zlib.compress(pdata))

def zdecode(x):
    if x.startswith("__DBDIR__:"):
        data_id = x.split(':', 1)[1]
        data = six.moves.cPickle.load(open(pjoin(GLOBALS['db_dir'], data_id+".pkl"), "rb"))
    else:
        data = six.moves.cPickle.loads(zlib.decompress(base64.decodestring(x)))
    return data

def prevent_sqlite_umask_bug(fname):
    # avoids using sqlite module to create the file with deafult 644 umask
    # permissions. Bug
    # http://www.mail-archive.com/sqlite-users@sqlite.org/msg59080.html
    if not pexist(fname):
        open(fname, "w").close()

def connect_nprdb(nprdb_file):
    global conn, cursor
    conn = sqlite3.connect(nprdb_file)
    cursor = conn.cursor()

def init_datadb(datadb_file):
    global dataconn, datacursor
    prevent_sqlite_umask_bug(datadb_file)
    dataconn = sqlite3.connect(datadb_file)
    datacursor = dataconn.cursor()
    create_data_db()

def init_nprdb(nprdb_file):
    global conn, cursor
    prevent_sqlite_umask_bug(nprdb_file)
    conn = sqlite3.connect(nprdb_file)
    cursor = conn.cursor()
    create_db()

def init_seqdb(seqdb_file):
    global seqconn, seqcursor
    prevent_sqlite_umask_bug(seqdb_file)
    seqconn = sqlite3.connect(seqdb_file)
    seqcursor = seqconn.cursor()
    create_seq_db()


def close():
    conn.close()
    seqconn.close()
    dataconn.close()


def parse_job_list(jobs):
    if isjob(jobs) or istask(jobs):
        jobs = [jobs]
    ids = ','.join(["'%s'" %j.jobid for j in jobs if isjob(j)] +
                   ["'%s'" %j.taskid for j in jobs if istask(j)])
    return jobs, ids


def create_data_db():
    data_table = '''
    CREATE TABLE IF NOT EXISTS task(
    taskid CHAR(32) PRIMARY KEY,
    type INTEGER,
    tasktype INTEGER,
    cmd BLOB,
    stdout BLOB,
    stderr BLOB,
    time BLOB,
    status CHAR(1)
    );

    CREATE TABLE IF NOT EXISTS task2data(
      taskid CHAR(32),
      datatype INTEGER,
      md5 CHAR(32),
      PRIMARY KEY(taskid, datatype)
    );

    CREATE TABLE IF NOT EXISTS data(
      md5 CHAR(32) PRIMARY KEY,
      data BLOB
    );

    '''
    # indexes are created while importing
    datacursor.executescript(data_table)
    autocommit(dataconn)

def get_dataid(taskid, datatype):
    cmd = """ SELECT md5 FROM task2data WHERE taskid="%s" AND datatype = "%s"
        """ %(taskid, datatype)
    datacursor.execute(cmd)
    try:
        return datacursor.fetchone()[0]
    except TypeError:
        raise ValueError("data not found")

def get_data(dataid):
    cmd = """ SELECT data.data FROM data WHERE md5="%s" """ %(dataid)
    datacursor.execute(cmd)
    return zdecode(datacursor.fetchone()[0])

def get_task_data(taskid, datatype):
    cmd = """ SELECT data FROM task2data as t LEFT JOIN data AS d ON(d.md5 = t.md5) WHERE taskid="%s" AND t.datatype = "%s"
        """ %(taskid, datatype)
    datacursor.execute(cmd)
    return zdecode(datacursor.fetchone()[0])

def task_is_saved(taskid):
    cmd = """ SELECT status FROM task WHERE taskid="%s" """ %taskid
    datacursor.execute(cmd)
    try:
        st = datacursor.fetchone()[0]
    except TypeError:
        return False
    else:
        return True if st =="D" else False

def add_task_data(taskid, datatype, data, duplicates="OR IGNORE"):
    data_id = md5(str(data))
    cmd = """ INSERT %s INTO task (taskid, status) VALUES
    ("%s", "D") """ %(duplicates, taskid)
    datacursor.execute(cmd)

    cmd = """ INSERT %s INTO task2data (taskid, datatype, md5) VALUES
    ("%s", "%s", "%s") """ %(duplicates, taskid, datatype, data_id)
    datacursor.execute(cmd)
    cmd = """ INSERT %s INTO data (md5, data) VALUES
    ("%s", "%s") """ %(duplicates, data_id, zencode(data, data_id))
    datacursor.execute(cmd)
    autocommit()
    return data_id

def register_task_data(taskid, datatype, data_id, duplicates="OR IGNORE"):
    cmd = """ INSERT %s INTO task2data (taskid, datatype, md5) VALUES
    ("%s", "%s", "%s") """ %(duplicates, taskid, datatype, data_id)
    datacursor.execute(cmd)
    autocommit()
    return data_id


def create_seq_db():
    seq_table ='''
    CREATE TABLE IF NOT EXISTS nt_seq(
    seqid CHAR(10) PRIMARY KEY,
    seq TEXT
    );

    CREATE TABLE IF NOT EXISTS aa_seq(
    seqid CHAR(10) PRIMARY KEY,
    seq TEXT
    );

    CREATE TABLE IF NOT EXISTS seqid2name(
    seqid CHAR(32) PRIMARY KEY,
    name VARCHAR(32)
    );

    CREATE TABLE IF NOT EXISTS species(
      taxid VARCHAR(16) PRIMARY KEY,
      size INT
    );

    CREATE INDEX IF NOT EXISTS i6 ON seqid2name(name);
    '''
    seqcursor.executescript(seq_table)
    autocommit(seqconn)

def create_db():
    job_table = '''
    CREATE TABLE IF NOT EXISTS node(
    nodeid CHAR(32),
    runid CHAR(32),
    cladeid CHAR(32),
    target_seqs TEXT,
    out_seqs TEXT,
    target_size INTEGER,
    out_size INTEGER,
    newick BLOB,
    PRIMARY KEY (runid, nodeid)
    );

    CREATE TABLE IF NOT EXISTS task(
    taskid CHAR(32) PRIMARY KEY,
    nodeid CHAR(32),
    parentid CHAR(32),
    status CHAR(1),
    type VARCHAR,
    subtype VARCHAR,
    name VARCHAR,
    host VARCHAR,
    pid VARCHAR,
    cores INTEGER,
    tm_start FLOAT,
    tm_end FLOAT
    );

    CREATE TABLE IF NOT EXISTS runid2task(
    runid CHAR(32),
    taskid CHAR(32),
    PRIMARY KEY(runid, taskid)
    );


    CREATE INDEX IF NOT EXISTS i1 ON task(host, status);
    CREATE INDEX IF NOT EXISTS i2 ON task(nodeid, status);
    CREATE INDEX IF NOT EXISTS i3 ON task(parentid, status);
    CREATE INDEX IF NOT EXISTS i4 ON task(status, host, pid);
    CREATE INDEX IF NOT EXISTS i5 ON node(runid, cladeid);

'''
    cursor.executescript(job_table)
    autocommit()


def add_task(tid, nid, parent=None, status=None, type=None, subtype=None,
             name=None):
    values = ','.join(['"%s"' % (v or "") for v in
              [tid, nid, parent, status, type, subtype, name]])
    cmd = ('INSERT OR REPLACE INTO task (taskid, nodeid, parentid, status,'
           ' type, subtype, name) VALUES (%s);' %(values))
    execute(cmd)
    autocommit()

def add_runid2task(runid, tid):
    cmd = ('INSERT OR REPLACE INTO runid2task (runid, taskid)'
           ' VALUES ("%s", "%s");' %(runid, tid))
    execute(cmd)
    autocommit()

def get_runid_tasks(runid):

    cmd = ('SELECT taskid FROM runid2task'
           ' WHERE runid = "%s";' %(runid))
    execute(cmd)
    return [e[0] for e in cursor.fetchall()]


def update_task(tid, **kargs):
    if kargs:
        values = ', '.join(['%s="%s"' %(k,v) for k,v in
                       six.iteritems(kargs)])
        cmd = 'UPDATE task SET %s where taskid="%s";' %(values, tid)
        execute(cmd)
        autocommit()

def update_node(nid, runid, **kargs):
    if kargs:
        values = ', '.join(['%s="%s"' %(k,v) for k,v in
                       six.iteritems(kargs)])
        cmd = 'UPDATE node SET %s where nodeid="%s" AND runid="%s";' %\
              (values, nid, runid)
        execute(cmd)
        autocommit()

def get_last_task_status(tid):
    cmd = 'SELECT status FROM task WHERE taskid="%s"' %(tid)
    execute(cmd)
    return cursor.fetchone()[0]

def get_task_info(tid):
    cmd = 'SELECT status, host, pid  FROM task WHERE taskid="%s"' %(tid)
    execute(cmd)
    values = cursor.fetchone()
    if values:
        keys = ["status", "host", "pid"]
        return dict(list(zip(keys, values)))
    else:
        return {}

def get_sge_tasks():
    cmd = ('SELECT taskid, pid FROM task WHERE host="@sge" '
           ' AND status IN ("Q", "R", "L");')
    execute(cmd)
    values = cursor.fetchall()
    pid2jobs = defaultdict(list)
    for tid, pid in values:
        pid2jobs[pid].append(tid)
    return pid2jobs

def add_node(runid, nodeid, cladeid, targets, outgroups):
    values = ','.join(['"%s"' % (v or "") for v in
                       [nodeid, cladeid, encode(targets),
                        encode(outgroups), len(targets),
                        len(outgroups), runid]])
    cmd = ('INSERT OR REPLACE INTO node (nodeid, cladeid, target_seqs, out_seqs,'
           ' target_size, out_size, runid) VALUES (%s);' %(values))
    execute(cmd)
    autocommit()

def get_cladeid(nodeid):
    cmd = 'SELECT cladeid FROM node WHERE nodeid="%s"' %(nodeid)
    execute(cmd)
    return (cursor.fetchone() or [])[0]

def get_node_info(threadid, nodeid):
    cmd = ('SELECT cladeid, target_seqs, out_seqs FROM'
           ' node WHERE runid="%s" AND nodeid="%s"' %(threadid,
           nodeid))

    execute(cmd)
    cladeid, targets, outgroups = cursor.fetchone()
    targets = decode(targets)
    outgroups = decode(outgroups)
    return cladeid, targets, outgroups

def print_node_by_clade(threadid, cladeid):
    cmd = ('SELECT nodeid, target_seqs, out_seqs, newick FROM'
           ' node WHERE runid="%s" AND cladeid="%s"' %(threadid,
           cladeid))

    execute(cmd)
    newicks = []
    for nodeid, targets, outgroups, newick in cursor.fetchall():
        targets = decode(targets)
        outgroups = decode(outgroups)
        if newick:
            print(threadid, nodeid, len(targets), len(outgroups),len(decode(newick)))
            return targets, outgroups
        else:
            print()

def get_runid_nodes(runid):
    cmd = ('SELECT cladeid, newick, target_size FROM node'
           ' WHERE runid="%s" ORDER BY target_size DESC' %(runid))
    execute(cmd)
    return cursor.fetchall()

def report(runid, filter_rules=None):
    task_ids = get_runid_tasks(runid)
    #filters = 'WHERE runid ="%s" AND taskid IN (%s) ' %(runid,
    #                        ','.join(map(lambda x: '"%s"' %x, task_ids)))
    # There is a single npr.db file per runid
    filters = 'WHERE runid ="%s" ' %(runid)

    if filter_rules:
        custom_filter = ' AND '.join(filter_rules)
        filters += " AND " + custom_filter
    cmd = ('SELECT task.taskid, task.nodeid, task.parentid, node.cladeid, task.status, type, subtype, name,'
           ' target_size, out_size, tm_end-tm_start, tm_start, tm_end FROM task '
           ' LEFT JOIN node ON task.nodeid = node.nodeid %s ' %filters)
    #ORDER BY task.status ASC,target_size DESC;
    execute(cmd)
    report = cursor.fetchall()
    return report

def add_seq_name(seqid, name):
    cmd = ('INSERT OR REPLACE INTO seqid2name (seqid, name)'
           ' VALUES ("%s", "%s");' %(seqid, name))
    execute(cmd, seqcursor)
    autocommit()

def add_seq_name_table(entries):
    cmd = 'INSERT OR REPLACE INTO seqid2name (seqid, name) VALUES (?, ?)'
    seqcursor.executemany(cmd, entries)
    autocommit()

def get_seq_name(seqid):
    cmd = 'SELECT name FROM seqid2name WHERE seqid="%s"' %seqid
    execute(cmd, seqcursor)
    return (seqcursor.fetchone() or [seqid])[0]

def get_seq_name_dict():
    cmd = 'SELECT name, seqid FROM seqid2name'
    execute(cmd, seqcursor)
    return dict(seqcursor.fetchall())

    
def get_all_seq_names():
    cmd = 'SELECT name FROM seqid2name'
    execute(cmd, seqcursor)
    return set([name[0] for name in seqcursor.fetchall()])

def translate_names(names):
    name_string = ",".join(['"%s"'%x for x in names])
    cmd = 'SELECT name, seqid FROM seqid2name WHERE name in (%s);' %name_string
    execute(cmd, seqcursor)
    return dict(seqcursor.fetchall())

def get_all_seqids(seqtype):
    cmd = 'SELECT seqid FROM %s_seq;' %seqtype
    execute(cmd, seqcursor)
    seqids = set()
    for sid in seqcursor.fetchall():
        seqids.add(sid[0])
    return seqids

def add_seq(seqid, seq, seqtype):
    cmd = 'INSERT OR REPLACE INTO %s_seq (seqid, seq) VALUES ("%s", "%s")' %(seqtype, seqid, seq)
    execute(cmd, seqcursor)
    autocommit(seqconn)

def add_seq_table(entries, seqtype):
    cmd = 'INSERT OR REPLACE INTO %s_seq (seqid, seq) VALUES (?, ?)' %seqtype
    seqcursor.executemany(cmd, entries)
    autocommit(seqconn)

def get_seq(seqid, seqtype):
    cmd = 'SELECT seq FROM %s_seq WHERE seqid = "%s";' %(seqtype, seqid)
    execute(cmd, seqcursor)
    return seqcursor.fetchone()[0]

    
def get_seq_species():
    cmd = 'SELECT DISTINCT taxid FROM species;'
    execute(cmd, seqcursor)
    species = set([name[0] for name in seqcursor.fetchall()])
    return species

def add_seq_species(species):
    cmd = 'INSERT OR REPLACE INTO species (taxid, size) VALUES (?, ?)'
    seqcursor.executemany(cmd, [[sp, counter] for sp, counter in
                                six.iteritems(species)])
    autocommit()


def get_all_task_states():
    cmd = 'SELECT status FROM task'
    execute(cmd)
    return [v[0] for v in cursor.fetchall()]

def execute(cmd, dbcursor=None):
    if not dbcursor:
        dbcursor = cursor
    for retry in range(10):
        try:
            s = dbcursor.execute(cmd)
        except sqlite3.OperationalError as e:
            log.warning(e)
            if retry > 1:
                raise
            time.sleep(1)
            retry +=1
        else:
            return s

def commit(dbconn=None):
    if not dbconn:
        dbconn = conn
    conn.commit()

