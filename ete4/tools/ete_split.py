DESC = ""
def populate_args(split_args_p):
    split_args = split_args_p.add_argument_group('TREE SPLIT OPTIONS')

    split_args.add_argument("--size_split", dest="split_at_size",
                          type = int,
                          help=""" """)

    split_args.add_argument("--attr_split", dest="split_at_attr", action='append',
                          type = str,
                          help=""" """) #    "@dist > 10, @support >= 0.9 "


    split_args.add_argument("--dup_split", dest="split_at_duplications",
                          type = str,
                          help=""" """) # split where attr is duplicated
