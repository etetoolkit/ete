DESC = ""

def populate_args(extract_args_p):    
    extract_args = extract_args_p.add_argument_group('TREE EDIT OPTIONS')

    extract_args.add_argument("--orthologs", dest="orthologs",
                              action="store_true",
                              help=""" """)
    
    extract_args.add_argument("--sptrees", dest="sptrees",
                              action="store_true",
                              help=""" """)
       
    extract_args.add_argument("--duplications", dest="duplications",
                              action="store_true",
                              help=""" """)


