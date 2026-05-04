import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, extract_markdown_links
from textnode import TextNode, TextType

class TestHTMLNode(unittest.TestCase):
    def test_empty(self):
        node = HTMLNode("a", "Click", None, {})
        result = node.props_to_html()
        self.assertEqual(result, "")
    
    def test_none(self):
        node = HTMLNode("a", "Click", None, None)
        result = node.props_to_html()
        self.assertEqual(result, "")

    def test_correct_output_multiple_props(self):
        node = HTMLNode("a", "Click", None, {"href": "https://www.google.com","target": "_blank",})
        result = node.props_to_html()
        self.assertEqual(result, ' href="https://www.google.com" target="_blank"')

    #######################
    """HTML <TAG> Tests"""
    #######################

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_None_value(self): 
        with self.assertRaises(ValueError): ### Check for ValueError
            LeafNode("p", None).to_html()

    def test_leaf_to_html_None_tag(self):
        node = LeafNode(None, "Nothing here!")
        self.assertEqual(node.to_html(), "Nothing here!")

    def test_leaf_to_html_with_props(self):
        node = LeafNode(
            "a",
            "Click me",
            {"href": "https://example.com", "target": "_blank"}
        )
        self.assertEqual(
            node.to_html(),
            '<a href="https://example.com" target="_blank">Click me</a>'
        )
    
    def test_leaf_to_html_empty_string_value(self):
        node = LeafNode("p", "")
        self.assertEqual(node.to_html(), "<p></p>")

    ###############################
    """TO HTML RECURSION TESTING"""
    ###############################
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_parent_single_child(self):
        child = LeafNode("p", "Hello")
        node = ParentNode("div", [child])
        self.assertEqual(node.to_html(), "<div><p>Hello</p></div>")


    def test_parent_multiple_children(self):
        child1 = LeafNode("p", "Hello")
        child2 = LeafNode("p", "World")
        node = ParentNode("div", [child1, child2])
        self.assertEqual(
            node.to_html(),
            "<div><p>Hello</p><p>World</p></div>"
        )

    def test_parent_no_tag(self):
        child = LeafNode("p", "Hello")
        with self.assertRaises(ValueError):
            ParentNode(None, [child]).to_html()

    def test_parent_no_children(self):
        with self.assertRaises(ValueError):
            ParentNode("div", None).to_html()

    def test_parent_empty_children_list(self):
        with self.assertRaises(ValueError):
            ParentNode("div", []).to_html()

    def test_parent_nested_parent(self):
        child = LeafNode("span", "Nested")
        inner = ParentNode("p", [child])
        outer = ParentNode("div", [inner])

        self.assertEqual(
            outer.to_html(),
            "<div><p><span>Nested</span></p></div>"
        )
    
    def test_parent_with_link_child(self):
        child = LeafNode(
            "a",
            "Open AI",
            {"href": "https://openai.com"}
        )
        node = ParentNode("div", [child])

        self.assertEqual(
            node.to_html(),
            '<div><a href="https://openai.com">Open AI</a></div>'
        )
    def test_nested_parent_multiple_links(self):
        child1 = LeafNode("a", "Google", {"href": "https://google.com"})
        child2 = LeafNode("a", "OpenAI", {"href": "https://openai.com"})

        inner = ParentNode("p", [child1])
        outer = ParentNode("div", [inner, child2])

        self.assertEqual(
            outer.to_html(),
            '<div><p><a href="https://google.com">Google</a></p>'
            '<a href="https://openai.com">OpenAI</a></div>'
        )

    def test_parent_missing_children_none(self):
        with self.assertRaises(ValueError):
            ParentNode("div", None).to_html()
    
    def test_parent_missing_children_empty(self):
        with self.assertRaises(ValueError):
            ParentNode("div", []).to_html()
    
    def test_parent_missing_tag(self):
        child = LeafNode("p", "Hello")
        with self.assertRaises(ValueError):
            ParentNode(None, [child]).to_html()
    
    def test_deeply_nested_parents(self):
        node = ParentNode(
            "div",
            [
                ParentNode(
                    "p",
                    [
                        ParentNode(
                            "span",
                            [LeafNode(None, "Deep")]
                        )
                    ]
                )
            ]
        )

        self.assertEqual(
            node.to_html(),
            "<div><p><span>Deep</span></p></div>"
        )
    
    ##########################
    """TextNode To HTMLNode"""
    ##########################
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")
    
    def test_text_node_to_html_text(self):
        node = TextNode("Hello", TextType.TEXT)
        html_node = text_node_to_html_node(node)

        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "Hello")

    def test_text_node_to_html_bold(self):
        node = TextNode("Bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)

        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold text")

    def test_text_node_to_html_italic(self):
        node = TextNode("Italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)

        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "Italic text")

    def test_text_node_to_html_code(self):
        node = TextNode("print('hi')", TextType.CODE)
        html_node = text_node_to_html_node(node)

        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "print('hi')")

    def test_text_node_to_html_link(self):
        node = TextNode("OpenAI", TextType.LINK, "https://openai.com")
        html_node = text_node_to_html_node(node)

        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "OpenAI")
        self.assertEqual(html_node.props,{"href": "https://openai.com"})

    def test_text_node_to_html_image(self):
        node = TextNode("A cat", TextType.IMAGE, "cat.png")
        html_node = text_node_to_html_node(node)

        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.props, {"src": "cat.png", "alt": "A cat"})

    def test_text_node_invalid_type(self):
        node = TextNode("Bad", "not_real_type")

        with self.assertRaises(Exception):
            text_node_to_html_node(node)

    ################################
    """Split nodes by deliminator"""
    ################################

    def test_Bold_split(self):
        node = TextNode("This is text with a **BOLD-WORD** word", TextType.TEXT)
        node2 = split_nodes_delimiter([node], "**", TextType.BOLD)
        result = [
                    TextNode("This is text with a ", TextType.TEXT),
                    TextNode("BOLD-WORD", TextType.BOLD),
                    TextNode(" word", TextType.TEXT),
                ]
        self.assertEqual(result, node2)
    
    def test_italic_split(self):
        node = TextNode("This is _italic word_ in text", TextType.TEXT)
        node2 = split_nodes_delimiter([node], "_", TextType.ITALIC)

        result = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic word", TextType.ITALIC),
            TextNode(" in text", TextType.TEXT),
        ]

        self.assertEqual(result, node2)

    def test_code_split(self):
        node = TextNode("Text with `code block` inside", TextType.TEXT)
        node2 = split_nodes_delimiter([node], "`", TextType.CODE)

        result = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" inside", TextType.TEXT),
        ]

        self.assertEqual(result, node2)

    def test_code_split(self):
        node = TextNode("Text with `code block` inside", TextType.TEXT)
        node2 = split_nodes_delimiter([node], "`", TextType.CODE)

        result = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" inside", TextType.TEXT),
        ]

        self.assertEqual(result, node2)

    def test_no_delimiter(self):
        node = TextNode("Just plain text", TextType.TEXT)
        node2 = split_nodes_delimiter([node], "**", TextType.BOLD)

        result = [
            TextNode("Just plain text", TextType.TEXT),
        ]

        self.assertEqual(result, node2)

    def test_non_text_node_passthrough(self):
        node = TextNode("Already bold", TextType.BOLD)
        node2 = split_nodes_delimiter([node], "**", TextType.BOLD)

        result = [
            TextNode("Already bold", TextType.BOLD),
        ]

        self.assertEqual(result, node2)

    def test_multiple_bold_blocks_and_spacing(self):
        node = TextNode(
            "Start **A** middle **B** end **C** finish",
            TextType.TEXT
        )

        result = split_nodes_delimiter([node], "**", TextType.BOLD)

        expected = [
            TextNode("Start ", TextType.TEXT),
            TextNode("A", TextType.BOLD),
            TextNode(" middle ", TextType.TEXT),
            TextNode("B", TextType.BOLD),
            TextNode(" end ", TextType.TEXT),
            TextNode("C", TextType.BOLD),
            TextNode(" finish", TextType.TEXT),
        ]

        self.assertEqual(expected, result)

class TestTextToURLandIMG(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images("This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)")
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)
    
    def test_extract_markdown_url(self):
        match = extract_markdown_links("this is text and [this link](https://www.google.com)")
        self.assertListEqual([("this link", "https://www.google.com")], match)
    
    def test_extract_markdown_images2(self):
        matches = extract_markdown_images("This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) This is text with an ![image2](https://i.imgur.com/zjjcJKZ.png)")
        self.assertListEqual([(
            "image", "https://i.imgur.com/zjjcJKZ.png"),
            ("image2", "https://i.imgur.com/zjjcJKZ.png")],
            matches)

    def test_extract_markdown_url_with_image(self):
        match = extract_markdown_links("this is text and [this link](https://www.google.com) some image![image](https://i.imgur.com/zjjcJKZ.png)")
        self.assertListEqual([("this link", "https://www.google.com")], match)

    def test_extract_markdown_img_with_url(self):
        match = extract_markdown_images("this is textand[this link](https://www.google.com) some image![image](https://i.imgur.com/zjjcJKZ.png)")
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], match)    

    

if __name__ == "__main__":
    unittest.main()