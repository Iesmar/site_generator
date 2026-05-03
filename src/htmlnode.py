

class HTMLNode():
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError
    
    def props_to_html(self):
        
        ### Turn this thing below into normal code that HTLM can read.
        
        {
            "href": "https://www.google.com",
            "target": "_blank",
        }