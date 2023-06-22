from collections import Counter, defaultdict
from ..treelayout import TreeLayout
from ..faces import ArrowFace


__all__ = [ "LayoutGenomicContext" ]


class LayoutGenomicContext(TreeLayout):
    def __init__(self, name="Genomic context", nside=2,
            conservation_threshold=0, width=70, height=15, collapse_size=1,
            gene_name="name", tooltip_props=[],
            stroke_color="gray", stroke_width="1.5px",
            anchor_stroke_color="black", anchor_stroke_width="3px",
            non_conserved_color="#d0d0d0", collapse_conservation=0.2,
            collapse_by_conservation=True):

        super().__init__(name, aligned_faces=True)

        self.nside = nside
        self.conservation_threshold = conservation_threshold
        self.gene_name = gene_name
        self.tooltip_props = tooltip_props

        self.width = width
        self.height = height

        self.collapse_size = collapse_size

        self.anchor_stroke_color = anchor_stroke_color
        self.anchor_stroke_width = anchor_stroke_width
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width

        self.non_conserved_color = non_conserved_color

        self.collapse_conservation = collapse_conservation
        self.collapse_by_conservation = collapse_by_conservation

    def set_tree_style(self, tree, style):
        super().set_tree_style(tree, style)
        style.collapse_size = self.collapse_size

    def set_node_style(self, node):
        context = self.get_context(node)
        if context:
            for idx, gene in enumerate(context):
                name = gene.get("name")
                color = gene.get("color", self.non_conserved_color)
                conservation = gene.get("conservation_score")
                if conservation is not None\
                    and float(conservation) < self.conservation_threshold:
                    color = self.non_conserved_color
                strand = gene.get("strand", "+")
                cluster = gene.get("cluster")
                orientation = "left" if strand == "-" else "right"
                text = gene.get(self.gene_name, "")
                if idx == self.nside:
                    stroke_color = self.anchor_stroke_color
                    stroke_width = self.anchor_stroke_width
                else:
                    stroke_color = self.stroke_color
                    stroke_width = self.stroke_width
                arrow = ArrowFace(self.width, self.height,
                        orientation=orientation, color=color,
                        stroke_color=stroke_color, stroke_width=stroke_width,
                        tooltip=self.get_tooltip(gene),
                        text=text,
                        padding_x=2, padding_y=2)
                node.add_face(arrow, position="aligned", column=idx,
                        collapsed_only=(not node.is_leaf))

    def get_tooltip(self, gene):
        if self.tooltip_props is None:
            return ""

        if self.tooltip_props == []:
            key_props = gene.keys()
        else:
            key_props = self.tooltip_props

        props = {}
        for k,v in gene.items():
            if k in key_props and v and not k in ("strand", "color")\
                    and not k.startswith("_"):
                if k == "hyperlink":
                    k = "Go to"
                    label, url = v
                    v = f'<a href="{url}" target="_blank">{label}</a>'
                props[k] = v

        return "<br>".join(f'{k}: {v}' for k,v in props.items())

    def get_context(self, node):
        if node.is_leaf:
            return node.props.get("_context")

        if not self.collapse_by_conservation:
            first_leaf = next(node.iter_leaves())
            return first_leaf.props.get("_context")

        # Compute conserved context by color
        color_context = defaultdict(list)
        color2genes = {}

        for l in node:
            lcontext = l.props.get("_context")
            for pos, gene in enumerate(lcontext):
                color = gene["color"]
                color_context[pos].append(color)
                color2genes[color] = gene

        ntips = len(node)
        context = []
        for pos, colors in sorted(color_context.items()):
            color, n = Counter(colors).most_common(1)[0]
            if n / ntips >= self.collapse_conservation\
                and color != self.non_conserved_color:
                context.append({
                    **color2genes[color],
                    "vertical_conservation": n / ntips })
            else:
                context.append({ "color": self.non_conserved_color })

        return context
