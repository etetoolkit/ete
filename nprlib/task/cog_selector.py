import numpy
from StringIO import StringIO
import cPickle
from collections import defaultdict
import logging
import os
log = logging.getLogger("main")


from nprlib.master_task import CogSelectorTask
from nprlib.errors import DataError
from nprlib.utils import (GLOBALS, print_as_table, generate_node_ids,
                          encode_seqname)
from nprlib import db

__all__ = ["BrhCogSelector"]

quote = lambda _x: '"%s"' %_x

class BrhCogSelector(CogSelectorTask):
    def __init__(self, target_sp, out_sp, seqtype, confname):

        conf = GLOBALS["config"]
        self.seed = conf[confname]["_seed"]
        self.missing_factor = float(conf[confname]["_species_missing_factor"])
        self.min_orthology_score = float(conf[confname]["_min_orthology_score"])
        base_args = {
            "_seed": self.seed,
            "_missing_factor": self.missing_factor,
            "_min_orthology_score": self.min_orthology_score
        }
        
        node_id, clade_id = generate_node_ids(target_sp, out_sp)
        # Initialize task
        CogSelectorTask.__init__(self, node_id, "cog_selector",
                                 "Cog-Selector", base_args)

        # taskid does not depend on jobs, so I set it manually
        self.cladeid = clade_id
        self.seqtype = seqtype
        self.targets = target_sp
        self.outgroups = out_sp
        self.init()
        self.size = len(target_sp | out_sp)
        self.cog_analysis = None
        self.cogs = None
        self.cog_analysis_file = os.path.join(self.taskdir, "cog_analysis.pkl")
        self.cogs_file = os.path.join(self.taskdir, "all_cogs.pkl")
        
    def finish(self):
        if os.path.exists(self.cog_analysis_file) and \
           os.path.exists(self.cogs_file):
            log.log(22, "Loading COGs from cache files")
            self.cog_analysis = cPickle.load(open(self.cog_analysis_file))
            self.cogs = cPickle.load(open(self.cogs_file))
        else: 
            all_species = self.targets | self.outgroups
            cogs, cog_analysis = brh_cogs(db, all_species,
                                          missing_factor=self.missing_factor,
                                          seed_sp=self.seed)
            
            self.cog_analysis = cog_analysis
            self.cogs = []
            for co in cogs:
                self.cogs.append(map(encode_seqname, co))
            
            log.log(22, "Dumping COGs into file")
            cPickle.dump(self.cog_analysis, open(self.cog_analysis_file, "w"))
            cPickle.dump(self.cogs, open(self.cogs_file, "w"))

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
        sp_to_test = list(species)
    elif seed_sp == "largest":
        cmd = """SELECT taxid1, count(*) from ortho_pair GROUP BY taxid1"""
        cmd2 = """SELECT taxid2, count(*) from ortho_pair GROUP BY taxid2"""
        db.cursor.execute(cmd)
        sp2size = {}
        for tax, counter in db.cursor.fetchall():
            sp2size[tax] = counter
        db.cursor.execute(cmd2)            
        for tax, counter in db.cursor.fetchall():
            sp2size[tax] = sp2size.get(tax, 0) + counter
        
        sorted_sp = sorted(sp2size.items(), lambda x,y: cmp(x[1],y[1]))
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
        log.log(26,"Testing new seed species:%s (%d/%d)", DB.get_species_name(seed), j+1, len(sp_to_test))
        species_side1 = ','.join(map(quote, [s for s in species if str(s)>str(seed)]))
        species_side2 = ','.join(map(quote, [s for s in species if str(s)<str(seed)]))
        pairs1 = []
        pairs2 = []
        # Select all ids with matches in the target species, and
        # return the total number of species covered by each of
        # such ids.
        if species_side1 != "":
            cmd = """SELECT seqid1, taxid1, seqid2, taxid2 from ortho_pair WHERE
            taxid1="%s" AND taxid2 IN (%s) AND score >= %s""" %\
            (seed, species_side1, min_score)
            DB.cursor.execute(cmd)
            pairs1 = DB.cursor.fetchall()

        if species_side2 != "":
            cmd = """SELECT seqid2, taxid2, seqid1, taxid1 from ortho_pair WHERE
            taxid2="%s" AND taxid1 IN (%s) AND score >= %s""" %\
            (seed, species_side2, min_score)
            DB.cursor.execute(cmd)
            pairs2 = DB.cursor.fetchall()

        cog_candidates = defaultdict(set)
        for seq1, sp1, seq2, sp2 in pairs1 + pairs2:
            s1 = (sp1, seq1)
            s2 = (sp2, seq2)
            cog_candidates[(sp1, seq1)].update([s1, s2])

        all_cogs = [cand for cand in cog_candidates.values() if
                    len(cand) >= min_species]
        
        cog_sizes = [len(cog) for cog in all_cogs]
        cog_spsizes = [len(set([e[0] for e in cog])) for cog in all_cogs]

        if [1 for i in xrange(len(cog_sizes)) if cog_sizes[i] != cog_spsizes[i]]:
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
        mx1, mn1, avg1 = numpy.max(cog_sizes1), numpy.min(cog_sizes1), round(numpy.mean(cog_sizes1))
        mx2, mn2, avg2 = numpy.max(cog_sizes2), numpy.min(cog_sizes2), round(numpy.mean(cog_sizes2))
        
        # we want to maximize all these values in the following order:
        for i, j in ((mx1, mx2), (avg1, avg2), (len(cogs1), len(cogs2))):
            v = -1 * cmp(i, j)
            if v != 0:
                break
        return v
    
    log.log(28, "Finding best COG selection...")
    cogs_selection.sort(_sort_cogs)
    lines = []
    for seed, all_cogs in cogs_selection:
        cog_sizes = [len(cog) for cog in all_cogs]
        mx, mn, avg = max(cog_sizes), min(cog_sizes), round(numpy.mean(cog_sizes))
        lines.append([seed, mx, mn, avg, len(all_cogs)])
    analysis_txt = StringIO()
    print_as_table(lines[:25], stdout=analysis_txt,
                   header=["Seed","max # COGs", "min # COGs", "avg # COGs", "total # COGs"])
    log.log(24, "Analysis details:\n"+analysis_txt.getvalue())
    best_seed, best_cogs = cogs_selection[0]
    cog_sizes = [len(cog) for cog in best_cogs]
    best_cogs.sort(lambda x,y: cmp(len(x), len(y)), reverse=True)
    
    if max(cog_sizes) < len(species):
        raise ValueError("Current COG selection parameters do not permit to cover all species")

    recoded_cogs = []
    for cog in best_cogs:
        named_cog = map(lambda x: "%s%s%s" %(x[0], GLOBALS["spname_delimiter"],x[1]), cog)
        recoded_cogs.append(named_cog)
    return recoded_cogs, analysis_txt.getvalue()
 

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
    max_cogs = numpy.max([len(data[2]) for data in cogs_selections])
    median_cogs = numpy.median([len(data[2]) for data in cogs_selections])

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
                    "%0.1f%% +- %0.1f" %(numpy.mean(sp_percent_coverages), numpy.std(sp_percent_coverages)), \
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
    print cog_analysis.getvalue()
    #best_cog_selection = int(raw_input("choose:"))
    return cogs_selections[best_cog_selection], cog_analysis

def _analyze_cog_selection(all_cogs):
    print "total cogs:", len(all_cogs)
    sp2cogcount = {}
    size2cogs = {}
    for cog in all_cogs:
        for seq in cog:
            sp = seq.split(GLOBALS["spname_delimiter"])[0]
            sp2cogcount[sp] = sp2cogcount.setdefault(sp, 0)+1
        size2cogs.setdefault(len(cog), []).append(cog)

    sorted_spcs = sorted(sp2cogcount.items(), lambda x,y: cmp(x[1], y[1]))
    # Take only first 20 species 
    coverages = [s[1] for s in sorted_spcs][:20]
    spnames  = [str(s[0])+ DB.get_species_name(s[0]) for s in sorted_spcs][:20]
    pylab.subplot(1,2,1)
    pylab.bar(range(len(coverages)), coverages)
    labels = pylab.xticks(pylab.arange(len(spnames)), spnames)
    pylab.subplots_adjust(bottom=0.35)
    pylab.title(str(len(all_cogs))+" COGs")
    pylab.setp(labels[1], 'rotation', 90,fontsize=10, horizontalalignment = 'center')
    pylab.subplot(1,2,2)
    pylab.title("Best COG contains "+str(max(size2cogs.values()))+" species" )
    pylab.bar(range(1,216), [len(size2cogs.get(s, [])) for s in range(1,216)])
    pylab.show()
  

def cog_info(candidates, sp2hits):
    sp_coverages = [hits/float(len(candidates)) for hits in sp2hits.values()]
    species_covered = len(set(sp2hits.keys()))+1
    min_cov = numpy.min(sp_coverages)
    max_cov = numpy.min(sp_coverages)
    median_cov = numpy.median(sp_coverages)
    return min_cov, max_cov, median_cov


def get_cog_score(candidates, sp2hits, max_cogs, all_species):

    cog_cov = numpy.mean([len(cogs) for cogs in candidates])/float(len(sp2hits)+1)
    cog_mean_cov = numpy.mean([len(cogs)/float(len(sp2hits)) for cogs in candidates]) # numero medio de especies en cada cog
    cog_min_sp = numpy.min([len(cogs) for cogs in candidates])

    sp_coverages = [sp2hits.get(sp, 0)/float(len(candidates)) for sp in all_species]
    species_covered = len(set(sp2hits.keys()))+1

    nfactor = len(candidates)/float(max_cogs) # Numero de cogs
    min_cov = numpy.min(sp_coverages) # el coverage de la peor especie
    max_cov = numpy.min(sp_coverages)
    median_cov = numpy.median(sp_coverages)
    cov_std = numpy.std(sp_coverages)

    score = numpy.min([nfactor, cog_mean_cov, min_cov])
    return score, min_cov, max_cov, median_cov, cov_std, cog_cov 

def brh_cogs_OLD(DB, species, min_score=0.3, missing_factor=0.0, \
             seed_sp=None):
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

    if seed_sp == "auto":
        sp_to_test = list(species)
    elif seed_sp == "largest":
        cmd = """SELECT taxid1, count(*) from ortho_pair GROUP BY taxid1"""
        cmd2 = """SELECT taxid2, count(*) from ortho_pair GROUP BY taxid2"""
        db.cursor.execute(cmd)
        sp2size = {}
        for tax, counter in db.cursor.fetchall():
            sp2size[tax] = counter
        db.cursor.execute(cmd2)            
        for tax, counter in db.cursor.fetchall():
            sp2size[tax] = sp2size.get(tax, 0) + counter
        
        sorted_sp = sorted(sp2size.items(), lambda x,y: cmp(x[1],y[1]))
        log.log(24, sorted_sp[:6])
        largest_sp = sorted_sp[-1][0]
        sp_to_test = [largest_sp]
        log.log(28, "Using %s as search seed. Proteome size=%s genes" %\
            (largest_sp, sp2size[largest_sp]))
    else:
        sp_to_test = [str(seed_sp)]
        
    # The following loop tests each possible seed if none is
    # specified.
    log.log(28, "Identifying Clusters of Orthologs groups (COGs)")
    best_cogs_selection = []
    
    for j, seed in enumerate(sp_to_test):
        log.log(26,"Testing new seed species:%s (%d/%d)", DB.get_species_name(seed), j+1, len(sp_to_test))
        species_side1 = ','.join(map(quote, [s for s in species if str(s)>str(seed)]))
        species_side2 = ','.join(map(quote, [s for s in species if str(s)<str(seed)]))
        candidates1 = []
        candidates2 = []
        # Select all ids with matches in the target species, and
        # return the total number of species covered by each of
        # such ids.
        if species_side1 != "":
            cmd = """SELECT seqid1, count(taxid2) from ortho_pair WHERE
            taxid1="%s" AND taxid2 IN (%s) AND score >= %s GROUP BY seqid1""" %\
            (seed, species_side1, min_score)
            DB.cursor.execute(cmd)
            candidates1 = DB.cursor.fetchall()

        if species_side2 != "":
            cmd = """SELECT seqid2, count(taxid1) from ortho_pair WHERE
            taxid2="%s" AND taxid1 IN (%s) AND score >= %s GROUP BY seqid2""" %\
            (seed, species_side2, min_score)
            DB.cursor.execute(cmd)
            candidates2 = DB.cursor.fetchall()

        seqid2spcs = {}
        #for seqid, spcounter in set(candidates1)|set(candidates2):
        for seqid, spcounter in candidates1 + candidates2:
            seqid2spcs[seqid] = seqid2spcs.get(seqid, 0) + spcounter

        # From the previously selected ids, filter out those that are
        # two small (few species). For this, I check what cogs pass missing_factor.
        cogs_selection = []
        for missing_species_allowed in xrange(0, int(round(len(species) * missing_factor))+1):
            # filtered_candidates = set([seqid for seqid, counter in seqid2spcs.iteritems() \
            #                           if counter>len(species)*(1-missing_factor)])
            #log.log(20, "Evaluating COGs when allowing %s missing species", missing_species_allowed)
            filtered_candidates = set([seqid for seqid, counter in seqid2spcs.iteritems() \
                                       if counter >= len(species) - missing_species_allowed - 1]) # -1 is to avoid counting seed 
            filtered_ids = ','.join(map(quote, filtered_candidates))
            valid_species = ','.join(map(quote, [s for s in species]))
            # Now, lets see how many species we cover with the
            # filtered list of ids, and how well is each species
            # represented.
            sp2hits = {}
            print "STEP 2"
            if filtered_ids != "":
                cmd = """SELECT taxid2, count(seqid1) from ortho_pair WHERE
                taxid1="%s" AND seqid1 IN (%s) AND taxid2 IN (%s) AND score>=%s GROUP BY taxid2""" %\
                (seed, filtered_ids, valid_species, min_score)
                if DB.cursor.execute(cmd):
                    for record in DB.cursor.fetchall():
                        sp2hits[record[0]] = sp2hits.get(record[0], 0) + record[1]

                cmd = """SELECT taxid1, count(seqid2) from ortho_pair WHERE
                taxid2="%s" AND seqid2 IN (%s) AND  taxid1 IN (%s) AND score>=%s GROUP BY taxid1""" %\
                (seed, filtered_ids, valid_species, min_score)
                if DB.cursor.execute(cmd):
                    for record in DB.cursor.fetchall():
                        sp2hits[record[0]] = sp2hits.get(record[0], 0) + record[1]
                print "STEP 3"
                species_side1 = ','.join(map(quote, [s for s in species if str(s)>str(seed)]))
                species_side2 = ','.join(map(quote, [s for s in species if str(s)<str(seed)]))
                visited_seqids = set()
                all_cogs = []
                visited_seqids = set()

                for c1, seqid in enumerate(filtered_candidates):
                    # Avoid to detect the same COG
                    seedname = str(seed)+GLOBALS["spname_delimiter"]+str(seqid)
                    COG = [seedname]
                    if species_side1 != "":
                        cmd = """ SELECT taxid2, seqid2 from ortho_pair WHERE 
                             taxid1="%s" AND seqid1="%s" AND taxid2 IN (%s) AND score>=%s""" % \
                            (seed, seqid, species_side1, min_score)
                        DB.cursor.execute(cmd)
                        COG += [str(r[0])+GLOBALS["spname_delimiter"]+str(r[1]) for r in  DB.cursor.fetchall()]

                    if species_side2 != "":
                        cmd = """SELECT taxid1, seqid1 from ortho_pair WHERE
                            taxid2="%s" AND seqid2="%s" AND taxid1 IN (%s) AND score>=%s""" %\
                            (seed, seqid, species_side2, min_score)

                        DB.cursor.execute(cmd)
                        COG += [str(r[0])+GLOBALS["spname_delimiter"]+str(r[1]) for r in  DB.cursor.fetchall()]

                    # This ensure that once an id has been used to form a COG,
                    # none of the members will be rescaned
                    for seqname in COG: 
                        visited_seqids.add(seqname)
                    all_cogs.append(COG)
                cogs_selection.append([seed, missing_species_allowed, all_cogs, sp2hits])
            else:
                pass
        print "END"
        cogs, cogs_analysis = get_best_selection(cogs_selection, species)
        best_cogs_selection.append(cogs)
    log.log(28, "\tFinal cogs:")
    cogs, cogs_analysis = get_best_selection(best_cogs_selection, species)
    return cogs[2], cogs_analysis



