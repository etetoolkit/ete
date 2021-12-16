from ..treelayout import TreeLayout


__all__ = [ "LayoutEvolEvents" ]


class LayoutEvolEvents(TreeLayout):
    def __init__(self, name="Evolution events", 
            speciation_color="blue", duplication_color="red"):
        super().__init__(name)
        
        self.speciation_color = speciation_color
        self.duplication_color = duplication_color


    def set_node_style(self, node):
        if not node.is_leaf():
            if node.props.get("evoltype", "") == "S":
                node.sm_style["fgcolor"] = self.speciation_color
                node.sm_style["size"] = 2

            elif node.props.get("evoltype", "") == "D":
                node.sm_style["fgcolor"] = self.duplication_color
                node.sm_style["size"] = 2
