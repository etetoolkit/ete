import textwrap as twrap 

__all__ = ["CITATIONS"]

class Citator(object):
    def __init__(self):
        self.citations = set()
        
    def add(self, authors, title, ref):
        self.citations.add((authors, title, ref))
        
    def show(self):
        wrapper = twrap.TextWrapper(width=75, initial_indent="   ",
                              subsequent_indent="      ",
                              replace_whitespace=False)
        citations = sorted(self.citations)
        print "   ========================================================================"
        print "         The following published software and/or algorithms were used.     "
        print "               *** Please, do not forget to cite them! ***                 "
        print "   ========================================================================"
        for au, ti, ref in citations:
            print wrapper.fill(' '.join([au, ti, ref]))
         
