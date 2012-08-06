import time
from collections import defaultdict
import sqlite3
import cPickle
import base64
import logging
log = logging.getLogger("main")

conn = None
cursor = None

AUTOCOMMIT = False
def autocommit():
    if AUTOCOMMIT:
        conn.commit()

def encode(x):
    return base64.encodestring(cPickle.dumps(x, 2))

def decode(x):
    return cPickle.loads(base64.decodestring(x))

def init_db(dbname):
    connect(dbname)
    create_db()
   
def connect(dbname):
    global conn, cursor
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()

def parse_job_list(jobs):
    if isjob(jobs) or istask(jobs):
        jobs = [jobs]
    ids = ','.join(["'%s'" %j.jobid for j in jobs if isjob(j)] +
                   ["'%s'" %j.taskid for j in jobs if istask(j)])
    return jobs, ids
    
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
    PRIMARY KEY (nodeid, runid)
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

    CREATE TABLE IF NOT EXISTS task2child(
    taskid CHAR(32),
    child CHAR(32),
    PRIMARY KEY(taskid, child)
    );
    
    CREATE TABLE IF NOT EXISTS seqid2name(
    seqid CHAR(32) PRIMARY KEY,
    name VARCHAR(32)
    );

    CREATE TABLE IF NOT EXISTS ortho_pair(
    taxid1 VARCHAR(16), 
    seqid1 VARCHAR(16),
    taxid2 VARCHAR(16),
    seqid2 VARCHAR(16),
    score FLOAT DEFAULT(1.0),
    PRIMARY KEY(taxid1, seqid1, taxid2, seqid2)
    );

    CREATE TABLE IF NOT EXISTS nt_seq(
    seqid CHAR(10) PRIMARY KEY, 
    seq TEXT
    );

    CREATE TABLE IF NOT EXISTS aa_seq(
    seqid CHAR(10) PRIMARY KEY, 
    seq TEXT
    );
    
    CREATE INDEX IF NOT EXISTS i1 ON task(host, status);
    CREATE INDEX IF NOT EXISTS i2 ON task(nodeid, status);
    CREATE INDEX IF NOT EXISTS i3 ON task(parentid, status);
    CREATE INDEX IF NOT EXISTS i4 ON task(status, host, pid);

    CREATE INDEX IF NOT EXISTS i5 ON node(runid, cladeid);

    CREATE INDEX IF NOT EXISTS i6 ON ortho_pair (taxid1, taxid2, score);
    CREATE INDEX IF NOT EXISTS i7 ON ortho_pair (taxid1, seqid1, taxid2, seqid2, score);
    
    '''
    cursor.executescript(job_table)
    
def add_task(tid, nid, parent=None, status=None, type=None, subtype=None,
             name=None):
    values = ','.join(['"%s"' % (v or "") for v in
              [tid, nid, parent, status, type, subtype, name]])
    cmd = ('INSERT OR REPLACE INTO task (taskid, nodeid, parentid, status,'
           ' type, subtype, name) VALUES (%s);' %(values))
    execute(cmd)

    autocommit()
    
def add_task2child(tid, child):
    cmd = ('INSERT OR REPLACE INTO task2child (taskid, child)'
           ' VALUES ("%s", "%s");' %(tid, child))
    execute(cmd)
    autocommit()

def get_task2child_tree():
    cmd = """SELECT tree.taskid, child, task.type, task.subtype,
    task.name, task.status, node.cladeid FROM task2child AS tree
    LEFT OUTER JOIN task, node ON task.taskid = tree.child AND node.nodeid = task.nodeid
    """
    execute(cmd)
    return cursor.fetchall()

def get_species_name(spcode):
    return spcode
    
def update_task(tid, **kargs):
    if kargs:
        values = ', '.join(['%s="%s"' %(k,v) for k,v in
                       kargs.iteritems()])
        cmd = 'UPDATE task SET %s where taskid="%s";' %(values, tid)
        execute(cmd)
        autocommit()
        
def update_node(nid, runid, **kargs):
    if kargs:
        values = ', '.join(['%s="%s"' %(k,v) for k,v in
                       kargs.iteritems()])
        cmd = 'UPDATE node SET %s where nodeid="%s" AND runid="%s";' %\
              (values, nid, runid)
        execute(cmd)
        autocommit()
        
def get_task_status(tid):
    cmd = 'SELECT status FROM task WHERE taskid="%s"' %(tid)
    execute(cmd)
    return cursor.fetchone()

def get_task_info(tid):
    cmd = 'SELECT status, host, pid  FROM task WHERE taskid="%s"' %(tid)
    execute(cmd)
    values = cursor.fetchone()
    if values:
        keys = ["status", "host", "pid"]
        return dict(zip(keys, values))
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

def add_node(runid, nodeid, cladeid, target_seqs, out_seqs):
    values = ','.join(['"%s"' % (v or "") for v in
                       [nodeid, cladeid, encode(target_seqs),
                        encode(out_seqs), len(target_seqs),
                        len(out_seqs), runid]])
    cmd = ('INSERT OR REPLACE INTO node (nodeid, cladeid, target_seqs, out_seqs,'
           ' target_size, out_size, runid) VALUES (%s);' %(values))
    execute(cmd)
    autocommit()

def get_cladeid(nodeid):
    cmd = 'SELECT cladeid FROM node WHERE nodeid="%s"' %(nodeid)
    execute(cmd)
    return (cursor.fetchone() or [])[0]
       

def get_node_info(nodeid):
    cmd = ('SELECT cladeid, target_seqs, out_seqs FROM'
           ' node WHERE nodeid="%s"' %(nodeid))
    execute(cmd)
    cladeid, target_seqs, out_seqs = cursor.fetchone()
    target_seqs = decode(target_seqs)
    out_seqs = decode(out_seqs)
    return cladeid, target_seqs, out_seqs

def get_runid_nodes(runid):
    cmd = ('SELECT cladeid, newick, target_size FROM node'
           ' WHERE runid="%s" ORDER BY target_size DESC' %(runid))
    execute(cmd)
    return cursor.fetchall()
    
    
def report(runid, start=-40, max_records=40, filter_status=None):
    filters = "WHERE runid='%s' " %runid
    if filter_status:
        st = ','.join(map(lambda x: "'%s'"%x, list(filter_status)))
        if st:
            filters +=  "AND status NOT IN (%s)" %st
    
    cmd = ('SELECT task.taskid, task.nodeid, task.parentid, node.cladeid, task.status, type, subtype, name,'
           ' target_size, out_size, tm_end-tm_start, tm_start, tm_end FROM task '
           ' LEFT OUTER JOIN node ON task.nodeid = node.nodeid %s ORDER BY task.status ASC,target_size ASC;' %filters)

    execute(cmd)
    report = cursor.fetchall()
    end = start + max_records
    print start, end
    if end == 0:
        report = report[start:]
    else:
        report = report[start:end]

    return report

def add_seq_name(seqid, name):
    cmd = ('INSERT OR REPLACE INTO seqid2name (seqid, name)'
           ' VALUES ("%s", "%s");' %(seqid, name))
    execute(cmd)
    autocommit()

def get_seq_name(seqid):
    cmd = 'SELECT name FROM seqid2name WHERE seqid="%s"' %seqid
    execute(cmd)
    return (cursor.fetchone() or [seqid])[0]

def add_seq(seqid, seq, seqtype):
    cmd = 'INSERT OR REPLACE INTO %s_seq (seqid, seq) VALUES ("%s", "%s")' %(seqtype, seqid, seq)
    execute(cmd)
    autocommit()

def get_seq(seqid, seqtype):
    cmd = 'SELECT seq FROM %s_seq WHERE seqid = "%s";' %(seqtype, seqid)
    execute(cmd)
    return cursor.fetchone()[0]
        
    
def add_ortho_pair(taxid1, seqid1, taxid2, seqid2):
    cmd = ('INSERT OR REPLACE INTO ortho_pair (taxid1, seqid1, taxid2, seqid2)'
           ' VALUES ("%s", "%s", "%s", "%s");' %(taxid1, seqid1, taxid2, seqid2))
    execute(cmd)
    autocommit()
    
def get_all_task_states():
    cmd = 'SELECT status FROM task'
    execute(cmd)
    return [v[0] for v in cursor.fetchall()]
    
def commit():
    conn.commit()

def execute(cmd):
    for retry in xrange(3):
        try:
            s = cursor.execute(cmd)
        except sqlite3.OperationalError, e:
            log.warning(e)
            if retry > 1:
                raise
            time.sleep(1)
            retry +=1
        else:
            return s

