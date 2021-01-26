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
import os
import shutil
import re
#from . import sge
from . import db
import logging
import six
from six.moves import map
log = logging.getLogger("main")

from .utils import (md5, basename, pid_up, HOSTNAME,
                    GLOBALS, TIME_FORMAT, pjoin)

class Job(object):
    ''' A generic program launcher.

    A job is executed and monitored. Execution time, standard output
    and error are tracked into log files. The final status of the
    application is also logged. Possible status for process status are
    (W)aiting, (R)unning, (E)rror and (D)one.

    Each job generates the following info files:

      self.status_file = join(self.jobdir, "__status__")
      self.time_file = join(self.jobdir, "__time__")
      self.stdout_file = join(self.jobdir, "__stdout__")
      self.stderr_file = join(self.jobdir, "__stderr__")
      self.pid_file = join(self.jobdir, "__pid__")

    In addition, job launching command is stored in:

      self.cmd_file = join(self.jobdir, "__cmd__")

    '''
    def __repr__(self):
        return "Job (%s, %s)" %(self.jobname, self.jobid[:6])

    def __init__(self, bin, args, jobname=None, parent_ids=None):
        # Used at execution time
        self.status = None
        # How to run the app
        self.bin = bin
        # command line arguments
        self.args = args
        # Default number of cores used by the job. If more than 1,
        # this attribute should be changed
        self.cores = 1
        self.exec_type = "insitu"
        self.jobname = jobname

        # generates the unique job identifier based on the params of
        # the app. Some params include path names that can prevent
        # recycling the job, so a clean it.
        clean = lambda x: basename(x) if GLOBALS["basedir"] in x or GLOBALS["tasks_dir"] in x else x
        parsed_id_string = ["%s %s" %(clean(str(pair[0])), clean(str(pair[1])))
                            for pair in six.iteritems(self.args)]
        #print '\n'.join(map(str, self.args.items()))

        self.jobid = md5(','.join(sorted([md5(e) for e in
                                          parsed_id_string])))
        # self.jobid = md5(','.join(sorted([md5(str(pair)) for pair in
        #                                  self.args.iteritems()])))
        if parent_ids:
            self.jobid = md5(','.join(sorted(parent_ids+[self.jobid])))

        if not self.jobname:
            self.jobname = re.sub("[^0-9a-zA-Z]", "-", basename(self.bin))

        self.ifdone_cmd = ""
        self.iffail_cmd = ""
        self.set_jobdir(pjoin(GLOBALS["tasks_dir"], self.jobid))
        self.input_files = {}
        self.dependencies = set()

    def add_input_file(self, ifile, outpath = None):
        self.input_files[ifile] = outpath

    def set_jobdir(self, basepath):
        ''' Initialize the base path for all info files associated to
        the job. '''
        #self.jobdir = os.path.join(basepath, self.jobid)
        #jobname = "%s_%s" %(basename(self.bin), self.jobid[:6])
        #jobname = re.sub("[^0-9a-zA-Z]", "-",jobname)
        #self.jobdir = os.path.join(basepath, "%s_%s" %\
        #                               (self.jobname, self.jobid[:6]))

        self.jobdir = basepath
        #if not os.path.exists(self.jobdir):
        #    os.makedirs(self.jobdir)
        self.status_file = os.path.join(self.jobdir, "__status__")
        self.time_file = os.path.join(self.jobdir, "__time__")
        self.cmd_file = os.path.join(self.jobdir, "__cmd__")
        self.stdout_file = os.path.join(self.jobdir, "__stdout__")
        self.stderr_file = os.path.join(self.jobdir, "__stderr__")
        self.pid_file = os.path.join(self.jobdir, "__pid__")

    def write_pid(self, host, pid):
        open(self.pid_file,"w").write("%s\t%s" %(host, pid))

    def read_pid(self):
        try:
           host, pid = [_f.strip() for _f in 
                        open(self.pid_file,"r").readline().split("\t")]
        except IOError:
            host, pid = "", ""
        else:
            pid = int(pid)

        return host, pid

    def get_launch_cmd(self):
        return ' '.join([self.bin] + ["%s %s" %(k,v) for k,v in six.iteritems(self.args) if v is not None])

    def dump_script(self):
        ''' Generates the shell script launching the job. '''

        launch_cmd = self.get_launch_cmd()
        lines = [
            "#!/bin/sh",
            " (echo R > %s && date +'%s' > %s) &&" %(self.status_file,
                                                     TIME_FORMAT,
                                                     self.time_file),
            " (cd %s && %s && (echo D > %s; %s) || (echo E > %s; %s));" %\
                (self.jobdir, launch_cmd,  self.status_file, self.ifdone_cmd,
                 self.status_file, self.iffail_cmd),
            " date +'%s' >> %s; " %(TIME_FORMAT, self.time_file),
            ]
        script = '\n'.join(lines)
        if not os.path.exists(self.jobdir):
            os.makedirs(self.jobdir)
        open(self.cmd_file, "w").write(script)

    def get_status(self, sge_jobs=None):
        # Finished status:
        #  E.rror
        #  D.one
        # In execution status:
        #  W.ating
        #  Q.ueued
        #  R.unning
        #  L.ost
        if self.status not in set("DE"):
            jinfo = db.get_task_info(self.jobid)
            self.host = jinfo.get("host", None) or ""
            self.pid = jinfo.get("pid", None) or ""
            saved_status = jinfo.get("status", "W")

            try:
                st = open(self.status_file).read(1)
            except IOError:
                st = saved_status

            # If this is in execution, tries to track the job
            if st in set("QRL"):
                if self.host.startswith("@sge"):
                    sge_st = sge_jobs.get(self.pid, {}).get("state", None)
                    log.debug("%s %s", self, sge_st)
                    if not sge_st:
                        log.debug("%s %s %s", self, sge_st, self.pid)
                        st = "L"
                    elif "E" in sge_st:
                        pass
                elif self.host == HOSTNAME and not pid_up(self.pid):
                    st = "L"
            elif st == "E":
                log.error("Job error reported: %s" %self)
            elif st == "":
                st = "L"

            # if this is the first time this job is checked and has an error
            # state saved from prev runs, retry if necessary
            if (st == "E" and self.status is None):
                log.warning('@@3:Retrying job marked as error from previous executions.@@1:')
                self.status = 'W'
                try:
                    st = open(self.status_file, "w").write("W")
                except IOError:
                    pass
            else:
                self.status = st

        return self.status

    def clean(self):
        if os.path.exists(self.jobdir):
            shutil.rmtree(self.jobdir)
        self.status = "W"


