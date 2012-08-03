import logging
log = logging.getLogger("main")

from nprlib.master_task import Task
from nprlib.errors import DataError

__all__ = ["CogSelector"]

class CogSelector(Task):
    def __init__(self, species, out_species, seqtype,
                 cog_selection_fn=brh_cogs):
        
        node_id, clade_id = generate_node_ids(species, out_species)

        # Initialize task
        Task.__init__(self, node_id, "cog_selector", "Cog-Selector")

        # taskid does not depend on jobs, so I set it manually
        self.taskid = node_id
        self.init()

        self.cog_selection_fn = cog_selection_fn
        
        # Clusters of Ortholog Groups
        self.cogs = []

    def check(self):
        if os.path.exists(self.multiseq_file):
            return True
        return False

def brh_cogs(species, min_coverage=0.1, missing_factor=0.0, \
             seed_sp=None, log=None):
    """It scans all precalculate BRH relationships among the species
       passed as an argument, and detects Clusters of Orthologs
       according to several criteria:

       min_coverage: the min coverage/overalp value required for a
       blast to be a reliable hit.

       missing_factor: the min percentage of species in which a
       given seq must have  orthologs.

    """
    species = set(map(str, species))

    if not log:
        logger = Logger()
        log = logger.log

    # Check SP_SIZE to select best seed

    sp2size = dict([[int(s), DB.get_proteome_size(s)] for s in species])

    for s, size in sp2size.iteritems():
        if size < MIN_PROTEOME_SIZE:
            log(1, "%s proteome size = %s" %(DB.get_species_name(s),size), -1)

    all_sizes = sp2size.values()
    log(1, "avg proteome size = %0.2f min=%0.2f max=%0.2f" %\
            (numpy.mean(all_sizes), min(all_sizes), max(all_sizes)))

    if type(seed_sp) in set([str, int]):
        sp_to_test = [str(seed_sp)]
    elif seed_sp == []: # Test all seeds
        sp_to_test = list(species)
    else: 
        sorted_sp = sorted(sp2size.items(), lambda x,y: cmp(x[1],y[1]))
        sp_to_test = [sorted_sp[-1][0]]
        name = DB.get_species_name(sp_to_test[0])
        psize = sp2size[sp_to_test[0]]
        log(1, "Using %s as search seed. Proteome size=%s genes" %\
                (name, psize))
    
    # if raw_input("Press to continue...")== "c":
    #    return None

    # The following loop tests each possible seed if none is
    # specified.
    print "Getting COG candidates." 
    best_cogs_selection = []
    for j, seed in enumerate(sp_to_test):
        print "\tTesting", DB.get_species_name(seed), j, "/", len(sp_to_test)
        species_side1 = ','.join(map(str, [s for s in species if str(s)>str(seed)]))
        species_side2 = ','.join(map(str, [s for s in species if str(s)<str(seed)]))
        candidates1 = []
        candidates2 = []
        # SELECT all ids with matches in the target species, and
        # return the total number of species covered by each of
        # such ids.
        if species_side1 != "":
            cmd = """SELECT id1, count(taxid2) from brh WHERE
            taxid1=%s AND taxid2 IN (%s) AND coverage>=%s GROUP BY id1""" %\
            (seed, species_side1, min_coverage)
            DB.listSQL.execute(cmd)
            candidates1 = DB.listSQL.fetchall()
        if species_side2 != "":
            cmd = """SELECT id2, count(taxid1) from brh WHERE
            taxid2=%s AND taxid1 IN (%s) AND coverage>=%s GROUP BY id2""" %\
            (seed, species_side2, min_coverage)
            DB.listSQL.execute(cmd)
            candidates2 = DB.listSQL.fetchall()

        seqid2spcs = {}
        for seqid, spcounter in set(candidates1)|set(candidates2):
            seqid2spcs[seqid] = seqid2spcs.get(seqid, 0) + spcounter

        # From the previously selected ids, filter out those that are
        # two small (few species). For this, I check what cogs pass missing_factor.
        cogs_selection = []
        for missing_species_allowed in xrange(0, int(round(len(species)*missing_factor))+1):
            # filtered_candidates = set([seqid for seqid, counter in seqid2spcs.iteritems() \
            #                           if counter>len(species)*(1-missing_factor)])

            filtered_candidates = set([seqid for seqid, counter in seqid2spcs.iteritems() \
                                       if counter>=len(species)-missing_species_allowed-1]) # -1 is to avoid counting seed 

            filtered_ids = ','.join(map(str, filtered_candidates))
            valid_species = ','.join(map(str, [s for s in species]))

            # Now, lets see how many species we cover with the
            # filtered list of ids, and how well is each species
            # represented.
            sp2hits = {}            
            if filtered_ids != "":
                cmd = """SELECT taxid2, count(id1) from brh WHERE
                taxid1=%s AND id1 IN (%s) AND taxid2 IN (%s) AND coverage>=%s GROUP BY taxid2""" %\
                (seed, filtered_ids, valid_species, min_coverage)
                if DB.listSQL.execute(cmd):
                    for record in DB.listSQL.fetchall():
                        sp2hits[record[0]] = sp2hits.get(record[0], 0) + record[1]

                cmd = """SELECT taxid1, count(id2) from brh WHERE
                taxid2=%s AND id2 IN (%s) AND  taxid1 IN (%s) AND coverage>=%s GROUP BY taxid1""" %\
                (seed, filtered_ids, valid_species, min_coverage)
                if DB.listSQL.execute(cmd):
                    for record in DB.listSQL.fetchall():
                        sp2hits[record[0]] = sp2hits.get(record[0], 0) + record[1]
       
   
                species_side1 = ','.join(map(str, [s for s in species if str(s)>str(seed)]))
                species_side2 = ','.join(map(str, [s for s in species if str(s)<str(seed)]))
                visited_seqids = set()
                all_cogs = []
                visited_seqids = set()
                for c1, seqid in enumerate(filtered_candidates):
                    # Avoid to detect the same COG
                    seedname = str(seed)+":"+str(seqid)
                    if seedname in visited_seqids: 
                        continue
                    COG = [seedname]
                    if species_side1 != "":
                        cmd = """ SELECT taxid2, id2 FROM brh WHERE 
                             taxid1=%s AND id1=%s AND taxid2 IN (%s) AND coverage>=%s""" % \
                            (seed, seqid, species_side1, min_coverage)
                        DB.listSQL.execute(cmd)
                        COG += [str(r[0])+":"+str(r[1]) for r in  DB.listSQL.fetchall()]

                    if species_side2 != "":
                        cmd = """SELECT taxid1, id1 from brh WHERE
                            taxid2=%s AND id2=%s AND taxid1 IN (%s) AND coverage>=%s""" %\
                            (seed, seqid, species_side2, min_coverage)

                        DB.listSQL.execute(cmd)
                        COG += [str(r[0])+":"+str(r[1]) for r in  DB.listSQL.fetchall()]

                    # This ensure that once an id has been used to form a COG,
                    # none of the members will be rescaned
                    for seqname in COG: 
                        visited_seqids.add(seqname)
                    all_cogs.append(COG)
                cogs_selection.append([seed, missing_species_allowed, all_cogs, sp2hits])
            else:
                pass
        cogs, cogs_analysis = get_best_selection(cogs_selection, species)
        best_cogs_selection.append(cogs)
    print "\tFinal cogs:"
    cogs, cogs_analysis = get_best_selection(best_cogs_selection, species)
    return cogs[2], cogs_analysis


def get_best_selection(cogs_selections, species):
    min_score = 0.5
   
    max_cogs = numpy.max([len(data[2]) for data in cogs_selections])
    median_cogs = numpy.median([len(data[2]) for data in cogs_selections])

    def _compare_cog_selection(cs1, cs2):
        seed_1, missing_sp_allowed_1, candidates_1, sp2hits_1 = cs1
        seed_2, missing_sp_allowed_2, candidates_2, sp2hits_2 = cs2

        score_1, min_cov_1, max_cov_1, median_cov_1, cov_std_1, cog_cov_1 = get_cog_score(candidates_1, sp2hits_1, median_cogs)
        score_2, min_cov_2, max_cov_2, median_cov_2, cov_std_2, cog_cov_2 = get_cog_score(candidates_2, sp2hits_2, median_cogs)

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

    cogs_selections.sort(_compare_cog_selection)            
    cogs_selections.reverse()

    header = ['seed',
              'missing sp allowed',
              'spcs covered',
              '#COGs',
              '%sp coverage(avg)',
              'dev.',
              '#COGs worst sp.',
              '#COGs best sp.',
              'sp. in COGS(avg)',
              'SCORE' ]
    print_header = True
    best_cog_selection = None
    cog_analysis = StringIO()
    for i, cogs in enumerate(cogs_selections):
        seed, missing_sp_allowed, candidates, sp2hits = cogs
        sp_percent_coverages = [100*v/float(len(candidates)) for v in sp2hits.values()]
        sp_coverages = sp2hits.values()
        score, min_cov, max_cov, median_cov, cov_std, cog_cov = get_cog_score(candidates, sp2hits, median_cogs)

        if best_cog_selection is None:
            best_cog_selection = i
            flag = "*"
        else:
            flag = ""
        data = (candidates, 
                flag+"%10s" %seed, \
                    missing_sp_allowed, \
                    len(set(sp2hits.keys()))+1, \
                    len(candidates), \
                    numpy.mean(sp_percent_coverages), \
                    numpy.std(sp_percent_coverages), \
                    "% 3d (%0.2f%%)" %(min(sp_coverages),100*min(sp_coverages)/float(len(candidates))), \
                    "% 3d (%0.2f%%)" %(max(sp_coverages),100*max(sp_coverages)/float(len(candidates))), \
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
            sp = seq.split(":")[0]
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


def get_cog_score(candidates, sp2hits, max_cogs):
    cog_cov = numpy.mean([len(cogs) for cogs in candidates])/float(len(sp2hits)+1)
    cog_mean_cov = numpy.mean([len(cogs)/float(len(sp2hits)) for cogs in candidates]) # numero medio de especies en cada cog
    cog_min_sp = numpy.min([len(cogs) for cogs in candidates])

    sp_coverages = [hits/float(len(candidates)) for hits in sp2hits.values()]
    species_covered = len(set(sp2hits.keys()))+1

    nfactor = len(candidates)/float(max_cogs) # Numero de cogs
    min_cov = numpy.min(sp_coverages) # el coverage de la peor especie
    max_cov = numpy.min(sp_coverages)
    median_cov = numpy.median(sp_coverages)
    cov_std = numpy.std(sp_coverages)

    score = numpy.min([nfactor, cog_mean_cov, min_cov])
    return score, min_cov, max_cov, median_cov, cov_std, cog_cov 


        