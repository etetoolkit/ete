from ..treelayout import TreeLayout


__all__ = [ "LayoutEteDiffDistance" ]


class LayoutEteDiffDistance(TreeLayout):
    def __init__(self, name="ETE diff distance", diff_node_color="#a50000"):
        super().__init__(name)

        self.diff_node_color = diff_node_color

    def set_node_style(self, node):
        difference = node.props.get("compare_distance")
        if difference:
            node.sm_style["fgcolor"] = self.diff_node_color
            node.sm_style["size"] = 2
            node.sm_style["fgopacity"] = float(difference)
