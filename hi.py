from pickle import load, dump

t = Tree()  # whatever tree

with open("tree.pickle", "wb") as handle:
    dump(t, handle)


with open("tree.pickle", "rb") as handle:
    t = load(handle)
