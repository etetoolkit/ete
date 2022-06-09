class TreeLayout():
    def __init__(self, name, ts=None, ns=None, aligned_faces=False, 
            active=True, legend=True):
        self.name = name
        self.active = active
        self.aligned_faces = aligned_faces
        self.description = ""
        self.legend = legend

        self.always_render = False

        self.ts = ts
        self.ns = ns

    def set_tree_style(self, tree, style):
        if self.aligned_faces:
            style.aligned_panel = True

        if self.ts:
            self.ts(style)
    
    def set_node_style(self, node):
        if self.ns:
            self.ns(node)
