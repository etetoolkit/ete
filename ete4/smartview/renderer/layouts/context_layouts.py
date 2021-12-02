from ..treelayout import TreeLayout
from ..faces import ArrowFace


__all__ = [ "LayoutGenomicContext" ]


class LayoutGenomicContext(TreeLayout):

    def __init__(self, name="Genomic context", nside=2,
            conservation_threshold=0, width=70, height=15, collapse_size=1,
            stroke_color="gray", stroke_width="1.5px",
            anchor_stroke_color="black", anchor_stroke_width="3px",
            non_conserved_color="#d0d0d0"):

        super().__init__(name, aligned_faces=True)

        self.nside = nside
        self.conservation_threshold = conservation_threshold

        self.width = width
        self.height = height

        self.collapse_size = collapse_size

        self.anchor_stroke_color = anchor_stroke_color
        self.anchor_stroke_width = anchor_stroke_width
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width

        self.non_conserved_color = non_conserved_color

    def set_tree_style(self, style):
        super().set_tree_style(style)
        style.collapse_size = self.collapse_size

    def set_node_style(self, node):
        if node.is_leaf():
            context = node.props.get("_context")
        else:
            first_leaf = next(node.iter_leaves())
            context = first_leaf.props.get("_context")
        if context:
            for idx, gene in enumerate(context):
                name = gene.get("name")
                color = gene.get("color", "gray")
                conservation = gene.get("conservation_score")
                if conservation is not None\
                    and float(conservation) >= self.conservation_threshold:
                    color = self.non_conserved_color
                strand = gene.get("strand", "+")
                cluster = gene.get("cluster")
                orientation = "left" if strand == "-" else "right"
                text = name + " #" + cluster
                if idx == self.nside:
                    stroke_color = self.anchor_stroke_color
                    stroke_width = self.anchor_stroke_width
                else:
                    stroke_color = self.stroke_color
                    stroke_width = self.stroke_width
                props = {"name": name, "cluster": cluster}
                tooltip = "\n".join(f'{k}: {v}' for k,v in props.items())
                arrow = ArrowFace(self.width, self.height,
                        orientation=orientation, color=color,
                        stroke_color=stroke_color, stroke_width=stroke_width,
                        tooltip=tooltip,
                        text=text,
                        padding_x=2, padding_y=2)
                node.add_face(arrow, position="aligned", column=idx,
                        collapsed_only=(not node.is_leaf()))
