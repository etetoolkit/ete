"""
Read trees from a file in nexus format.
"""

# See https://en.wikipedia.org/wiki/Nexus_file

import re

from . import newick as newick_parser


class NexusError(Exception):
    pass



def load(fp, parser=None):
    return loads(fp.read(), parser=parser)


def loads(text, parser=None):
    return {name: newick_parser.loads(newick, parser=parser)
            for name, newick in get_trees(text, parser=parser).items()}


def get_trees(text, parser=None):
    """Return trees as {name: newick} with all the name transformations done."""
    if not re.match(r'^#NEXUS\s*\n', text, flags=re.I):
        raise NexusError('text does not start with "#NEXUS"')

    commands = get_section(text, 'TREES')

    translate = {}
    if 'TRANSLATE' in commands:
        if len(commands['TRANSLATE']) != 1:
            raise NexusError('multiple TRANSLATE commands')
        pairs = commands['TRANSLATE'][0].split(',')
        translate.update(pair.split(maxsplit=1) for pair in pairs)

    trees = {}
    for command in commands.get('TREE', []):
        name_ugly, newick_ugly = command.split('=', maxsplit=1)

        name = name_ugly.strip('\t\r\n "\'')
        newick = newick_ugly.strip() + ';'

        if newick.startswith('['):  # remove possible [&U] or comment
            newick = newick[newick.find(']')+1:].strip()

        trees[name] = apply_translations(translate, newick, parser)

    return trees


def apply_translations(translate, newick, parser=None):
    """Return newick with node names translated according to the given dict."""
    if not translate:
        return newick

    t = newick_parser.loads(newick, parser=parser)

    for node in t:
        if node.name in translate:
            node.name = translate[node.name]

    return newick_parser.dumps(t, parser=parser)


def get_section(text, section_name):
    """Return commands ({name: [args]}) that correspond to the given section."""
    return get_sections(text).get(section_name.upper(), {})


def get_sections(text):
    """Return {section: commands} read from the full text of a nexus file."""
    pattern = r'\nBEGIN\s+(\w+)\s*;(.*?)\nEND\s*;'

    sections = {}
    for m in re.finditer(pattern, text, flags=re.I | re.S):
        name, text_section = m.groups()
        sections[name.upper()] = get_commands(text_section)

    return sections


def get_commands(text_section):
    """Return a dict that for each command has a list with its arguments."""
    pattern = r';.*?(?=;)'

    commands = {}
    for m in re.finditer(pattern, ';' + text_section, flags=re.I | re.S):
        name, args = m.group().strip(';\r\n\t ').split(maxsplit=1)
        commands.setdefault(name.upper(), []).append(args)

    return commands
