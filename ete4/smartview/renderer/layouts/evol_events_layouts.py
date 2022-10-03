from ..treelayout import TreeLayout


__all__ = [ "LayoutEvolEvents" ]


class LayoutEvolEvents(TreeLayout):
    def __init__(self, name="Evolutionary events", 
            prop="evol_event",
            speciation_color="blue", 
            duplication_color="red",
            legend=True):
        super().__init__(name)
        
        self.prop = prop
        self.speciation_color = speciation_color
        self.duplication_color = duplication_color
        self.legend = legend

        self.active = True

    def set_tree_style(self, tree, tree_style):
        super().set_tree_style(tree, tree_style)
        if self.legend:
            colormap = { "Speciation event": self.speciation_color,
                         "Duplication event": self.duplication_color }
            tree_style.add_legend(title=self.name, 
                    variable="discrete",
                    colormap=colormap)

    def set_node_style(self, node):
        if not node.is_leaf():
            if node.props.get(self.prop, "") == "S":
                node.sm_style["fgcolor"] = self.speciation_color
                node.sm_style["size"] = 2

            elif node.props.get(self.prop, "") == "D":
                node.sm_style["fgcolor"] = self.duplication_color
                node.sm_style["size"] = 2
