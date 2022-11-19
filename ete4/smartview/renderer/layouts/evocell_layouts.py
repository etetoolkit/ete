from ..faces import RectFace, TextFace
from ..treelayout import TreeLayout

__all__ = [ "LayoutHumanOGs", "LayoutUCSC"]


class LayoutHumanOGs(TreeLayout):
    def __init__(self, name="Human OGs", human_orth_prop="human_orth",
                 column=5, color="#6b92d6"):
        super().__init__(name)
        self.aligned_faces = True
        self.human_orth_prop = human_orth_prop
        self.column = column
        self.color = color

    def set_node_style(self, node):
        if node.is_leaf():
            human_orth = node.props.get(self.human_orth_prop)
            if human_orth:
                human_orth = " ".join(human_orth.split('|'))
                human_orth_face = TextFace(human_orth, color=self.color)
                node.add_face(human_orth_face, column=self.column, position="aligned")

class LayoutUCSC(TreeLayout):
    def __init__(self, name="UCSC", column=6, 
                 nodecolor="#800000", nodesize=5,
                 textcolor="#c43b5d"):
        super().__init__(name)
        self.aligned_faces = True
        self.column = column
        self.nodecolor = nodecolor
        self.nodesize = nodesize
        self.textcolor = textcolor

    def set_node_style(self, node):
        # if node.is_leaf():
        #     if node.props.get('UCSC'):
        #         ucsc = node.props.get('UCSC')
        #         ucsc_face = TextFace(ucsc, color=self.textcolor)
        #         node.add_face(ucsc_face, column=self.column, position="aligned")
        #         node.sm_style["fgcolor"] = self.nodecolor
        #         node.sm_style["size"] = self.nodesize
        
         if node.is_leaf():
            if node.props.get('UCSC'):
                # tooltip = self.get_html(node)
                # if tooltip:
                #     node.props["tooltip"] = tooltip
 
                ucsc = node.props.get('UCSC')
                ucsc_face = TextFace(ucsc, color=self.textcolor)
                node.add_face(ucsc_face, column=self.column, position="aligned")
                node.sm_style["bgcolor"] = self.nodecolor # highligh clade
                while (node):
                    node = node.up
                    if node:
                        node.sm_style["hz_line_width"] = self.nodesize

class LayoutUCSCtrans(TreeLayout):
    def __init__(self, name="UCSC Trans", ucsc_trans_prop="ucsc_trans",
                 column=4, color="#6b92d6"):
        super().__init__(name)
        self.aligned_faces = True
        self.ucsc_trans_prop = ucsc_trans_prop
        self.column = column
        self.color = color

    def set_node_style(self, node):
        if node.is_leaf():
            ucsc_trans = node.props.get(self.ucsc_trans_prop)
            if ucsc_trans:
                ucsc_trans = " ".join(ucsc_trans.split('|'))
                ucsc_trans_face = TextFace(ucsc_trans, color=self.color)
                node.add_face(ucsc_trans_face, column=self.column, position="aligned")

    # def get_html(self, node):
    #     ucsc = node.props.get("UCSC")
    #     if not ucsc:
    #         return None
        
    #     endpoint = ucsc.split("__")[0]
    #     name = node.props.get("sci_name", node.props.get("name", ""))

    #     return html.format(name, endpoint)

# html = """
# <html>
#     <div style="background-color: #3e32a8;
#                 width: 200px;
#                 height: 150px;
#                 border-radius: 10px;
#                 text-align: center">
#       <h3 style="color:white; padding-top:20px">{}</h3>
#       <br>
#       <hr style="border: 4px dotted white"></hr>
#       <br>
#       <p style="color: white">Whole Adult</p>
#       <div style="margin: 20px 0">
#           <a target="_blank"
#              href="https://cells-test.gi.ucsc.edu/?ds=evocell+{}" 
#              style="
#                   background-color: #d1c92c;
#                   color: white;
#                   text-decoration: none;
#                   padding: 2px 6px 2px 6px;
#                   border-top: 1px solid #CCCCCC;
#                   border-right: 1px solid #333333;
#                   border-bottom: 1px solid #333333;
#                   border-left: 1px solid #CCCCCC;
#                   border-radius: 4px;
#                   padding:10px;
#                   margin-top:5px;
#              ">UCSC</a>
#       </div>
#     </div>
# </html>
# """