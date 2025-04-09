from . import newick


def extract_data_parser(data, parser):
    """Return data as a string, and the parser to use."""
    # This function basically does:
    #   data = data.read() if hasattr(data, 'read') else data
    #   parser = 'newick' if parser in [None, 'auto'] else parser
    #   return data.lstrip('\n').rstrip(), parser
    # but trying to guess if we have to open a file, and which parser to use.

    # parser may start with 'file-' or 'data-' to force how to interpret data.
    force = None  # to allow to specify if data is a file name or just data
    if type(parser) is str and parser.startswith(('file-', 'data-')):
        force, parser = parser.split('-', 1)  # force can be 'file'/'data'

    # Handle when data is a file-like object.
    if hasattr(data, 'read'):
        if parser is None or parser == 'auto':  # undefined parser?
            parser = guess_parser(data.name)  # try to guess from the name
        data = data.read()  # data is now raw data
        force = 'data'  # specify data as raw data, not a file to read

    # If parser is still undefined, try to guess from file name or content.
    if parser is None or parser == 'auto':  # undefined parser?
        if not force or force == 'file':  # so data could be a path
            parser = guess_parser(data) or 'newick'
        elif force != 'file' and data.lstrip().startswith(('#NEXUS', '#nexus')):
            parser = 'nexus'  # and data is raw data (not a path)
        else:  # everything else, we guess it's a newick
            parser = 'newick'  # whether data is raw data or a path

    # Get data from file if appropriate.
    if force == 'file':  # data is a path to a file
        data = open(data).read()
    elif force == 'data':  # data is just raw data, not a path
        pass
    else:  # guess if it is a path to a file depending on data and format
        if (parser == 'newick' or parser in newick.PARSERS or
            type(parser) is dict):  # for newick format
            if (not data.lstrip('\n').startswith('(') and
                not data.rstrip().endswith(';')):
                data = open(data).read()  # probably a file name - open it
        elif parser == 'nexus':
            if data.endswith(('.nexus', '.NEXUS')):
                data = open(data).read()  # probably a file name - open it
        elif parser == 'ete':
            if data.endswith(('.ete', '.ETE')):
                data = open(data).read()  # probably a file name - open it
        # NOTE: We could try to guess more and/or better.

    # Clean commonly seen whitespace. Safe to do for all our formats.
    return data.lstrip('\n').rstrip(), parser


def guess_parser(name):
    """Return the parser to use if we can guess it from the name."""
    # We don't use name.lower() because "name" may be data, not a name.
    if name.endswith(('.ete', '.ETE')):
        return 'ete'
    elif name.endswith(('.nex', '.nxs', '.nexus', '.NEX', '.NXS', '.NEXUS')):
        return  'nexus'
    elif name.endswith(('.nw', '.newick', '.tree', '.NW', '.NEWICK', '.TREE')):
        return 'newick'
    else:
        return None  # no idea which parser to use
