from __future__ import absolute_import
from __future__ import print_function
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

import os
import re
from sys import stderr as STDERR
import six
from six.moves import range

def read_phylip(source, interleaved=True, obj=None,
                relaxed=False, fix_duplicates=True):
    if obj is None:
        from ..coretype import SeqGroup
        SG = SeqGroup()
    else:
        SG = obj

    # Prepares handle from which read sequences
    if os.path.isfile(source):
        if source.endswith('.gz'):
            import gzip
            _source = gzip.open(source)
        else:
            _source = open(source, "r")
    else:
        _source = iter(source.split("\n"))

    nchar, ntax = None, None
    counter = 0
    id_counter = 0
    for line in _source:
        line = line.strip("\n")
        # Passes comments and blank lines
        if not line or line[0] == "#":
            continue
        # Reads head
        if not nchar or not ntax:
            m = re.match("^\s*(\d+)\s+(\d+)",line)
            if m:
                ntax  = int (m.groups()[0])
                nchar = int (m.groups()[1])
            else:
                raise Exception("A first line with the alignment dimension is required")
        # Reads sequences
        else:
            if not interleaved:
                # Reads names and sequences
                if SG.id2name.get(id_counter, None) is None:
                    if relaxed:
                        m = re.match("^([^ ]+)(.+)", line)
                    else:
                        m = re.match("^(.{10})(.+)", line)
                    if m:
                        name = m.groups()[0].strip()
                        if fix_duplicates and name in SG.name2id:
                            tag = str(len([k for k in list(SG.name2id.keys()) \
                                              if k.endswith(name)]))
                            old_name = name
                            # Tag is in the beginning to avoid being
                            # cut it by the 10 chars limit
                            name = tag+"_"+name
                            print("Duplicated entry [%s] was renamed to [%s]" %\
                                (old_name, name), file=STDERR)
                        SG.id2name[id_counter] = name
                        SG.name2id[name] = id_counter
                        SG.id2seq[id_counter] = ""
                        line = m.groups()[1]
                    else:
                        raise Exception("Wrong phylip sequencial format.")
                SG.id2seq[id_counter] += re.sub("\s","", line)
                if len(SG.id2seq[id_counter]) == nchar:
                    id_counter += 1
                    name = None
                elif len(SG.id2seq[id_counter]) > nchar:
                    raise Exception("Unexpected length of sequence [%s] [%s]." %(name,SG.id2seq[id_counter]))
            else:
                if len(SG)<ntax:
                    if relaxed:
                        m = re.match("^([^ ]+)(.+)", line)
                    else:
                        m = re.match("^(.{10})(.+)",line)
                    if m:
                        name = m.groups()[0].strip()

                        seq = re.sub("\s","",m.groups()[1])
                        SG.id2seq[id_counter] = seq
                        SG.id2name[id_counter] = name
                        if fix_duplicates and name in SG.name2id:
                            tag = str(len([k for k in list(SG.name2id.keys()) \
                                              if k.endswith(name)]))
                            old_name = name
                            name = tag+"_"+name
                            print("Duplicated entry [%s] was renamed to [%s]" %\
                                (old_name, name), file=STDERR)
                        SG.name2id[name] = id_counter
                        id_counter += 1
                    else:
                        raise Exception("Unexpected number of sequences.")
                else:
                    seq = re.sub("\s", "", line)
                    if id_counter == len(SG):
                        id_counter = 0
                    SG.id2seq[id_counter] += seq
                    id_counter += 1

    if len(SG) != ntax:
        raise Exception("Unexpected number of sequences.")

    # Check lenght of all seqs
    for i in list(SG.id2seq.keys()):
        if len(SG.id2seq[i]) != nchar:
            raise Exception("Unexpected lenght of sequence [%s]" %SG.id2name[i])

    return SG

def write_phylip(aln, outfile=None, interleaved=True, relaxed=False):
    width = 60
    seq_visited = set([])

    show_name_warning = False
    lenghts = set((len(seq) for seq in list(aln.id2seq.values())))
    if len(lenghts) >1:
        raise Exception("Phylip format requires sequences of equal lenght.")
    seqlength = lenghts.pop()

    if not relaxed:
        name_fix = 10
    else:
        name_fix = max([len(name) for name in list(aln.id2name.values())])

    alg_lines = []
    alg_text = " %d %d" %(len(aln), seqlength)
    alg_lines.append(alg_text)
    if interleaved:
        visited = set([])
        for i in range(0, seqlength, width):
            for j in six.iterkeys(aln.id2name): #xrange(len(aln)):
                name =  aln.id2name[j]
                if not relaxed and len(name)>name_fix:
                    name = name[:name_fix]
                    show_name_warning = True

                seq = aln.id2seq[j][i:i+width]
                if j not in visited:
                    name_str = "%s   " %name.ljust(name_fix)
                    visited.add(j)
                else:
                    name_str = "".ljust(name_fix+3)

                seq_str = ' '.join([seq[k:k+10] for k in range(0, len(seq), 10)])
                line_str = "%s%s" %(name_str, seq_str)
                alg_lines.append(line_str)
            alg_lines.append("")
    else:
        for name, seq, comments in aln.iter_entries():
            if not relaxed and len(name)>10:
                name = name[:name_fix]
                show_name_warning = True
            line_str = "%s   %s\n%s" %\
                (name.ljust(name_fix), seq[0:width-name_fix-3], '\n'.join([seq[k:k+width]  \
                                      for k in range(width-name_fix-3, len(seq), width)]))
            alg_lines.append(line_str)
        alg_lines.append("")


    if show_name_warning:
        print("Warning! Some sequence names were cut to 10 characters!!", file=STDERR)
    alg_text = '\n'.join(alg_lines)
    if outfile is not None:
        OUT = open(outfile, "w")
        OUT.write(alg_text)
        OUT.close()
    else:
        return alg_text
