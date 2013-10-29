import numpy
from StringIO import StringIO
import cPickle
from string import strip
from collections import defaultdict
import logging
import os
import time
log = logging.getLogger("main")


from nprlib.master_task import CogSelectorTask
from nprlib.errors import DataError
from nprlib.utils import (GLOBALS, print_as_table, generate_node_ids,
                          encode_seqname, md5, pjoin)
from nprlib import db

__all__ = ["CogSelector"]

quote = lambda _x: '"%s"' %_x

class CogSelector(CogSelectorTask):
    def __init__(self, target_sp, out_sp, seqtype, conf, confname):
        self.missing_factor = float(conf[confname]["_species_missing_factor"])
        node_id, clade_id = generate_node_ids(target_sp, out_sp)
        # Initialize task
        CogSelectorTask.__init__(self, node_id, "cog_selector",
                                 "MCL-COGs", None, conf[confname])

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
        def sort_cogs_by_size(c1, c2):
            '''
            sort cogs by descending size. If two cogs are the same size, sort
            them keeping first the one with the less represented
            species. Otherwise sort by sequence name sp_seqid.'''
            
            r = -1 * cmp(len(c1), len(c2))
            if r == 0:
                # finds the cog including the less represented species
                c1_repr = numpy.min([sp2cogs[_seq.split(GLOBALS["spname_delimiter"], 1)[0]] for _seq in c1])
                c2_repr = numpy.min([sp2cogs[_seq.split(GLOBALS["spname_delimiter"], 1)[0]] for _seq in c2])
                r = cmp(c1_repr, c2_repr)
                if r == 0:
                    return cmp(sorted(c1), sorted(c2))
                else:
                    return r
            else:
                return r

        def sort_cogs_by_sp_repr(c1, c2):
            c1_repr = numpy.min([sp2cogs[_seq.split(GLOBALS["spname_delimiter"], 1)[0]] for _seq in c1])
            c2_repr = numpy.min([sp2cogs[_seq.split(GLOBALS["spname_delimiter"], 1)[0]] for _seq in c2])
            r = cmp(c1_repr, c2_repr)
            if r == 0:
                r = -1 * cmp(len(c1), len(c2))
                if r == 0:
                    return cmp(sorted(c1), sorted(c2))
                else:
                    return r
            else:
                return r
            
        all_species = self.targets | self.outgroups
        min_species = len(all_species) - int(round(self.missing_factor * len(all_species)))
        smallest_cog, largest_cog = len(all_species), 0
        all_singletons = []
        sp2cogs = defaultdict(int)
        for cognumber, cog in enumerate(open(GLOBALS["cogs_file"])):
            sp2seqs = defaultdict(list)
            for sp, seqid in [map(strip, seq.split(GLOBALS["spname_delimiter"], 1)) for seq in cog.split("\t")]:
                sp2seqs[sp].append(seqid)
            one2one_cog = set()
            for sp, seqs in sp2seqs.iteritems():
                if sp in all_species and len(seqs) == 1:
                    sp2cogs[sp] += 1
                    one2one_cog.add("%s%s%s" %(sp, GLOBALS["spname_delimiter"], seqs[0]))
            smallest_cog = min(smallest_cog, len(one2one_cog))
            largest_cog = max(largest_cog, len(one2one_cog))
            all_singletons.append(one2one_cog)
            #if len(one2one_cog) >= min_species:
            #    valid_cogs.append(one2one_cog)
            
        for sp, ncogs in sp2cogs.iteritems():
            log.log(28, "% 20s  found in single copy in  % 6d (%0.2f%%) COGs " %(sp, ncogs, ncogs/float(cognumber)))

        valid_cogs = sorted([sing for sing in all_singletons if len(sing) >= min_species],
                            sort_cogs_by_size)
       
        log.log(28, "Largest cog size: %s. Smallest cog size: %s" %(
                largest_cog, smallest_cog))
        self.cog_analysis = ""

        self.cogs = []
        # Translate sequence names into the internal DB names
        for co in valid_cogs:
            #print len(co), numpy.median([sp2cogs[_seq.split(GLOBALS["spname_delimiter"], 1)[0]] for _seq in co])
            # self.cogs.append(map(encode_seqname, co))
            encoded_names = db.translate_names(co)
            if len(encoded_names) != len(co):
                print set(co) - set(encoded_names.keys())
                raise DataError("Some sequence ids could not be translated")
            self.cogs.append(encoded_names.values())
            
        # save original cog names
        self.raw_cogs = valid_cogs
                
        # Sort Cogs according to the md5 hash of its content. Random
        # sorting but kept among runs
        map(lambda x: x.sort(), self.cogs)
        self.cogs.sort(lambda x,y: cmp(md5(','.join(x)), md5(','.join(y))))
        log.log(28, "%s COGs detected with at least %s species" %(len(self.cogs), min_species))                
        tm_end = time.ctime()
        #open(pjoin(self.taskdir, "__time__"), "w").write(
        #    '\n'.join([tm_start, tm_end]))
        CogSelectorTask.store_data(self, self.cogs, self.cog_analysis)
