import matplotlib as mpl
import numpy as np

from ..treelayout import TreeLayout
from ..faces import TextFace, RectFace, ScaleFace
from ....treeview.svg_colors import random_color

from ...utils import InvalidUsage


__all__ = [ "LayoutBarplot" ]


def color_gradient(c1, c2, mix=0):
    """ Fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1) """
    # https://stackoverflow.com/questions/25668828/how-to-create-colour-gradient-in-python
    c1 = np.array(mpl.colors.to_rgb(c1))
    c2 = np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)


class LayoutPlot(TreeLayout):
    def __init__(self, name=None, width=200, size_prop=None, color_prop=None, 
            position="aligned", column=0, 
            color_gradient=None, color="red", colors=None,
            padding_x=10, scale=True, legend=True, active=True):
        super().__init__(name, 
                aligned_faces=True if position == "aligned" else False,
                legend=legend, active=active)

        self.width = width
        self.position = position
        self.column = column

        self.scale = scale
        self.padding_x = padding_x

        # if not (size_prop or color_prop):
            # raise InvalidUsage("Either size_prop or color_prop required")

        self.size_prop = size_prop
        self.color_prop = color_prop

        self.size_range = None
        self.color_range = None

        self.color = color
        self.colors = colors
        self.color_gradient = color_gradient
        if self.color_prop and not self.color_gradient:
            self.color_gradient = ("#FFF", self.color)

    def set_tree_style(self, tree, tree_style):
        super().set_tree_style(tree, tree_style)
        def update_vals(metric, node):
            p, minval, maxval, uniqvals = vals[metric]
            prop = node.props.get(p)
            if type(prop) in [int, float]:
                vals[metric][1] = min(minval, prop)
                vals[metric][2] = max(maxval, prop)
            elif prop is None or prop == "":
                return
            else:
                uniqvals.add(prop)

        vals = { 
            "size": [ self.size_prop, 0, 0, set() ],    # min, max, unique
            "color":  [ self.color_prop,  0, 0, set() ] # min, max, unique
            }

        for node in tree.traverse():
            if self.size_prop:
                update_vals("size", node)

            if self.color_prop:
                update_vals("color", node)
                
        if self.size_prop:
            self.size_range = vals["size"][1:3]


        if self.color_prop:
            unique = vals["color"][3]
            if len(unique):
                colors = self.colors or random_color(num=len(unique))
                if type(colors) == dict:
                    self.colors = colors.copy()
                else:
                    colors = list(colors)
                    self.colors = {}
                    for idx, value in enumerate(unique):
                        self.colors[value] = colors[idx % len(colors)]
                if self.legend:
                    tree_style.add_legend(title=self.name,
                            variable="discrete",
                            colormap=self.colors)
            else:
                self.color_range = vals["color"][1:3]
                if self.legend:
                    tree_style.add_legend(title=self.name, 
                            variable="continuous",
                            value_range=self.color_range,
                            color_range=self.color_gradient)

    def get_size(self, node):
        if not self.size_prop:
            return self.width
        minval, maxval = self.size_range
        return float(node.props.get(self.size_prop, 0)) / float(maxval) * self.width

    def get_color(self, node):
        if not self.color_prop:
            return self.color
        prop = node.props.get(self.color_prop)
        if prop is None:
            return None
        if self.color_range:
            minval, maxval = self.color_range
            return color_gradient(*self.color_gradient, (prop - minval) / maxval)
        else:
            return self.colors.get(prop)

    def get_legend(self):
        return self.legend


class LayoutBarplot(LayoutPlot):
    def __init__(self, name=None, width=200, size_prop=None,
            color_prop=None, position="aligned", column=0, 
            color_gradient=None, color="red", colors=None,
            padding_x=10, scale=True, legend=True, active=True):

        name = name or f'Barplot_{size_prop}_{color_prop}'
        super().__init__(name=name, width=width, size_prop=size_prop,
                color_prop=color_prop, position=position, column=column,
                color_gradient=color_gradient, color=color, colors=colors,
                padding_x=padding_x, scale=scale, legend=legend, active=active)

    def set_tree_style(self, tree, tree_style):
        super().set_tree_style(tree, tree_style)
            
        if self.scale and self.size_range:
            scale = ScaleFace(width=self.width, scale_range=self.size_range, 
                    formatter='%.2f',
                    padding_x=self.padding_x, padding_y=2)
            text = TextFace(self.name, max_fsize=11, padding_x=self.padding_x)
            tree_style.aligned_panel_header.add_face(scale, column=self.column)
            tree_style.aligned_panel_header.add_face(text, column=self.column)

    def set_node_style(self, node):
        width = self.get_size(node)
        color = self.get_color(node)
        if width and color:
            tooltip = ""
            if node.name:
                tooltip += f'<b>{node.name}</b><br>'
            if self.size_prop:
                tooltip += f'<br>{self.size_prop}: {width}<br>'
            if self.color_prop:
                tooltip += f'<br>{self.color_prop}: {color}<br>'
            face = RectFace(width, None, color=color, 
                    tooltip=tooltip, padding_x=self.padding_x)
            node.add_face(face, position=self.position, column=self.column,
                    collapsed_only=not node.is_leaf())
