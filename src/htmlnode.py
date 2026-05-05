import re

from textnode import TextNode, TextType

class HTMLNode():
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props



    def to_html(self):
        raise NotImplementedError
    
    ### Turns URL props int HTLM ###
    def props_to_html(self):
        if (self.props is None) or (self.props == {}):
            return str()
        
        parts = []
        for key, value in self.props.items(): ### .items() is needed to get both key and value othwerise it never works
            parts.append(f'{key}="{value}"')
        
        return " " + " ".join(parts) ### leading space join all index in list with " " between.

    def __repr__(self): ### Make sure we can see thing for troubleshooting!!!
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, children=None, props=props)
    
    def to_html(self): ### just two cases of how to deal with a tag and a props input, this is just a setup.
        if self.value is None:
            raise ValueError ("No value set! LeafNode")
        elif self.tag is None:
            return str(self.value)
        elif self.props:
            return f"<a{self.props_to_html()}>{self.value}</a>"
        else:
            return f"<{self.tag}>{self.value}</{self.tag}>"
            
    def __repr__(self): ### Make sure we can see thing for troubleshooting!!!
        return f"LeafNode({self.tag}, {self.value}, {self.props})"

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag=tag, value=None, children=children, props=props)

    def to_html(self):
        if (self.tag is None) or (self.tag == ""):
            raise ValueError ("No <tag> set! ParentNode")
        if (self.children is None) or (self.children == []):
            raise ValueError ("No children set! ParentNode")
        else:
            parts = []
            for node in self.children:
                parts.append(f"{node.to_html()}")
            return f"<{self.tag}>{"".join(parts)}</{self.tag}>"
    
def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    if text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    if text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    if text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    if text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    if text_node.text_type == TextType.IMAGE:
        return LeafNode("img", None, {"src": text_node.url, "alt": text_node.text})
    else:
        raise Exception ("Text Type does not exist!")


def split_nodes_delimiter(list_of_nodes, delimiter, text_type):
    processed_nodes = []
    for node in list_of_nodes:
        if node.text_type != TextType.TEXT:
            processed_nodes.append(node)
        else:
            if node.text.count(delimiter) % 2 !=0:
                raise Exception ("Delimiters unmatched!!!") #Checking for deliminotrs being correctly paired

            split_text = node.text.split(delimiter)
            
            for i, text in enumerate(split_text):
                if i % 2 == 0:
                    processed_nodes.append(TextNode(text, TextType.TEXT))
                else:
                    processed_nodes.append(TextNode(text, text_type))
    
    return processed_nodes
            

def extract_markdown_images(text):
    text_n_img = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return text_n_img

def extract_markdown_links(text):
    text_n_url = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return text_n_url

def split_nodes_image(list_of_nodes):
    processed_nodes = []
    for node in list_of_nodes:
        ### node == TextNode("This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)", TextType.TEXT,)
        if node.text_type != TextType.TEXT:
            processed_nodes.append(node)
        else:
            main_text = node.text
            text_img = extract_markdown_images(node.text) ### list of tuples with "text of img", img_link --> [("image", "https://i.imug.....")]
            for tuple in (text_img):
                text_of_img = tuple[0]
                img_link = tuple[1]
                split_text = main_text.split(f"![{text_of_img}]({img_link})", 1)
                plain_text = split_text[0]
                if plain_text != "":
                    processed_nodes.append(TextNode(plain_text, TextType.TEXT))         #Append text!
                    main_text = main_text.replace(plain_text, "")                       #REMOVE Text from string
                processed_nodes.append(TextNode(text_of_img, TextType.IMAGE, img_link)) #append IMG block
                main_text = main_text.replace(f"![{text_of_img}]({img_link})", "")      #REMOVE IMG form string
            if main_text != "":
                processed_nodes.append(TextNode(main_text, TextType.TEXT)) 
    return processed_nodes
    
def split_nodes_link(list_of_nodes):
    processed_nodes = []
    for node in list_of_nodes:
        if node.text_type != TextType.TEXT:
            processed_nodes.append(node)
        else:
            main_text = node.text
            text_link = extract_markdown_links(node.text)

            for tuple in(text_link):
                text_of_link = tuple[0]
                link = tuple[1]
                split_text = main_text.split(f"[{text_of_link}]({link})", 1)
                plain_text = split_text[0]
                if plain_text != "":
                    processed_nodes.append(TextNode(plain_text, TextType.TEXT))
                    main_text = main_text.replace(plain_text, "")
                processed_nodes.append(TextNode(text_of_link, TextType.LINK, link))
                main_text = main_text.replace(f"[{text_of_link}]({link})", "")
            if main_text != "":
                processed_nodes.append(TextNode(main_text, TextType.TEXT))
    return processed_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)

    return nodes