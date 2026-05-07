import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes
from textnode import TextNode, TextType
from htmlblocks import BlockType, markdown_to_blocks, block_to_block_type, markdown_to_html_node, extract_title

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

class TestSplitNodesToIMG(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an111 ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an111 ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

class TestSplitNodesToIMG(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an111 ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png) plus some trailing text",
            TextType.TEXT,
        )

        new_nodes = split_nodes_image([node])

        self.assertListEqual(
            [
                TextNode("This is text with an111 ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image",
                    TextType.IMAGE,
                    "https://i.imgur.com/3elNhQu.png",
                ),
                TextNode(" plus some trailing text", TextType.TEXT),
            ],
            new_nodes,
        )
    
    def test_split_images_only_image(self):
        node = TextNode(
            "![Boot.dev logo](https://blog.boot.dev/img/logo.png)",
            TextType.TEXT,
        )

        new_nodes = split_nodes_image([node])

        self.assertListEqual(
            [
                TextNode(
                    "Boot.dev logo",
                    TextType.IMAGE,
                    "https://blog.boot.dev/img/logo.png",
                ),
            ],
            new_nodes,
        )

class TestSplitNodesToLINKS(unittest.TestCase):

    def test_split_links_basic(self):
        node = TextNode(
            "This is text with a [link](https://www.google.com)",
            TextType.TEXT,
        )

        new_nodes = split_nodes_link([node])

        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://www.google.com"),
            ],
            new_nodes,
        )
    
    def test_split_links_multiple(self):
        node = TextNode(
            "Here is a [first](https://first.com) and a [second](https://second.com)",
            TextType.TEXT,
        )

        new_nodes = split_nodes_link([node])

        self.assertListEqual(
            [
                TextNode("Here is a ", TextType.TEXT),
                TextNode("first", TextType.LINK, "https://first.com"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("second", TextType.LINK, "https://second.com"),
            ],
            new_nodes,
        )
    
    def test_split_links_with_trailing_text(self):
        node = TextNode(
            "Visit [OpenAI](https://openai.com) for more info please",
            TextType.TEXT,
        )

        new_nodes = split_nodes_link([node])

        self.assertListEqual(
            [
                TextNode("Visit ", TextType.TEXT),
                TextNode("OpenAI", TextType.LINK, "https://openai.com"),
                TextNode(" for more info please", TextType.TEXT),
            ],
            new_nodes,
        )
    
    def test_split_links_only_link(self):
        node = TextNode(
            "[Boot.dev](https://boot.dev)",
            TextType.TEXT,
        )

        new_nodes = split_nodes_link([node])

        self.assertListEqual(
            [
                TextNode("Boot.dev", TextType.LINK, "https://boot.dev"),
            ],
            new_nodes,
        )

class TestTextToTextNodes(unittest.TestCase):
    
    def test_text_to_textnodes_multi_single_elements(self):
        node = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        test_node = text_to_textnodes(node)

        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            test_node
        )
    
    def test_text_to_textnodes_plain_text(self):
        text = "just plain text"
        actual = text_to_textnodes(text)
        self.assertListEqual(
            [TextNode("just plain text", TextType.TEXT)],
            actual,
        )
    
    def test_text_to_textnodes_starts_with_link(self):
        text = "[boot.dev](https://boot.dev) is useful"
        actual = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("boot.dev", TextType.LINK, "https://boot.dev"),
                TextNode(" is useful", TextType.TEXT),
            ],
            actual,
        )

    def test_text_to_textnodes_multiple_links_images_and_bold(self):
        node = (
            "This is **bold1** text with a [first link](https://first.com), "
            "then **bold2** and an ![first image](https://img1.com/image1.png), "
            "followed by a [second link](https://second.com), "
            "then **bold3** and another ![second image](https://img2.com/image2.png) "
            "plus a final [third link](https://third.com)."
        )

        test_node = text_to_textnodes(node)

        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("bold1", TextType.BOLD),
                TextNode(" text with a ", TextType.TEXT),
                TextNode("first link", TextType.LINK, "https://first.com"),
                TextNode(", then ", TextType.TEXT),
                TextNode("bold2", TextType.BOLD),
                TextNode(" and an ", TextType.TEXT),
                TextNode("first image", TextType.IMAGE, "https://img1.com/image1.png"),
                TextNode(", followed by a ", TextType.TEXT),
                TextNode("second link", TextType.LINK, "https://second.com"),
                TextNode(", then ", TextType.TEXT),
                TextNode("bold3", TextType.BOLD),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second image", TextType.IMAGE, "https://img2.com/image2.png"),
                TextNode(" plus a final ", TextType.TEXT),
                TextNode("third link", TextType.LINK, "https://third.com"),
                TextNode(".", TextType.TEXT),
            ],
            test_node,
        )

class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_clean(self):
        md = """
This is **bolded** paragraph 

 This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line  

   - This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )        

class TestBlockToBlockType(unittest.TestCase):
    def test_heading_level_1(self):
        block = "# Heading One"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_level_6(self):
        block = "###### Heading Six"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_invalid_heading_no_space_falls_to_paragraph(self):
        block = "##Invalid heading"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_heading_level_over_6(self):
        block = "####### Heading 7"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_quote_single_line(self):
        block = "> This is a quote"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_multi_line(self):
        block = "> First line\n> Second line\n> Third line"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_invalid_quote_mixed_lines_falls_to_paragraph(self):
        block = "> First line\nSecond line"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_unordered_list_single(self):
        block = "- Item one"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERD_LIST)

    def test_unordered_list_multi(self):
        block = "- Item one\n- Item two\n- Item three"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERD_LIST)

    def test_invalid_unordered_list_falls_to_paragraph(self):
        block = "- Item one\n-Item two"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_single(self):
        block = "1. First item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_multi(self):
        block = "1. First item\n2. Second item\n3. Third item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_invalid_ordered_list_wrong_sequence_falls_to_paragraph(self):
        block = "1. First item\n3. Third item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_invalid_ordered_list_no_space_falls_to_paragraph(self):
        block = "1. First item\n2.Third item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)    

    def test_code_block(self):
        block = "```\nprint('Hello world')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_invalid_code_block_falls_to_paragraph(self):
        block = "```\nprint('Hello world')"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_plain_paragraph(self):
        block = "This is just a normal paragraph."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_markdown_to_html_node_structure_paragraph(self):
        md = "hello world"

        node = markdown_to_html_node(md)

        self.assertEqual(node.tag, "div")
        self.assertEqual(len(node.children), 1)

        paragraph = node.children[0]
        self.assertEqual(paragraph.tag, "p")
        self.assertEqual(len(paragraph.children), 1)

        text = paragraph.children[0]
        self.assertEqual(text.value, "hello world")
    
    def test_markdown_to_html_node_structure_heading(self):
        md = "## hello world"

        node = markdown_to_html_node(md)

        self.assertEqual(node.tag, "div")
        self.assertEqual(len(node.children), 1)

        heading = node.children[0]
        self.assertEqual(heading.tag, "h2")
    
    def test_markdown_to_html_node_structure_code(self):
        md = """```
hello
```"""

        node = markdown_to_html_node(md)

        pre = node.children[0]
        self.assertEqual(pre.tag, "pre")

        code = pre.children[0]
        self.assertEqual(code.tag, "code")

    def test_debug_tree_shape(self):
        md = "your markdown here"

        node = markdown_to_html_node(md)

        #print(node)
        #print(node.children)
    
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

class TestMarkdownToHtmlNodeLists(unittest.TestCase):

    def test_unordered_list_plain_text(self):
        markdown = """
- First item
- Second item
- Third item
"""
        node = markdown_to_html_node(markdown)

        expected_html = (
            "<div><ul><li>First item</li><li>Second item</li><li>Third item</li></ul></div>"
        )

        self.assertEqual(node.to_html(), expected_html)

    def test_unordered_list_with_bold_and_italic(self):
        markdown = """
- This is **bold**
- This is _italic_
- This is **bold** and _italic_
"""
        node = markdown_to_html_node(markdown)

        expected_html = (
            "<div><ul><li>This is <b>bold</b></li><li>This is <i>italic</i></li><li>This is <b>bold</b> and <i>italic</i></li></ul></div>"
        )

        self.assertEqual(node.to_html(), expected_html)

    def test_ordered_list_plain_text(self):
        markdown = """
1. First item
2. Second item
3. Third item
"""
        node = markdown_to_html_node(markdown)

        expected_html = (
            "<div><ol><li>First item</li><li>Second item</li><li>Third item</li></ol></div>"
        )

        self.assertEqual(node.to_html(), expected_html)

    def test_ordered_list_with_bold_and_italic(self):
        markdown = """
1. This is **bold**
2. This is _italic_
3. This is **bold** and _italic_
"""
        node = markdown_to_html_node(markdown)

        expected_html = (
            "<div><ol><li>This is <b>bold</b></li><li>This is <i>italic</i></li><li>This is <b>bold</b> and <i>italic</i></li></ol></div>"
        )

        self.assertEqual(node.to_html(), expected_html)

class ExtractTitleFromMarkdown(unittest.TestCase):
    def test_unordered_list_plain_text(self):
        markdown = """
This is some radnom text

# This is A heading lvl 1

- Second item
- Third item
"""
        node = extract_title(markdown)

        expectedresult = ("This is A heading lvl 1")
        self.assertEqual(node,expectedresult)

    def test_unordered_list_plain_text(self):
        markdown = """
This is some radnom text

## This is A heading lvl 2
"""
        with self.assertRaises(Exception):
            extract_title(markdown)
    
    def test_unordered_list_plain_text(self):
        markdown = """
This is some radnom text

This has nothing
"""
        with self.assertRaises(Exception):
            extract_title(markdown)


if __name__ == "__main__":
    unittest.main()