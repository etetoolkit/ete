import textwrap as twrap 

__all__ = ["CITATIONS"]

class Citator(object):
    def __init__(self):
        self.citations = set()
        
    def add(self, ref):
        self.citations.add(ref)
        
    def show(self):
        wrapper = twrap.TextWrapper(width=75, initial_indent="   ",
                              subsequent_indent="      ",
                              replace_whitespace=False)
        citations = sorted(self.citations)
        print "   ========================================================================"
        print "         The following published software and/or algorithms were used.     "
        print "               *** Please, do not forget to cite them! ***                 "
        print "   ========================================================================"
        for ref in citations:
            print wrapper.fill(ref.replace("\n", " ").strip())
         
