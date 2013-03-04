import time
from collections import defaultdict
import sqlite3
import cPickle
import base64
import logging
log = logging.getLogger("main")

conn = None
cursor = None
seqconn = None
seqcursor = None
orthoconn = None
orthocursor = None

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

def connect2(seq_dbfile, npr_dbfile, ortho_dbfile):
    global conn, cursor
    conn = sqlite3.connect(npr_dbfile)
    cursor = conn.cursor()
    seqconn = sqlite3.connect(seq_dbfile)
    seqcursor = conn.cursor()
    orthoconn = sqlite3.connect(ortho_dbfile)
    orthocursor = conn.cursor()
      
def connect(dbname):
    global conn, cursor
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()

def close():
    conn.close()
    
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
    
    CREATE TABLE IF NOT EXISTS seqid2name(
    seqid CHAR(32) PRIMARY KEY,
    name VARCHAR(32)
    );

    CREATE TABLE IF NOT EXISTS species(
    name CHAR(32) PRIMARY KEY
    );

    CREATE TABLE IF NOT EXISTS ortho_pair(
    taxid1 VARCHAR(16), 
    seqid1 VARCHAR(16),
    taxid2 VARCHAR(16),
    seqid2 VARCHAR(16),
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
    CREATE INDEX IF NOT EXISTS i6 ON seqid2name(name);

'''
    cursor.executescript(job_table)
    autocommit()

def create_ortho_pair_indexes():
    ortho_indexes = '''
    CREATE INDEX IF NOT EXISTS i8 ON ortho_pair (taxid1, seqid1, taxid2);
    CREATE INDEX IF NOT EXISTS i9 ON ortho_pair (taxid1, taxid2);
    '''
    cursor.executescript(ortho_indexes)

def override_ortho_pair_table():
    cmd = """
    DROP TABLE IF EXISTS ortho_pair;

    CREATE TABLE IF NOT EXISTS ortho_pair(
    taxid1 VARCHAR(16), 
    seqid1 VARCHAR(16),
    taxid2 VARCHAR(16),
    seqid2 VARCHAR(16),
    PRIMARY KEY(taxid1, seqid1, taxid2, seqid2)
    );
    """
    cursor.executescript(cmd)
    autocommit()

def override_seq_tables():
    cmd = """
    DROP TABLE IF EXISTS nt_seq;
    DROP TABLE IF EXISTS aa_seq;

    CREATE TABLE IF NOT EXISTS nt_seq(
    seqid CHAR(10) PRIMARY KEY, 
    seq TEXT
    );

    CREATE TABLE IF NOT EXISTS aa_seq(
    seqid CHAR(10) PRIMARY KEY, 
    seq TEXT
    );

    """
    cursor.executescript(cmd)
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

def get_runid_nodes(runid):
    cmd = ('SELECT cladeid, newick, target_size FROM node'
           ' WHERE runid="%s" ORDER BY target_size DESC' %(runid))
    execute(cmd)
    return cursor.fetchall()
    
def report(runid, filter_rules=None):
    task_ids = get_runid_tasks(runid)
    filters = 'WHERE runid ="%s" AND taskid IN (%s) ' %(runid,
                            ','.join(map(lambda x: '"%s"' %x, task_ids)))
    if filter_rules: 
        custom_filter = ' AND '.join(filter_rules)
        filters += " AND " + custom_filter
    cmd = ('SELECT task.taskid, task.nodeid, task.parentid, node.cladeid, task.status, type, subtype, name,'
           ' target_size, out_size, tm_end-tm_start, tm_start, tm_end FROM task '
           ' LEFT OUTER JOIN node ON task.nodeid = node.nodeid %s ' %filters)
    #ORDER BY task.status ASC,target_size DESC;
    execute(cmd)
    report = cursor.fetchall()
    return report
    
def add_seq_name(seqid, name):
    cmd = ('INSERT OR REPLACE INTO seqid2name (seqid, name)'
           ' VALUES ("%s", "%s");' %(seqid, name))
    execute(cmd)
    autocommit()
    
def add_seq_name_table(entries):
    cmd = 'INSERT OR REPLACE INTO seqid2name (seqid, name) VALUES (?, ?)'
    cursor.executemany(cmd, entries)
    autocommit()
    
def get_seq_name(seqid):
    cmd = 'SELECT name FROM seqid2name WHERE seqid="%s"' %seqid
    execute(cmd)
    return (cursor.fetchone() or [seqid])[0]

def get_all_seq_names():
    cmd = 'SELECT name FROM seqid2name'
    execute(cmd)
    return [name[0] for name in cursor.fetchall()]

def translate_names(names):
    name_string = ",".join(map(lambda x: '"%s"'%x, names))
    cmd = 'SELECT name, seqid FROM seqid2name WHERE name in (%s);' %name_string
    execute(cmd)
    return dict(cursor.fetchall())

def get_all_seqids(seqtype):
    cmd = 'SELECT seqid FROM %s_seq;' %seqtype
    execute(cmd)
    seqids = set()
    for sid in cursor.fetchall():
        seqids.add(sid[0])
    return seqids
    
def add_seq(seqid, seq, seqtype):
    cmd = 'INSERT OR REPLACE INTO %s_seq (seqid, seq) VALUES ("%s", "%s")' %(seqtype, seqid, seq)
    execute(cmd)
    autocommit()

def add_seq_table(entries, seqtype):
    cmd = 'INSERT OR REPLACE INTO %s_seq (seqid, seq) VALUES (?, ?)' %seqtype
    cursor.executemany(cmd, entries)
    autocommit()
    
def get_seq(seqid, seqtype):
    cmd = 'SELECT seq FROM %s_seq WHERE seqid = "%s";' %(seqtype, seqid)
    execute(cmd)
    return cursor.fetchone()[0]
   
def get_species_in_ortho_pairs():
    cmd = 'SELECT DISTINCT taxid1, taxid2 FROM ortho_pair;'
    execute(cmd)
    species = set()
    for t1, t2 in cursor.fetchall():
        species.update([t1, t2])
    return species

def get_target_species():
    cmd = 'SELECT DISTINCT name FROM species;'
    execute(cmd)
    species = set([name[0] for name in cursor.fetchall()])
    return species

def add_target_species(species):
    cmd = 'INSERT OR REPLACE INTO species (name) VALUES (?)'
    cursor.executemany(cmd, [[sp] for sp in species])
    autocommit()

def get_all_ortho_seqs(target_species=None):
    if target_species: 
        sp_filter = "WHERE taxidNNN in (%s) " %(','.join(map(lambda n: '"%s"'%n )))
    else:
        sp_filter = ""
    
    cmd = 'SELECT DISTINCT seqid1,taxid1 FROM ortho_pair ' + sp_filter.replace("NNN","1")
    print cmd
    execute(cmd)
    seqs = set(["_".join(q) for q in cursor.fetchall()])

    cmd = 'SELECT DISTINCT seqid2,taxid2 FROM ortho_pair ' + sp_filter.replace("NNN","2")
    execute(cmd)
    print cmd
    seqs.update(set(["_".join(q) for q in cursor.fetchall()]))
    return seqs
    
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

