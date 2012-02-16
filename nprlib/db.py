from collections import defaultdict
import sqlite3
import cPickle
import base64

conn = None
cursor = None

AUTOCOMMIT = False
def autocommit():
    if AUTOCOMMIT:
        conn.commit()

def encode(x):
    return base64.encodestring(cPickle.dumps(x))

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
    nodeid CHAR(32) PRIMARY KEY,
    cladeid CHAR(32),
    target_seqs TEXT,
    out_seqs TEXT,
    target_size INTEGER,
    out_size INTEGER,
        
    current_task CHAR(32)
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

    CREATE TABLE IF NOT EXISTS seqid2name(
    seqid CHAR(32) PRIMARY KEY,
    name VARCHAR(256)
    );

    
    CREATE INDEX IF NOT EXISTS i1 ON task(host, status);
    CREATE INDEX IF NOT EXISTS i2 ON task(nodeid, status);
    CREATE INDEX IF NOT EXISTS i3 ON task(parentid, status);
    CREATE INDEX IF NOT EXISTS i4 ON task(status, host, pid);
        
    
    '''
    cursor.executescript(job_table)
    
def add_task(tid, nid, parent=None, status=None, type=None, subtype=None,
             name=None):
    values = ','.join(['"%s"' % (v or "") for v in
              [tid, nid, parent, status, type, subtype, name]])
    cmd = ('INSERT INTO task (taskid, nodeid, parentid, status,'
           ' type, subtype, name) VALUES (%s);' %(values))
    cursor.execute(cmd)

    autocommit()

def update_task(tid, **kargs):
    if kargs:
        values = ', '.join(['%s="%s"' %(k,v) for k,v in
                       kargs.iteritems()])
        cmd = 'UPDATE task SET %s where taskid="%s";' %(values, tid)
        cursor.execute(cmd)
        autocommit()

def get_task_status(tid):
    cmd = 'SELECT status FROM task WHERE taskid="%s"' %(tid)
    cursor.execute(cmd)
    return cursor.fetchone()

def get_task_info(tid):
    cmd = 'SELECT status, host, pid  FROM task WHERE taskid="%s"' %(tid)
    cursor.execute(cmd)
    values = cursor.fetchone()
    if values:
        keys = ["status", "host", "pid"]
        return dict(zip(keys, values))
    else:
        return {}

def get_sge_tasks():
    cmd = ('SELECT taskid, pid FROM task WHERE host="@sge" '
           ' AND status IN ("Q", "R", "L");')
    cursor.execute(cmd)
    values = cursor.fetchall()
    pid2jobs = defaultdict(list)
    for tid, pid in values:
        pid2jobs[pid].append(tid)
    return pid2jobs

def add_node(nodeid, cladeid, target_seqs, out_seqs):
    values = ','.join(['"%s"' % (v or "") for v in
                       [nodeid, cladeid, encode(target_seqs),
                        encode(out_seqs), len(target_seqs),
                        len(out_seqs)]])
    cmd = ('INSERT INTO node (nodeid, cladeid, target_seqs, out_seqs,'
           ' target_size, out_size) VALUES (%s);' %(values))
    cursor.execute(cmd)
    autocommit()

def get_cladeid(nodeid):
    cmd = 'SELECT cladeid FROM node WHERE nodeid="%s"' %(nodeid)
    cursor.execute(cmd)
    return (cursor.fetchone() or [])[0]
       

def get_node_info(nodeid):
    cmd = ('SELECT cladeid, target_seqs, out_seqs FROM'
           ' node WHERE nodeid="%s"' %(nodeid))
    cursor.execute(cmd)
    cladeid, target_seqs, out_seqs = cursor.fetchone()
    target_seqs = decode(target_seqs)
    out_seqs = decode(out_seqs)
    return cladeid, target_seqs, out_seqs


    
def report(max_records=40):
    cmd = ('SELECT task.taskid, task.nodeid, task.parentid, node.cladeid, task.status, type, subtype, name,'
           ' target_size, out_size, TIME(tm_start), TIME(tm_end) FROM task '
           ' left outer join node ON task.nodeid = node.nodeid;')
    cursor.execute(cmd)
    report = cursor.fetchall()[-max_records:]
    return report

def add_seq_name(seqid, name):
    cmd = ('INSERT INTO seqid2name (seqid, name)'
           ' VALUES ("%s", "%s");' %(seqid, name))
    cursor.execute(cmd)
    autocommit()

def get_seq_name(seqid):
    cmd = 'SELECT name FROM seqid2name WHERE seqid="%s"' %seqid
    cursor.execute(cmd)
    return (cursor.fetchone() or [seqid])[0]

def get_all_task_states():
    cmd = 'SELECT status FROM task'
    cursor.execute(cmd)
    return [v[0] for v in cursor.fetchall()]
    
def commit():
    conn.commit()