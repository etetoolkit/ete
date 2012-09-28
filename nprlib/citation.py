__all__ = ["CITATIONS"]

class Citator(object):
    def __init__(self):
        self.citations = set()
        
    def add(self, cite):
        self.citations.add(cite)
        
    def show(self):
        for cit in self.citations:
            print cit
         
