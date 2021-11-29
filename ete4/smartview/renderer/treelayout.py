class TreeLayout():
    def __init__(self, name, ns=None, ts=None):
        self.name = name
        self.active = True
        self.aligned_faces = False
        self.description = ""

        self.always_render = False

    def set_tree_style(self, style):
        if self.aligned_faces:
            style.aligned_panel = True
    
    def set_node_style(self, node):
        pass
        
    def post_render(self):
        pass
