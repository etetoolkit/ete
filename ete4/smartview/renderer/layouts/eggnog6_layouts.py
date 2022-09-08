from ..treelayout import TreeLayout
from ..faces import TextFace

from ..draw_helpers import summary, Padding
from .evol_events_layouts import LayoutEvolEvents
from .ncbi_taxonomy_layouts import LayoutLastCommonAncestor
from .pfam_layouts import LayoutPfamDomains


__all__ = [ "LayoutScientificName", "LayoutProteinName", "LayoutAlias",
            "LayoutEvolEvents", "LayoutLastCommonAncestor"]


class _LayoutNodeProperty(TreeLayout):
    def __init__(self, prop, name=None,
            pos='branch_right', column=2,
            summarize=True, show_header=False,
            color='black',
            ftype='sans-serif',
            min_fsize=4, max_fsize=15,
            padding_x=5, padding_y=0):
        super().__init__(name or f'{prop} layout')
        self.prop = prop
        self.pos = pos
        self.column = column
        self.aligned_faces = self.pos == 'aligned'
        self.show_header = show_header
        self.color = color
        self.ftype = ftype
        self.min_fsize = min_fsize
        self.max_fsize = max_fsize
        self.padding = Padding(padding_x, padding_y)

        self.summarize = summarize

    def set_node_style(self, node):
        prop = node.props.get(self.prop)
        if prop:
            node.add_face(TextFace(prop, name='leaf_name', 
                            color=self.color, ftype=self.ftype,
                            min_fsize=self.min_fsize, max_fsize=self.max_fsize,
                            padding_x=self.padding.x, padding_y=self.padding.y),
                    position=self.pos, column=self.column, 
                    collapsed_only=(not node.is_leaf()))
        elif self.summarize:
            # Collapsed face
            names = summary(node.children, self.prop)
            texts = names if len(names) < 6 else (names[:3] + ['...'] + names[-2:])
            for i, text in enumerate(texts):
                node.add_face(TextFace(text, name='leaf_name', 
                                color=self.color, ftype=self.ftype,
                                min_fsize=self.min_fsize, max_fsize=self.max_fsize,
                                padding_x=self.padding.x, padding_y=self.padding.y),
                        position=self.pos, column=self.column, collapsed_only=True)

    def set_tree_style(self, tree, tree_style):
        if self.pos == "aligned" and self.show_header:
            face = TextFace(self.name, padding_y=5)
            tree_style.aligned_panel_header.add_face(face, column=self.column)



class LayoutScientificName(_LayoutNodeProperty):
    def __init__(self, prop="sci_name", name="Leaf name",
            pos='branch_right', column=2,
            summarize=True,
            color='black',
            ftype='sans-serif',
            min_fsize=4, max_fsize=15,
            padding_x=5, padding_y=0):
        super().__init__(prop=prop, name=name, pos=pos, column=column,
                summarize=summarize, color=color, ftype=ftype,
                min_fsize=min_fsize, max_fsize=max_fsize,
                padding_x=padding_x, padding_y=padding_y)


class LayoutProteinName(_LayoutNodeProperty):
    def __init__(self, prop="prot_name", name="Protein name",
            pos='aligned', column=3,
            summarize=True,
            color='gray',
            ftype='sans-serif',
            min_fsize=4, max_fsize=15,
            padding_x=5, padding_y=0):
        super().__init__(prop=prop, name=name, pos=pos, column=column,
                summarize=summarize, color=color, ftype=ftype,
                min_fsize=min_fsize, max_fsize=max_fsize,
                padding_x=padding_x, padding_y=padding_y)


class LayoutAlias(_LayoutNodeProperty):
    def __init__(self, prop="alias", name="Alias",
            pos='aligned', column=4,
            summarize=True,
            color='black',
            ftype='sans-serif',
            min_fsize=4, max_fsize=15,
            padding_x=5, padding_y=0):
        super().__init__(prop=prop, name=name, pos=pos, column=column,
                summarize=summarize, color=color, ftype=ftype,
                min_fsize=min_fsize, max_fsize=max_fsize,
                padding_x=padding_x, padding_y=padding_y)
