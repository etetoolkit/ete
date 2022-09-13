from ..treelayout import TreeLayout


__all__ = [ "LayoutEvolEvents" ]


class LayoutEvolEvents(TreeLayout):
    def __init__(self, name="Evolution events", 
            prop="evol_type",
            speciation_color="blue", duplication_color="red"):
        super().__init__(name)
        
        self.prop = prop
        self.speciation_color = speciation_color
        self.duplication_color = duplication_color

        self.active = True


    def set_node_style(self, node):
        if not node.is_leaf():
            print(node.props.get(self.prop))
            if node.props.get(self.prop, "") == "S":
                node.sm_style["fgcolor"] = self.speciation_color
                node.sm_style["size"] = 2

            elif node.props.get(self.prop, "") == "D":
                node.sm_style["fgcolor"] = self.duplication_color
                node.sm_style["size"] = 2
