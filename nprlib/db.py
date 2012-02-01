from collections import defaultdict
import sqlite3
conn = None
cursor = None

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
    CREATE TABLE IF NOT EXISTS job (
    jid CHAR(32) PRIMARY KEY,
    jtype VARCHAR,
    status CHAR,
    host VARCHAR,
    pid VARCHAR
    );

    CREATE TABLE IF NOT EXISTS task (
    tid CHAR(32) PRIMARY KEY,
    ttype VARCHAR,
    status CHAR
    );

    CREATE INDEX IF NOT EXISTS job_host_index ON job(host, status);
    '''
  
    cursor.executescript(job_table)
    
def update_task(tid, **kargs):
    values = []
    for k,v in kargs.iteritems():
        values.append("%s='%s'" %(k,v))
    values = ','.join(values)
    cmd = 'UPDATE task SET %s where tid="%s";' %(values, tid)
    cursor.execute(cmd)
    conn.commit()
    
def add_task(tid, **kargs):
    cmd = 'INSERT INTO task (tid) VALUES ("%s")' %(tid)
    cursor.execute(cmd)
    conn.commit()
    update_task(tid, **kargs)
    
def get_task_status(tid):
    cmd = 'SELECT status FROM task WHERE tid="%s"' %(tid)
    cursor.execute(cmd)
    return cursor.fetchone()

def update_job(jid, **kargs):
    values = []
    for k,v in kargs.iteritems():
        values.append("%s='%s'" %(k,v))
    values = ','.join(values)
    cmd = 'UPDATE job SET %s where jid="%s";' %(values, jid)
    cursor.execute(cmd)
    conn.commit()
    
def add_job(jid, **kargs):
    cmd = 'INSERT INTO job (jid) VALUES ("%s")' %(jid)
    cursor.execute(cmd)
    conn.commit()
    update_job(jid, **kargs)
    
def get_job_status(jid):
    cmd = 'SELECT status FROM job WHERE jid="%s"' %(jid)
    cursor.execute(cmd)
    return cursor.fetchone()

def get_job_info(jid):
    cmd = 'SELECT status, host, pid  FROM job WHERE jid="%s"' %(jid)
    cursor.execute(cmd)
    values = cursor.fetchone()
    if values:
        keys = ["status", "host", "pid"]
        return dict(zip(keys, values))
    else:
        return {}

def get_sge_jobids():
    cmd = 'SELECT jid, pid FROM job WHERE host="@sge" and status IN ("Q", "R", "L");'
    cursor.execute(cmd)
    values = cursor.fetchall()
    pid2jobs = defaultdict(list)
    for jid, pid in values:
        pid2jobs[pid].append(jid)
    return pid2jobs
        
def commit():
    conn.commit()