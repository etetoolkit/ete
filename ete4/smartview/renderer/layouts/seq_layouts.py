from ete4.core.seqgroup import SeqGroup
from ..treelayout import TreeLayout
from ..faces import AlignmentFace, SeqMotifFace, ScaleFace


__all__ = [ "LayoutAlignment" ]


class LayoutAlignment(TreeLayout):
    def __init__(self, name="Alignment",
            alignment=None, format='seq', width=700, height=15,
            column=0, range=None, summarize_inner_nodes=False):
        super().__init__(name)
        self.alignment = SeqGroup(alignment) if alignment else None
        self.width = width
        self.height = height
        self.column = column
        self.aligned_faces = True
        self.format = format

        self.length = len(next(self.alignment.iter_entries())[1]) if self.alignment else None
        self.scale_range = range or (0, self.length)
        self.summarize_inner_nodes = summarize_inner_nodes

    def set_tree_style(self, tree, tree_style):
        if self.length:
            face = ScaleFace(width=self.width, scale_range=self.scale_range, padding_y=10)
            tree_style.aligned_panel_header.add_face(face, column=self.column)

    def _get_seq(self, node):
        if self.alignment:
            return self.alignment.get_seq(node.name)
        return node.props.get("seq", None)

    def get_seq(self, node):
        if node.is_leaf:
            return self._get_seq(node)

        if self.summarize_inner_nodes:
            # TODO: summarize inner node's seq
            return None
        else:
            first_leaf = next(node.iter_leaves())
            return self._get_seq(first_leaf)

    def set_node_style(self, node):
        seq = self.get_seq(node)

        if seq:
            seqFace = AlignmentFace(seq, seq_format=self.format, bgcolor='grey',
                    width=self.width, height=self.height)
            node.add_face(seqFace, column=self.column, position='aligned',
                    collapsed_only=(not node.is_leaf))
