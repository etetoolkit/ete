from ..treelayout import TreeLayout
from ..faces import SeqMotifFace, ScaleFace

from ...utils import InvalidUsage


class LayoutPlot(TreeLayout):
    def __init__(self, name="Plot", width=200, size_prop=None, color_prop=None):
        super().__init__(name)

        self.width = width

        if not (size_prop or color_prop):
            raise InvalidUsage("Either size_prop or color_prop required")

        self.size_prop = size_prop
        self.color_prop = color_prop

    def set_tree_style(self, tree, tree_style):
        def update_vals(metric, node):
            p, minval, maxval, uniqvals = vals[metric]
            prop = node.props.get(p)
            if type(prop) in [int, float]:
                minval = min(minval, prop)
                maxval = max(maxval, prop)
            else if prop is None:
                continue
            else:
                uniqvals.add(prop)

        vals = { 
            "size": [ self.size_prop, 0, 0, set() ] # min, max, unique
            "color":  [ self.color_prop,  0, 0, set() ] # min, max, unique
            }

        for node in tree.traverse():
            if self.size_prop:
                update_vals("size")

            if self.color_prop:
                update_vals("color")
                
        if self.size_prop:
            self.size_range = vals["size"][1:3]

    def get_size(self, node):
        minval, maxval = self.size_range
        return node.props.get(self.size_prop, 0) / maxval * self.size




class LayoutBarplot(TreeLayout):
    def __init__(self, name="Barplot"):
        super().__init__(name)

        self.size_prop = size_prop
        self.color_prop = color_prop

    def set_tree_style(self, tree, tree_style):
        super().set_tree_style(tree, tree_style)

            
        if self.length:
            face = ScaleFace(width=self.width, scale_range=self.scale_range, padding_y=10)
            tree_style.aligned_panel_header.add_face(face, column=0)
