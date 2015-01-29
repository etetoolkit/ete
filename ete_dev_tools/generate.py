DESC = ""

def populate_args(generate_args_p):
    generate_args_p.add_argument('--number', dest='number', type=int, default=1)
    generate_args_p.add_argument('--size', dest='size', type=int, default=10)
    generate_args_p.add_argument('--random_branches', dest='random_branches', action="store_true")

def run(args):
    import random
    from ete_dev import Tree
    
    for n in xrange(args.number):
        t = Tree()
        t.populate(args.size, random_branches=args.random_branches)
        dump(t)
