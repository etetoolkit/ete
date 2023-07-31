from .common import dump, src_tree_iterator

DESC = ""
def populate_args(annotate_args_p):
    annotate_args = annotate_args_p.add_argument_group("TREE ANNOTATE OPTIONS")
    annotate_args.add_argument("--ncbi", dest="ncbi", action="store_true",
                               help="annotate tree nodes using ncbi taxonomy database.")
    annotate_args.add_argument("--taxid_attr", dest="taxid_attr", default='name',
                               help="attribute used as NCBI taxid number")
    annotate_args.add_argument("--feature", dest="feature", nargs="+", action='append', default=[],
                               help="")
def run(args):
    from .. import Tree, PhyloTree

    features = set()
    for ftree in src_tree_iterator(args):
        if args.ncbi:
            tree = PhyloTree(open(ftree))
            features.update(["taxid", "name", "rank", "bgcolor", "sci_name",
                             "collapse_subspecies", "named_lineage", "lineage"])
            tree.annotate_ncbi_taxa(args.taxid_attr)
        else:
            tree = Tree(open(ftree))

        type2cast = {"str":str, "int":int, "float":float, "set":set, "list":list}

        for annotation in args.feature:
            aname, asource, amultiple, acast = None, None, False, str
            for field in annotation:
                try:
                    key, value = [_f.strip() for _f in field.split(":")]
                except Exception:
                    raise ValueError("Invalid feature option [%s]" %field )

                if key == "name":
                    aname = value
                elif key == "source":
                    asource = value
                elif key == "multiple":
                    #append
                    amultiple = value
                elif key == "type":
                    try:
                        acast = type2cast[value]
                    except KeyError:
                        raise ValueError("Invalid feature type [%s]" %field)
                else:
                    raise ValueError("Unknown feature option [%s]" %field)

            if not aname and not asource:
                ValueError('name and source are required when annotating a new feature [%s]'
                           % annotation)

            features.add(aname)
            for line in open(asource, 'r'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                nodenames, attr_value = [_ln.strip() for _ln in line.split('\t')]
                nodenames = list(map(str.strip, nodenames.split(',')))
                relaxed_grouping = True
                if nodenames[0].startswith('!'):
                    relaxed_grouping = False
                    nodenames[0] = nodenames[0][1:]

                if len(nodenames) > 1:
                    target_node = tree.get_common_ancestor(nodenames)
                    if not relaxed_grouping:
                        pass
                        # do something
                else:
                    target_node = tree & nodenames[0]

                if hasattr(target_node, aname):
                    log.warning('Overwriting annotation for node" [%s]"' %nodenames)
                else:
                    target_node.add_property(aname, acast(attr_value))

        dump(tree, properties=features)
