class TreeLayout():
    def __init__(self, name, ts=None, ns=None):
        self.name = name
        self.active = True
        self.aligned_faces = False
        self.description = ""

        self.always_render = False

        self.ts = ts
        self.ns = ns

    def set_tree_style(self, style):
        if self.aligned_faces:
            style.aligned_panel = True

        if self.ts:
            self.ts(style)
    
    def set_node_style(self, node):
        if self.ns:
            self.ns(node)
