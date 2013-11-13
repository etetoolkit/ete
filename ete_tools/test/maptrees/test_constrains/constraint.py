sp2phylome = {
              "A": set("A"),
              "B": set("A"),
              "C": set("C"),
              "D": set("C"),
              "E": set(["A", "C"]),
          }

def is_valid_treeid(treeid, refbranch_species):
    phylome = treeid.split("_")[1]
    for sp in refbranch_species:
        if phylome in sp2phylome[sp]:
            return True
    return False
    
