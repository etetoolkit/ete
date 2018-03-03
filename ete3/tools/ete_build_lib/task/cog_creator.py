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
from six import StringIO
import six.moves.cPickle
from collections import defaultdict
import logging
import os
import time
import six
from six.moves import map
from six.moves import range
log = logging.getLogger("main")

from ..master_task import CogSelectorTask
from ..errors import DataError
from ..utils import (GLOBALS, print_as_table, generate_node_ids, cmp,
                     encode_seqname, md5, pjoin, _mean, _median, _max, _min, _std)
from .. import db

__all__ = ["BrhCogCreator"]

quote = lambda _x: '"%s"' %_x

class BrhCogCreator(CogSelectorTask):
    def __init__(self, target_sp, out_sp, seqtype, conf, confname):

        self.seed = conf[confname]["_seed"]
        self.missing_factor = float(conf[confname]["_species_missing_factor"])
        node_id, clade_id = generate_node_ids(target_sp, out_sp)
        # Initialize task
        CogSelectorTask.__init__(self, node_id, "cog_selector",
                                 "Cog-Selector", None, conf[confname])

        # taskid does not depend on jobs, so I set it manually
        self.cladeid = clade_id
        self.seqtype = seqtype
        self.targets = target_sp
        self.outgroups = out_sp
        self.init()
        self.size = len(target_sp | out_sp)
        self.cog_analysis = None
        self.cogs = None

    def finish(self):
        tm_start = time.ctime()
        all_species = self.targets | self.outgroups
        cogs, cog_analysis = brh_cogs2(db, all_species,
                                      missing_factor=self.missing_factor,
                                      seed_sp=self.seed)
        self.raw_cogs = cogs
        self.cog_analysis = cog_analysis
        self.cogs = []
        for co in cogs:
            # self.cogs.append(map(encode_seqname, co))
            encoded_names = db.translate_names(co)
            if len(encoded_names) != len(co):
                print(set(co) - set(encoded_names.keys()))
                raise DataError("Some sequence ids could not be translated")
            self.cogs.append(list(encoded_names.values()))

        # Sort Cogs according to the md5 hash of its content. Random
        # sorting but kept among runs
        list(map(lambda x: x.sort(), self.cogs))
        self.cogs.sort(lambda x,y: cmp(md5(','.join(x)), md5(','.join(y))))
        log.log(28, "%s COGs detected" %len(self.cogs))
        tm_end = time.ctime()
        #open(pjoin(self.taskdir, "__time__"), "w").write(
        #    '\n'.join([tm_start, tm_end]))
        CogSelectorTask.store_data(self, self.cogs, self.cog_analysis)


def brh_cogs(DB, species, missing_factor=0.0, seed_sp=None, min_score=0):
    """It scans all precalculate BRH relationships among the species
       passed as an argument, and detects Clusters of Orthologs
       according to several criteria:

       min_score: the min coverage/overalp value required for a
       blast to be a reliable hit.

       missing_factor: the min percentage of species in which a
       given seq must have  orthologs.

    """
    log.log(26, "Searching BRH orthologs")
    species = set(map(str, species))

    min_species = len(species) - round(missing_factor * len(species))

    if seed_sp == "auto":
        # seed2size = get_sorted_seeds(seed_sp, species, species, min_species, DB)
        # sort_seeds =  sorted([(len(size), sp) for sp, size in seed2size.iteritems()])
        # sp_to_test = [sort_seeds[-1][1]]
        sp_to_test = list(species)
    elif seed_sp == "largest":
        cmd = """SELECT taxid, size FROM species"""
        db.seqcursor.execute(cmd)
        sp2size = {}
        for tax, counter in db.seqcursor.fetchall():
            if tax in species:
                sp2size[tax] = counter

        sorted_sp = sorted(list(sp2size.items()), lambda x,y: cmp(x[1],y[1]))
        log.log(24, sorted_sp[:6])
        largest_sp = sorted_sp[-1][0]
        sp_to_test = [largest_sp]
        log.log(28, "Using %s as search seed. Proteome size=%s genes" %\
            (largest_sp, sp2size[largest_sp]))
    else:
        sp_to_test = [str(seed_sp)]

    # The following loop tests each possible seed if none is
    # specified.
    log.log(28, "Detecting Clusters of Orthologs groups (COGs)")
    log.log(28, "Min number of species per COG: %d" %min_species)
    cogs_selection = []

    for j, seed in enumerate(sp_to_test):
        log.log(26,"Testing new seed species:%s (%d/%d)", seed, j+1, len(sp_to_test))
        species_side1 = ','.join(map(quote, [s for s in species if str(s)>str(seed)]))
        species_side2 = ','.join(map(quote, [s for s in species if str(s)<str(seed)]))
        pairs1 = []
        pairs2 = []
        # Select all ids with matches in the target species, and
        # return the total number of species covered by each of
        # such ids.
        if species_side1 != "":
            cmd = """SELECT seqid1, taxid1, seqid2, taxid2 from ortho_pair WHERE
            taxid1="%s" AND taxid2 IN (%s) """ %\
            (seed, species_side1)
            DB.orthocursor.execute(cmd)
            pairs1 = DB.orthocursor.fetchall()

        if species_side2 != "":
            cmd = """SELECT seqid2, taxid2, seqid1, taxid1 from ortho_pair WHERE
            taxid1 IN (%s) AND taxid2 = "%s" """ %\
            (species_side2, seed)

            #taxid2="%s" AND taxid1 IN (%s) AND score >= %s""" %\
            #(seed, species_side2, min_score)
            DB.orthocursor.execute(cmd)
            pairs2 = DB.orthocursor.fetchall()

        cog_candidates = defaultdict(set)
        for seq1, sp1, seq2, sp2 in pairs1 + pairs2:
            s1 = (sp1, seq1)
            s2 = (sp2, seq2)
            cog_candidates[(sp1, seq1)].update([s1, s2])

        all_cogs = [cand for cand in list(cog_candidates.values()) if
                    len(cand) >= min_species]

        cog_sizes = [len(cog) for cog in all_cogs]
        cog_spsizes = [len(set([e[0] for e in cog])) for cog in all_cogs]

        if [1 for i in range(len(cog_sizes)) if cog_sizes[i] != cog_spsizes[i]]:
            # for i in xrange(len(cog_sizes)):
            #     if cog_sizes[i] != cog_spsizes[i]:
            #         print cog_sizes[i], cog_spsizes[i]
            #         raw_input()
            raise ValueError("Inconsistent COG found")

        if cog_sizes:
            cogs_selection.append([seed, all_cogs])
        log.log(26, "Found %d COGs" % len(all_cogs))

    def _sort_cogs(cogs1, cogs2):
        cogs1 = cogs1[1] # discard seed info
        cogs2 = cogs2[1] # discard seed info
        cog_sizes1 = [len(cog) for cog in cogs1]
        cog_sizes2 = [len(cog) for cog in cogs2]
        mx1, mn1, avg1 = _max(cog_sizes1), _min(cog_sizes1), round(_mean(cog_sizes1))
        mx2, mn2, avg2 = _max(cog_sizes2), _min(cog_sizes2), round(_mean(cog_sizes2))

        # we want to maximize all these values in the following order:
        for i, j in ((mx1, mx2), (avg1, avg2), (len(cogs1), len(cogs2))):
            v = -1 * cmp(i, j)
            if v != 0:
                break
        return v

    log.log(26, "Finding best COG selection...")
    cogs_selection.sort(_sort_cogs)
    lines = []
    for seed, all_cogs in cogs_selection:
        cog_sizes = [len(cog) for cog in all_cogs]
        mx, mn, avg = max(cog_sizes), min(cog_sizes), round(_mean(cog_sizes))
        lines.append([seed, mx, mn, avg, len(all_cogs)])
    analysis_txt = StringIO()
    print_as_table(lines[:25], stdout=analysis_txt,
                   header=["Seed","largest COG", "smallest COGs", "avg COG size", "total COGs"])
    log.log(28, "Analysis details:\n"+analysis_txt.getvalue())
    best_seed, best_cogs = cogs_selection[0]
    cog_sizes = [len(cog) for cog in best_cogs]

    # Not necessary since they will be sorted differently later on
    #best_cogs.sort(lambda x,y: cmp(len(x), len(y)), reverse=True)

    if max(cog_sizes) < len(species):
        raise ValueError("Current COG selection parameters do not permit to cover all species")

    recoded_cogs = []
    for cog in best_cogs:
        named_cog = ["%s%s%s" %(x[0], GLOBALS["spname_delimiter"],x[1]) for x in cog]
        recoded_cogs.append(named_cog)

    return recoded_cogs, analysis_txt.getvalue()

def brh_cogs2(DB, species, missing_factor=0.0, seed_sp=None, min_score=0):
    """It scans all precalculate BRH relationships among the species
       passed as an argument, and detects Clusters of Orthologs
       according to several criteria:

       min_score: the min coverage/overalp value required for a
       blast to be a reliable hit.

       missing_factor: the min percentage of species in which a
       given seq must have  orthologs.

    """
    def _sort_cogs(cogs1, cogs2):
        seed1, mx1, avg1, ncogs1 = cogs1
        seed2, mx2, avg2, ncogs2 = cogs2
        for i, j in ((mx1, mx2), (avg1, avg2), (ncogs1, ncogs2)):
            v = -1 * cmp(i, j)
            if v != 0:
                break
        return v

    log.log(26, "Searching BRH orthologs")
    species = set(map(str, species))

    min_species = len(species) - round(missing_factor * len(species))

    if seed_sp == "auto":
        sp_to_test = list(species)
    elif seed_sp == "largest":
        cmd = """SELECT taxid, size FROM species"""
        db.seqcursor.execute(cmd)
        sp2size = {}
        for tax, counter in db.seqcursor.fetchall():
            if tax in species:
                sp2size[tax] = counter

        sorted_sp = sorted(list(sp2size.items()), lambda x,y: cmp(x[1],y[1]))
        log.log(24, sorted_sp[:6])
        largest_sp = sorted_sp[-1][0]
        sp_to_test = [largest_sp]
        log.log(28, "Using %s as search seed. Proteome size=%s genes" %\
            (largest_sp, sp2size[largest_sp]))
    else:
        sp_to_test = [str(seed_sp)]

    analysis_txt = StringIO()
    if sp_to_test:
        log.log(26, "Finding best COG selection...")
        seed2size = get_sorted_seeds(seed_sp, species, sp_to_test, min_species, DB)
        size_analysis = []
        for seedname, content in six.iteritems(seed2size):
            cog_sizes = [size for seq, size in content]
            mx, avg = _max(cog_sizes), round(_mean(cog_sizes))
            size_analysis.append([seedname, mx, avg, len(content)])
        size_analysis.sort(_sort_cogs)
        #print '\n'.join(map(str, size_analysis))
        seed = size_analysis[0][0]
        print_as_table(size_analysis[:25], stdout=analysis_txt,
                   header=["Seed","largest COG", "avg COG size", "total COGs"])
        if size_analysis[0][1] < len(species)-1:
            print(size_analysis[0][1])
            raise ValueError("Current COG selection parameters do not permit to cover all species")

    log.log(28, analysis_txt.getvalue())
    # The following loop tests each possible seed if none is
    # specified.
    log.log(28, "Computing Clusters of Orthologs groups (COGs)")
    log.log(28, "Min number of species per COG: %d" %min_species)
    cogs_selection = []
    log.log(26,"Using seed species:%s", seed)
    species_side1 = ','.join(map(quote, [s for s in species if str(s)>str(seed)]))
    species_side2 = ','.join(map(quote, [s for s in species if str(s)<str(seed)]))
    pairs1 = []
    pairs2 = []
    # Select all ids with matches in the target species, and
    # return the total number of species covered by each of
    # such ids.
    if species_side1 != "":
        cmd = """SELECT seqid1, taxid1, seqid2, taxid2 from ortho_pair WHERE
            taxid1="%s" AND taxid2 IN (%s) """ % (seed, species_side1)
        DB.orthocursor.execute(cmd)
        pairs1 = DB.orthocursor.fetchall()

    if species_side2 != "":
        cmd = """SELECT seqid2, taxid2, seqid1, taxid1 from ortho_pair WHERE
            taxid1 IN (%s) AND taxid2 = "%s" """ % (species_side2, seed)
        DB.orthocursor.execute(cmd)
        pairs2 = DB.orthocursor.fetchall()

    cog_candidates = defaultdict(set)
    for seq1, sp1, seq2, sp2 in pairs1 + pairs2:
        s1 = (sp1, seq1)
        s2 = (sp2, seq2)
        cog_candidates[(sp1, seq1)].update([s1, s2])

    all_cogs = [cand for cand in list(cog_candidates.values()) if
                len(cand) >= min_species]

    # CHECK CONSISTENCY
    seqs = set()
    for cand in all_cogs:
        seqs.update([b for a,b  in cand if a == seed])
    pre_selected_seqs = set([v[0] for v in seed2size[seed]])
    if len(seqs & pre_selected_seqs) != len(set(seed2size[seed])) or\
            len(seqs & pre_selected_seqs) != len(seqs):
        print("old method seqs", len(seqs), "new seqs", len(set(seed2size[seed])), "Common", len(seqs & pre_selected_seqs))
        raise ValueError("ooops")

    cog_sizes = [len(cog) for cog in all_cogs]
    cog_spsizes = [len(set([e[0] for e in cog])) for cog in all_cogs]

    if [1 for i in range(len(cog_sizes)) if cog_sizes[i] != cog_spsizes[i]]:
        raise ValueError("Inconsistent COG found")

    if cog_sizes:
        cogs_selection.append([seed, all_cogs])
    log.log(26, "Found %d COGs" % len(all_cogs))

    recoded_cogs = []
    for cog in all_cogs:
        named_cog = ["%s%s%s" %(x[0], GLOBALS["spname_delimiter"],x[1]) for x in cog]
        recoded_cogs.append(named_cog)

    return recoded_cogs, analysis_txt.getvalue()


def get_sorted_seeds(seed, species, sp_to_test, min_species, DB):
    seed2count = {}
    species = set(species)
    for j, seed in enumerate(sp_to_test):
        log.log(26,"Testing SIZE of new seed species:%s (%d/%d)", seed, j+1, len(sp_to_test))
        pairs1 = []
        pairs2 = []
        cmd = """SELECT seqid1, GROUP_CONCAT(taxid2) FROM ortho_pair WHERE
            taxid1="%s" GROUP BY (seqid1)""" % (seed)
        DB.orthocursor.execute(cmd)
        pairs1= DB.orthocursor.fetchall()

        cmd = """SELECT seqid2, GROUP_CONCAT(taxid1) FROM ortho_pair WHERE
            taxid2 = "%s" GROUP BY seqid2""" % (seed)
        DB.orthocursor.execute(cmd)
        pairs2 = DB.orthocursor.fetchall()


        # Compute number of species for each seqid representing a cog
        counter = defaultdict(set)
        all_pairs = pairs1 + pairs2
        for seqid, targets in all_pairs:
            counter[seqid].update(set(targets.split(",")) & species)

        # Filter out too small COGs
        valid_seqs = [(k, len(v)) for k, v in six.iteritems(counter) if
                      len(v)>= min_species-1]

        seed2count[seed] = valid_seqs
        log.log(28, "Seed species:%s COGs:%s" %(seed, len(seed2count[seed])))
    return seed2count

def get_best_selection(cogs_selections, species):
    ALL_SPECIES = set(species)

    def _compare_cog_selection(cs1, cs2):
        seed_1, missing_sp_allowed_1, candidates_1, sp2hits_1 = cs1
        seed_2, missing_sp_allowed_2, candidates_2, sp2hits_2 = cs2

        score_1, min_cov_1, max_cov_1, median_cov_1, cov_std_1, cog_cov_1 = get_cog_score(candidates_1, sp2hits_1, median_cogs, ALL_SPECIES-set([seed_1]))
        score_2, min_cov_2, max_cov_2, median_cov_2, cov_std_2, cog_cov_2 = get_cog_score(candidates_2, sp2hits_2, median_cogs, ALL_SPECIES-set([seed_2]))

        sp_represented_1 = len(sp2hits_1)
        sp_represented_2 = len(sp2hits_1)
        cmp_rpr = cmp(sp_represented_1, sp_represented_2)
        if cmp_rpr == 1:
            return 1
        elif cmp_rpr == -1:
            return -1
        else:
            cmp_score = cmp(score_1, score_2)
            if cmp_score == 1:
                return 1
            elif cmp_score == -1:
                return -1
            else:
                cmp_mincov = cmp(min_cov_1, min_cov_2)
                if cmp_mincov == 1:
                    return 1
                elif cmp_mincov == -1:
                    return -1
                else:
                    cmp_maxcov = cmp(max_cov_1, max_cov_2)
                    if cmp_maxcov == 1:
                        return 1
                    elif cmp_maxcov == -1:
                        return -1
                    else:
                        cmp_cand = cmp(len(candidates_1), len(candidates_2))
                        if cmp_cand == 1:
                            return 1
                        elif cmp_cand == -1:
                            return -1
                        else:
                            return 0

    min_score = 0.5
    max_cogs = _max([len(data[2]) for data in cogs_selections])
    median_cogs = _median([len(data[2]) for data in cogs_selections])

    cogs_selections.sort(_compare_cog_selection)
    cogs_selections.reverse()

    header = ['seed',
              'missing sp allowed',
              'spcs covered',
              '#COGs',
              'mean sp coverage)',
              '#COGs for worst sp.',
              '#COGs for best sp.',
              'sp. in COGS(avg)',
              'SCORE' ]
    print_header = True
    best_cog_selection = None
    cog_analysis = StringIO()
    for i, cogs in enumerate(cogs_selections):
        seed, missing_sp_allowed, candidates, sp2hits = cogs
        sp_percent_coverages = [(100*sp2hits.get(sp,0))/float(len(candidates)) for sp in species]
        sp_coverages = [sp2hits.get(sp, 0) for sp in species]
        score, min_cov, max_cov, median_cov, cov_std, cog_cov = get_cog_score(candidates, sp2hits, median_cogs, ALL_SPECIES-set([seed]))

        if best_cog_selection is None:
            best_cog_selection = i
            flag = "*"
        else:
            flag = " "
        data = (candidates,
                flag+"%10s" %seed, \
                    missing_sp_allowed, \
                    "%d (%0.1f%%)" %(len(set(sp2hits.keys()))+1, 100*float(len(ALL_SPECIES))/(len(sp2hits)+1)) , \
                    len(candidates), \
                    "%0.1f%% +- %0.1f" %(_mean(sp_percent_coverages), _std(sp_percent_coverages)), \
                    "% 3d (%0.1f%%)" %(min(sp_coverages),100*min(sp_coverages)/float(len(candidates))), \
                    "% 3d (%0.1f%%)" %(max(sp_coverages),100*max(sp_coverages)/float(len(candidates))), \
                    cog_cov,
                    score
                )
        if print_header:
            print_as_table([data[1:]], header=header, print_header=True, stdout=cog_analysis)
            print_header = False
        else:
            print_as_table([data[1:]], header=header, print_header=False, stdout=cog_analysis)

    #raw_input("Press")
    print(cog_analysis.getvalue())
    #best_cog_selection = int(raw_input("choose:"))
    return cogs_selections[best_cog_selection], cog_analysis

def _analyze_cog_selection(all_cogs):
    print("total cogs:", len(all_cogs))
    sp2cogcount = {}
    size2cogs = {}
    for cog in all_cogs:
        for seq in cog:
            sp = seq.split(GLOBALS["spname_delimiter"])[0]
            sp2cogcount[sp] = sp2cogcount.setdefault(sp, 0)+1
        size2cogs.setdefault(len(cog), []).append(cog)

    sorted_spcs = sorted(list(sp2cogcount.items()), lambda x,y: cmp(x[1], y[1]))
    # Take only first 20 species
    coverages = [s[1] for s in sorted_spcs][:20]
    spnames  = [str(s[0])+ s[0] for s in sorted_spcs][:20]
    pylab.subplot(1,2,1)
    pylab.bar(list(range(len(coverages))), coverages)
    labels = pylab.xticks(pylab.arange(len(spnames)), spnames)
    pylab.subplots_adjust(bottom=0.35)
    pylab.title(str(len(all_cogs))+" COGs")
    pylab.setp(labels[1], 'rotation', 90,fontsize=10, horizontalalignment = 'center')
    pylab.subplot(1,2,2)
    pylab.title("Best COG contains "+str(max(size2cogs.values()))+" species" )
    pylab.bar(list(range(1,216)), [len(size2cogs.get(s, [])) for s in range(1,216)])
    pylab.show()


def cog_info(candidates, sp2hits):
    sp_coverages = [hits/float(len(candidates)) for hits in list(sp2hits.values())]
    species_covered = len(set(sp2hits.keys()))+1
    min_cov = _min(sp_coverages)
    max_cov = _min(sp_coverages)
    median_cov = _median(sp_coverages)
    return min_cov, max_cov, median_cov


def get_cog_score(candidates, sp2hits, max_cogs, all_species):

    cog_cov = _mean([len(cogs) for cogs in candidates])/float(len(sp2hits)+1)
    cog_mean_cov = _mean([len(cogs)/float(len(sp2hits)) for cogs in candidates]) # numero medio de especies en cada cog
    cog_min_sp = _min([len(cogs) for cogs in candidates])

    sp_coverages = [sp2hits.get(sp, 0)/float(len(candidates)) for sp in all_species]
    species_covered = len(set(sp2hits.keys()))+1

    nfactor = len(candidates)/float(max_cogs) # Numero de cogs
    min_cov = _min(sp_coverages) # el coverage de la peor especie
    max_cov = _min(sp_coverages)
    median_cov = _median(sp_coverages)
    cov_std = _std(sp_coverages)

    score = _min([nfactor, cog_mean_cov, min_cov])
    return score, min_cov, max_cov, median_cov, cov_std, cog_cov

