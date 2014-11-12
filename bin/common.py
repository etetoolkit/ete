
import operator
from string import strip
import re

paired_colors = ['#a6cee3',
                 '#1f78b4',
                 '#b2df8a',
                 '#33a02c',
                 '#fb9a99',
                 '#e31a1c',
                 '#fdbf6f',
                 '#ff7f00',
                 '#cab2d6',
                 '#6a3d9a',
                 '#ffff99',
                 '#b15928']

COLOR_RANKS = {
    "superclass": "#a6cee3",
    "class": "#a6cee3",
    "subclass": "#a6cee3",
    "infraclass": "#a6cee3",
    
    "superfamily": "#1f78b4",
    "family": "#1f78b4",
    "subfamily": "#1f78b4",

    "superkingdom": "#b2df8a",
    "kingdom": "#b2df8a",
    "subkingdom": "#b2df8a",
    
    "superorder": "#33a02c",
    "order": "#33a02c",
    "suborder": "#33a02c",
    "infraorder": "#33a02c",
    "parvorder": "#33a02c",

    "superphylum": "#fdbf6f",
    "phylum": "#fdbf6f",
    "subphylum": "#fdbf6f",
#    "species group": "",
#    "species subgroup": "",
#    "species": "",
#    "subspecies": "",

#    "genus": "",
#    "subgenus": "",

#    "no rank": "",
#    "forma": "",

#    "tribe": "",
#    "subtribe": "",
#    "varietas"
    }


def itertrees(trees, treefile):
    if trees:
        for nw in trees:
            yield nw
    if treefile:
        for line in open(treefile):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            else:
                yield line


def node_matcher(node, filters):
    if not filters:
        return True
    
    for f in filters:        
        node_v = getattr(node, f[0], None)
        if node_v:
            try:
                node_v = type(f[2])(node_v)
            except ValueError:
                pass
            if OPFUNC[f[1]](node_v, f[2]):
                return True
            # else:
            #     print f, node_v, type(node_v)
    return False
            
def _re(q, exp):
    if re.search(exp, q):
        return True
    return False

POSNAMES = {
    "b-right":"branch-right",
    "b-top":"branch-top",
    "b-bottom":"branch-bottom",
    "float":"float",
    "float-behind":"float-behind",
    "aligned":"aligned",
}

OPFUNC = {
    "<":operator.lt,
    ">":operator.gt,
    "=":operator.eq,
    "==":operator.eq,
    "!=":operator.ne,
    ">=":operator.ge,
    "<-":operator.le,
    "~=":_re,
}
    
def parse_faces(face_args):    
    faces = []
    for fargs in face_args:
        face = {"filters":[],
                "value":None,
                "pos": "branch-right",
                "color": "black",
                "size": 12,
                "fstyle":None,
                "column":None,
                "bgcolor":None,
                "format":None,
                "nodetype":"any",
        }

        for clause in map(strip,fargs.split(',')):
            key, value = map(strip, clause.split(":"))
            key = key.lower()
            if key == "if":
                m = re.search("([^=><~!]+)(>=|<=|!=|~=|=|>|<)([^=><~!]+)", value)
                if not m:
                    raise ValueError("Invalid syntaxis in 'if' clause: %s" %clause)
                else:
                    target, op, value = map(strip, m.groups())
                    target = target.lstrip('@')
                    try:
                        value = float(value)                        
                    except ValueError:
                        pass
                        
                    face["filters"].append([target, op, value])                    
            elif key == "pos":
                try:
                    face["pos"] = POSNAMES[value]
                except KeyError:
                    raise ValueError("Invalid face position: %s" %clause)
            elif key == "size":
                face["size"] = int(value)
            elif key == "column":
                face["column"] = int(value)
            elif key == "color":
                if value.endswith("()"):
                    func_name = value[0:-2]
                face[key] = value
            elif key in face:
                face[key] = value
            else:
                raise ValueError("unknown keyword in face options: %s" %clause )
        faces.append(face)
    return faces

