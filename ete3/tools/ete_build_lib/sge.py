from __future__ import absolute_import
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
import sys
import os
import time
import re
from collections import defaultdict
from commands import getoutput as run


import logging
import six
from six.moves import map
log = logging.getLogger("main")

from . import db
from .errors import SgeError
from .utils import GLOBALS
OK_PATTERN = 'Your job-array ([\d]+).\d+\-\d+:\d+ \("[^"]*"\) has been submitted'
DEFAULT_SGE_CELL = "cgenomics"

def launch_jobs(jobs, conf):
    # Group jobs with identical config
    sge_path = GLOBALS["sge_dir"]

    conf2jobs = defaultdict(list)
    for j, cmd in jobs:
        job_config = conf["sge"].copy()
        job_config["-pe smp"] = j.cores
        for k,v in six.iteritems(j.sge):
            job_config[k] = v
        conf_key = tuple(sorted(job_config.items()))
        conf2jobs[conf_key].append((j,cmd))

    for job_config, commands in six.iteritems(conf2jobs):
        job_config = dict(job_config)
        job_file = "%s_%d_jobs" %(time.ctime().replace(" ", "_").replace(":","-"),
                                  len(commands))
        cmds_file = os.path.join(sge_path, job_file+".cmds")
        qsub_file = os.path.join(sge_path, job_file+".qsub")

        script =  '''#!/bin/sh\n'''
        for k,v in six.iteritems(job_config):
            if not k.startswith("_"):
                script += '#$ %s %s\n' %(k,v)
        script += '#$ -f \n'
        script += '#$ -o %s\n' % sge_path
        script += '#$ -e %s\n' % sge_path
        script += '#$ -N %s\n' % "NPR%djobs" %len(commands)
        script += '#$ -t 1-%d\n' % len(commands)
        script += 'SEEDFILE=%s\n' % cmds_file
        script += 'sh -c "`cat $SEEDFILE | head -n $SGE_TASK_ID | tail -n 1`" \n'

        open(cmds_file, "w").write('\n'.join([cmd for j,cmd in commands]))
        open(qsub_file, "w").write(script)

        log.log(28, "Launching %d SGE jobs." %len(commands))
        log.debug(script)
        answer = run("SGE_CELL=%s qsub %s" %(job_config["_cell"], qsub_file))
        log.debug(answer)
        match =  re.search(OK_PATTERN, answer)
        if match:
            jobid = match.groups()[0]
            for j, cmd in commands:
                db.update_task(j.jobid, status = "Q", host="@sge", pid=jobid)
        else:
            raise SgeError(answer)

def queue_has_jobs(sge_cell=DEFAULT_SGE_CELL, queue=None):
    if queue:
        resource = "-q %s" %queue
    else:
        resource = ""
    rawoutput = commands.getoutput("SGE_CELL=%s qstat %s" %(sge_cell, resource))
    if rawoutput:
        return len(rawoutput.split("\n"))
    else:
        return 0

def qstat(sge_cell=DEFAULT_SGE_CELL):
    ### OUTPUT EXAMPLE:
    ##
    ## job-ID  prior   name       user         state submit/start at     queue                          slots ja-task-ID
    ## -----------------------------------------------------------------------------------------------------------------
    ## 127 0.30007 tmpYW50Rl  jhuerta      r     07/15/2010 18:51:41 cgenomics@gen18.crg.es             1 141
    ## 127 0.30007 tmpYW50Rl  jhuerta      r     07/15/2010 18:51:41 cgenomics@gen19.crg.es             1 142
    ## 127 0.30007 tmpYW50Rl  jhuerta      r     07/15/2010 18:51:41 cgenomics@gen14.crg.es             1 143
    ## 127 0.30007 tmpYW50Rl  jhuerta      r     07/15/2010 18:51:41 cgenomics@gen20.crg.es             1 144
    ## 127 0.30002 tmpYW50Rl  jhuerta      qw    07/15/2010 18:51:35                                    1 145-1038:1

    #rawoutput = commands.getoutput("SGE_CELL=%s qstat" %(sge_cell))
    rawoutput = run("qstat")
    jobs = []
    proc = []
    for line in rawoutput.split("\n")[2:]:
        fields = list(map(str.strip, line.split()))
        if len(fields)==9:
            jobs.append(fields)
        elif len(fields)==10:
            proc.append(fields)

    job2info = {}
    for (jobid, prior, name, user, state, stime,
         slots, slot_ja, slot_ta) in jobs:
        job2info[jobid] = {"prior":prior, "name":name, "user":user,
                           "state":state, "stime":stime,
                           "ja":slot_ja, "ta":slot_ta }

    for (jobid, prior, name, user, state, stime, queue,
         slots, slot_ja, slot_ta) in proc:
        if jobid not in job2info:
            job2info[jobid] = {"prior":prior, "name":name, "user":user,
                               "state":state, "stime":stime, "queue":queue,
                               "ja":slot_ja, "ta":slot_ta }

    return job2info

def cancel_job(jobid):
    pass

def clean_job_outputs(jobid):
    pass

