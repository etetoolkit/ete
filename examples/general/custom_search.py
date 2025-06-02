from ete4 import Tree

t = Tree('((H:0.3,I:0.1):0.5, A:1, (B:0.4,(C:1,D:1):0.5):0.5);')

matches = [n for n in t.leaves() if n.dist > 0.3]

print(len(matches), 'leaves have distance > 0.3')
