import random

from .common import dump

DESC = ""

def populate_args(generate_args_p):
    generate_args_p.add_argument('--number', dest='number', type=int, default=1)
    generate_args_p.add_argument('--size', dest='size', type=int, default=10)
    generate_args_p.add_argument('--random_branches', dest='random_branches', action="store_true")

def run(args):
    import random
    from .. import Tree

    for n in range(args.number):
        t = Tree()
        fn = random.random if args.random_branches else None
        t.populate(args.size, dist_fn=fn, support_fn=fn)
        dump(t)
