import sys

from .common import log, dump

DESC = ""

def populate_args(gtdb_args_p):
    gtdb_args = gtdb_args_p.add_argument_group('GTDB GENERAL OPTIONS')

    gtdb_args.add_argument("--search", dest="search", nargs="+",
                           help="A list of GTDB taxa (like g__Escherichia) or genome accessions")

    gtdb_args.add_argument("--db",  dest="dbfile",
                        type=str,
                        help="""GTDB sqlite3 db file.""")

    gtdb_args.add_argument("--taxdump_file",  dest="taxdumpfile",
                        type=str,
                        help="""Use local GTDB taxdump file instead of downloading it.""")

    gtdb_args.add_argument("--create",  dest="create",
                        action='store_true',
                        default=False,
                        help="""Create taxdump file and exit.""")

    output_args = gtdb_args_p.add_argument_group('GTDB OUTPUT OPTIONS')

    output_args.add_argument("--tree", dest="tree",
                             action='store_true',
                             help=("dump a pruned version of the GTDB taxonomy"
                                   " tree containing target taxa"))

    output_args.add_argument("--descendants", dest="descendants",
                             action='store_true',
                             help=("dump the descendant taxa for each of the queries"))

    output_args.add_argument("--info", dest="info",
                             action='store_true',
                             help="""dump GTDB taxonomy information for each target taxon""")

    output_args.add_argument("--rank_limit", dest="rank_limit",
                             type=str,
                             help=("When used, all nodes under the provided rank"
                                   " are discarded"))

    output_args.add_argument("--full_lineage", dest="full_lineage",
                             action="store_true",
                             help=("When used, topology is not pruned to avoid "
                                   " one-child-nodes, so the complete lineage"
                                   " track leading from root to tips is kept."))


def run(args):
    from .. import GTDBTaxa

    # dump tree by default
    if not args.tree and not args.info and not args.descendants:
        args.tree = True

    gtdb = GTDBTaxa(args.dbfile, args.taxdumpfile)

    if args.create:
        sys.exit(0)

    if not args.search:
        log.error('Search terms should be provided (i.e. --search) ')
        sys.exit(-1)

    names = list(dict.fromkeys(n.strip() for n in args.search))  # unique, in order

    lineages = {}
    for name_lineage in gtdb.get_name_lineage(names):
        lineages.update(name_lineage)

    not_found_names = [n for n in names if n not in lineages]
    if not_found_names:
        log.warn("[%s] not found in the GTDB taxonomy!" %','.join(not_found_names))

    names = [n for n in names if n in lineages]
    ranks = gtdb.get_rank(names)

    if args.tree:
        if len(names) == 1:
            log.info("Dumping GTDB descendants tree for %s" %(names[0]))
            t = gtdb.get_descendant_taxa(names[0], rank_limit=args.rank_limit, return_tree=True)
        else:
            log.info("Dumping GTDB taxonomy of %d taxa..." %(len(names)))
            t = gtdb.get_topology(names, intermediate_nodes=args.full_lineage,
                                  rank_limit=args.rank_limit)

        for n in t.traverse():
            n.add_props(named_lineage='|'.join(n.props.get('named_lineage', [])))
        dump(t, properties=["rank", "named_lineage"])
    elif args.descendants:
        print('# ' + '\t'.join(["Name", "Rank", "descendant_names"]))
        for name in names:
            descendants = gtdb.get_descendant_taxa(name, rank_limit=args.rank_limit)
            print('\t'.join([name, ranks.get(name, ''), '|'.join(descendants)]))
    elif args.info:
        print('# ' + '\t'.join(["Name", "Rank", "Named Lineage"]))
        for name in names:
            print('\t'.join([name, ranks.get(name, ''), ','.join(lineages[name])]))
