from ..treelayout import TreeLayout
from ..faces  import RectFace, TextFace
from collections import  OrderedDict
import json



__all__ = [ "LayoutSciName", "LayoutPreferredName", "LayoutAutoName",
        "LayoutCuratedName", "LayoutEukOgs", "LayoutSeeds" ]


sciName2color = {}
taxid2color = {}
with open('/data/smartview_servers/ete4phylocloud/ete4/smartview/renderer/layouts/spongilla_taxa_color_codes.csv') as t:
    for line in t:
        if not line.startswith('#'):
            info = line.split('\t')
            sciName2color[(info[0])] = info[3].strip()
            taxid2color[int(info[1])] = info[3].strip()


def summary(nodes):
    "Return a list of names summarizing the given list of nodes"
    return list(OrderedDict((first_name(node), None) for node in nodes).keys())

def first_name(tree):
    "Return the name of the first node that has a name"
    
    sci_names = []
    for node in tree.traverse('preorder'):
        if node.is_leaf():
            sci_name = node.props.get('sciName')
            sci_names.append(sci_name)

    return next(iter(sci_names))



class LayoutSciName(TreeLayout):
    def __init__(self, name="Scientific name"):
        super().__init__(name, aligned_faces=True)

    def set_node_style(self, node):
        if node.is_leaf():
           
            sci_name = node.props.get('sciName')
            prot_id = node.name.split('.', 1)[1]

            if node.props.get('sciName') in sciName2color.keys():
                color = sciName2color[node.props.get('sciName')]
            else:
                color = 'black'
           
            node.add_face(TextFace(sci_name, color = color, padding_x=2),
                column=0, position="branch_right")

            if len(prot_id) > 40:
                prot_id = prot_id[0:37] + " ..."
           
            node.add_face(TextFace(prot_id, color = 'Gray', padding_x=2), column = 2, position = "aligned")


        else:
            # Collapsed face
            names = summary(node.children)
            texts = names if len(names) < 6 else (names[:3] + ['...'] + names[-2:])
            for i, text in enumerate(texts):

                if text in sciName2color.keys():
                    color = sciName2color[text]
                else:
                    color = 'black'
                node.add_face(TextFace(text, padding_x=2, color = color),
                        position="branch_right", column=1, collapsed_only=True)



class LayoutPreferredName(TreeLayout):

    def __init__(self, name="Preferred name", text_color="#fb3640"):
        super().__init__(name, aligned_faces=True)
        
        self.text_color = text_color

    def set_node_style(self, node):
        if node.is_leaf():
            if node.props.get('Pname'):
                pname= node.props.get('Pname')
                pname_face = TextFace(pname, color=self.text_color)
                node.add_face(pname_face, column = 3, position = "aligned")
        else:
            target_leaf = node.get_leaves()[0]
            if target_leaf.props.get('Pname'):
                pname= target_leaf.props.get('Pname')
                pname_face = TextFace(pname, color=self.text_color)
                node.add_face(pname_face, column = 3, position = "aligned", collapsed_only=True)



class LayoutAutoName(TreeLayout):

    def __init__(self, name="Auto name", text_color="grey"):
        super().__init__(name, aligned_faces=True)
        
        self.text_color = text_color

    def set_node_style(self, node):

        if node.is_leaf():
            if node.props.get('auto_name'):
                spongAutoName = " ".join(node.props.get('auto_name').split("_"))
                if len(spongAutoName) > 30:
                    spongAutoName = spongAutoName[0:27] + " ..."
                spongAutoName_face = TextFace(spongAutoName, color=self.text_color)
                node.add_face(spongAutoName_face, column = 4, position = "aligned")
        else:
            target_leaf = node.get_leaves()[0]
            if target_leaf.props.get('auto_name'):
                spongAutoName = " ".join(target_leaf.props.get('auto_name').split("_"))
                if len(spongAutoName) > 30:
                    spongAutoName = spongAutoName[0:27] + " ..."
                spongAutoName_face = TextFace(spongAutoName, color=self.text_color)
                node.add_face(spongAutoName_face, column = 4, position = "aligned", collapsed_only=True)



class LayoutCuratedName(TreeLayout):

    def __init__(self, name="Preferred name", text_color="black"):
        super().__init__(name, aligned_faces=True)
        
        self.text_color = text_color

    def set_node_style(self, node):
        if node.is_leaf():
            if node.props.get('curated_name') and node.props.get('curated_name') != 'NA':
                spongCuratedName = " ".join(node.props.get('curated_name').split("_"))
                if len(spongCuratedName) > 30:
                    spongCuratedName = spongCuratedName[0:27] + " ..."
                spongCuratedName_face = TextFace(spongCuratedName, color=self.text_color)
                node.add_face(spongCuratedName_face, column = 5, position = "aligned")
        else:
            target_leaf = node.get_leaves()[0]
            if target_leaf.props.get('curated_name') and target_leaf.props.get('curated_name') != 'NA':
                spongCuratedName = " ".join(target_leaf.props.get('curated_name').split("_"))
                if len(spongCuratedName) > 30:
                    spongCuratedName = spongCuratedName[0:27] + " ..."
                spongCuratedName_face = TextFace(spongCuratedName, color=self.text_color)
                node.add_face(spongCuratedName_face, column = 5, position = "aligned", collapsed_only=True)

    

class LayoutEukOgs(TreeLayout):

    def __init__(self, name="OGs euk", text_color="grey"):
        super().__init__(name, aligned_faces=True)
        
        self.text_color = text_color

    def set_node_style(self, node):

        if node.is_leaf():
            if node.props.get('OG_euk'):
                OG = node.props.get('OG_euk')
                og_face = TextFace(OG, color=self.text_color)
                node.add_face(og_face, column = 6, position = "aligned")
        else:
            target_leaf = node.get_leaves()[0]
            if target_leaf.props.get('OG_euk'):
                OG = target_leaf.props.get('OG_euk')
                og_face = TextFace(OG, color=self.text_color)
                node.add_face(og_face, column = 6, position = "aligned", collapsed_only=True)



class LayoutSeeds(TreeLayout):

    def __init__(self, name="Seeds", text_color="grey"):
        super().__init__(name)


    def set_node_style(self, node):

        if node.is_leaf():
            if node.props.get('taxid') == '6055' and "seed" in node.props.keys():
                node.sm_style["bgcolor"] = "#A3423C"

            elif node.props.get('taxid') == '6055' :
                node.sm_style["bgcolor"] = "#DE834D"
