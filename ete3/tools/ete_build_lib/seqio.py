from __future__ import absolute_import
from __future__ import print_function

import re
import os
import sys
import time
from collections import defaultdict

from .utils import log
from . import db
from .errors import ConfigError, DataError


def iter_fasta_seqs(source):
    """Iter records in a FASTA file"""

    if os.path.isfile(source):
        if source.endswith('.gz'):
            import gzip
            _source = gzip.open(source)
        else:
            _source = open(source, "r")
    else:
        _source = iter(source.split("\n"))

    seq_chunks = []
    seq_name = None
    for line in _source:
        line = line.strip()
        if line.startswith('#') or not line:
            continue       
        elif line.startswith('>'):
            # yield seq if finished
            if seq_name and not seq_chunks:
                raise ValueError("Error parsing fasta file. %s has no sequence" %seq_name)
            elif seq_name:
                yield seq_name, ''.join(seq_chunks)
                
            seq_name = line[1:].split('\t')[0].strip()
            seq_chunks = []
        else:
            if seq_name is None:
                raise Exception("Error reading sequences: Wrong format.")
            seq_chunks.append(line.replace(" ",""))

    # return last sequence
    if seq_name and not seq_chunks:
        raise ValueError("Error parsing fasta file. %s has no sequence" %seq_name)
    elif seq_name:
        yield seq_name, ''.join(seq_chunks)        

        
def load_sequences(args, seqtype, target_seqs, target_species, cached_seqs):
    seqfile = getattr(args, "%s_seed_file" %seqtype)
    skipped_seqs = 0                   
    loaded_seqs = {} 
                   
    log.log(28, "Reading %s sequences from %s...", seqtype, seqfile)
    fix_dups = True if args.rename_dup_seqnames else False
    if args.seq_name_parser:
        NAME_PARSER = re.compile(args.seq_name_parser)
        
    seq_repl = {}
    # Clear problematic symbols
    if not args.no_seq_correct:
        seq_repl["."] = "-"
        seq_repl["*"] = "X"
        if seqtype == "aa":
            seq_repl["J"] = "X" # phyml fails with J
            seq_repl["O"] = "X" # mafft fails with O
            seq_repl["U"] = "X" # selenocysteines
    if args.dealign:
        seq_repl["-"] = ""
        seq_repl["."] = ""
    if seq_repl:
        SEQ_PARSER = re.compile("(%s)" %('|'.join(map(re.escape,seq_repl.keys()))))

    start_time = time.time()
    dupnames = defaultdict(int)
    for c1, (raw_seqname, seq) in enumerate(iter_fasta_seqs(seqfile)):
        if c1 % 10000 == 0 and c1:
            if loaded_seqs and target_seqs:  # only works when workflow is supermatrix
                estimated_time = ((len(target_seqs) - len(loaded_seqs)) * (time.time() - start_time)) / float(c1)
                percent = (len(loaded_seqs) / float(len(target_seqs))) * 100.0
            else:
                percent = 0
                estimated_time = -1            
            print("loaded:%07d skipped:%07d scanned:%07d %0.1f%%" %\
                  (len(loaded_seqs), skipped_seqs, c1, percent), end='\n', file=sys.stderr)
        
        if args.seq_name_parser:
            name_match = re.search(NAME_PARSER, raw_seqname)
            if name_match:
                seqname = name_match.groups()[0]
            else:
                raise ConfigError("Could not parse sequence name: %s" %raw_seqname)
        else:
            seq_name = raw_seqname
        
        if target_seqs and loaded_seqs == len(target_seqs):
            break 
        elif target_seqs and seqname not in target_seqs:
            skipped_seqs += 1
            continue
        elif target_species and seqname.split(args.spname_delimiter, 1)[0] not in target_species:
            skipped_seqs += 1
            continue
            
        if seq_repl:
            seq = SEQ_PARSER.sub(lambda m: seq_repl[m.groups()[0]], seq)
            
        if cached_seqs:
            try:
                seqid = cached_seqs[seqname]
            except:
                raise DataError("%s sequence not found in %s sequence file" %(seqname, seqtype))
        else:
            seqid = "S%09d" %(len(loaded_seqs)+1)

        if seqname in loaded_seqs:
            if fix_dups:
                dupnames[seqname] += 1
                seqname = seqname + "_%d"%dupnames[seqname]
            else:
                raise DataError("Duplicated sequence name [%s] found. Fix manually or use --rename-dup-seqnames to continue" %(seqname))
            
            
        loaded_seqs[seqname] = seqid
        db.add_seq(seqid, seq, seqtype)
        if not cached_seqs:            
            db.add_seq_name(seqid, seqname)
    print('\n', file=sys.stderr)
    db.seqconn.commit()
    return loaded_seqs



    
        # if not args.no_seq_checks:
        #     # Load unknown symbol inconsistencies
        #     if seqtype == "nt" and set(seq) - NT:
        #         seq2unknown[seqtype][seqname] = set(seq) - NT
        #     elif seqtype == "aa" and set(seq) - AA:
        #         seq2unknown[seqtype][seqname] = set(seq) - AA

        # seq2seq[seqtype][seqname] = seq
        # seq2length[seqtype][seqname] = len(seq)


    # Initialize target sets using aa as source
    # if not target_seqs: # and seqtype == "aa":
    #     target_seqs = set(visited_seqs[source_seqtype])

    # if skipped_seqs:
    #     log.warning("%d sequences will not be used since they are"
    #                 "  not present in the aa seed file." %skipped_seqs)

    # return target_seqs, visited_seqs, seq2length, seq2unknown, seq2seq








def check_seq_integrity(args, target_seqs, visited_seqs, seq2length, seq2unknown, seq2seq):
    log.log(28, "Checking data consistency ...")
    source_seqtype = "aa" if "aa" in GLOBALS["seqtypes"] else "nt"
    error = ""

    # Check for duplicate ids
    if not args.ignore_dup_seqnames:
        seq_number = len(set(visited_seqs[source_seqtype]))
        if len(visited_seqs[source_seqtype]) != seq_number:
            counter = defaultdict(int)
            for seqname in visited_seqs[source_seqtype]:
                counter[seqname] += 1
            duplicates = ["%s\thas %d copies" %(key, value) for key, value in six.iteritems(counter) if value > 1]
            error += "\nDuplicate sequence names.\n"
            error += '\n'.join(duplicates)

    # check that the seq of all targets is available
    if target_seqs:
        for seqtype in GLOBALS["seqtypes"]:
            missing_seq = target_seqs - set(seq2seq[seqtype].keys())
            if missing_seq:
                error += "\nThe following %s sequences are missing:\n" %seqtype
                error += '\n'.join(missing_seq)

    # check for unknown characters
    for seqtype in GLOBALS["seqtypes"]:
        if seq2unknown[seqtype]:
            error += "\nThe following %s sequences contain unknown symbols:\n" %seqtype
            error += '\n'.join(["%s\tcontains:\t%s" %(k,' '.join(v)) for k,v in six.iteritems(seq2unknown[seqtype])] )

    # check for aa/cds consistency
    REAL_NT = set('ACTG')
    if GLOBALS["seqtypes"] == set(["aa", "nt"]):
        inconsistent_cds = set()
        for seqname, ntlen in six.iteritems(seq2length["nt"]):
            if seqname in seq2length["aa"]:
                aa_len = seq2length["aa"][seqname]
                if ntlen / 3.0 != aa_len:
                    inconsistent_cds.add("%s\tExpected:%d\tFound:%d" %\
                                         (seqname,
                                         aa_len*3,
                                         ntlen))
                else:
                    if not args.no_seq_checks:
                        for i, aa in enumerate(seq2seq["aa"][seqname]):
                            codon = seq2seq["nt"][seqname][i*3:(i*3)+3]
                            if not (set(codon) - REAL_NT):
                                if GENCODE[codon] != aa:
                                    log.warning('@@2:Unmatching codon in seq:%s, aa pos:%s (%s != %s)@@1: Use --no-seq-checks to skip' %(seqname, i, codon, aa))
                                    inconsistent_cds.add('Unmatching codon in seq:%s, aa pos:%s (%s != %s)' %(seqname, i, codon, aa))

        if inconsistent_cds:
            error += "\nUnexpected coding sequence length for the following ids:\n"
            error += '\n'.join(inconsistent_cds)

    # Show some stats
    all_len = list(seq2length[source_seqtype].values())
    max_len = _max(all_len)
    min_len = _min(all_len)
    mean_len = _mean(all_len)
    std_len = _std(all_len)
    outliers = []
    for v in all_len:
        if abs(mean_len - v) >  (3 * std_len):
            outliers.append(v)
    log.log(28, "Total sequences:  %d" %len(all_len))
    log.log(28, "Average sequence length: %d +- %0.1f " %(mean_len, std_len))
    log.log(28, "Max sequence length:  %d" %max_len)
    log.log(28, "Min sequence length:  %d" %min_len)

    if outliers:
        log.warning("%d sequence lengths look like outliers" %len(outliers))

    return error


def hash_names(target_names):
    """Given a set of strings of variable lengths, it returns their
    conversion to fixed and safe hash-strings.
    """
    # An example of hash name collision
    #test= ['4558_15418', '9600_21104', '7222_13002', '3847_37647', '412133_16266']
    #hash_names(test)

    log.log(28, "Generating safe sequence names...")
    hash2name = defaultdict(list)
    for c1, name in enumerate(target_names):
        print(c1, "\r", end=' ', file=sys.stderr)
        sys.stderr.flush()
        hash_name = encode_seqname(name)
        hash2name[hash_name].append(name)

    collisions = [(k,v) for k,v in six.iteritems(hash2name) if len(v)>1]
    #GLOBALS["name_collisions"] = {}
    if collisions:
        visited = set(hash2name.keys())
        for old_hash, coliding_names in collisions:
            logindent(2)
            log.log(20, "Collision found when hash-encoding the following gene names: %s", coliding_names)
            niter = 1
            valid = False
            while not valid or len(new_hashes) < len(coliding_names):
                niter += 1
                new_hashes = defaultdict(list)
                for name in coliding_names:
                    hash_name = encode_seqname(name*niter)
                    new_hashes[hash_name].append(name)
                valid = set(new_hashes.keys()).isdisjoint(visited)

            log.log(20, "Fixed with %d concatenations! %s", niter, ', '.join(['%s=%s' %(e[1][0], e[0]) for e in  six.iteritems(new_hashes)]))
            del hash2name[old_hash]
            hash2name.update(new_hashes)
            #GLOBALS["name_collisions"].update([(_name, _code) for _code, _name in new_hashes.iteritems()])
            logindent(-2)
    #collisions = [(k,v) for k,v in hash2name.iteritems() if len(v)>1]
    #log.log(28, "Final collisions %s", collisions )
    hash2name = {k: v[0] for k,v in six.iteritems(hash2name)}
    name2hash = {v: k for k,v in six.iteritems(hash2name)}
    return name2hash, hash2name

