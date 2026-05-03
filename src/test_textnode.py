import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node1 = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node1, node2)
    
    def test_eq_url(self):
        node1 = TextNode("This is a url", TextType.TEXT, "https://boot.dev")
        node2 = TextNode("This is a url", TextType.TEXT, "https://boot.dev")
        self.assertEqual(node1, node2)
    
    def test_not_eq_text_type(self):
        node1 = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node1, node2)



if __name__ == "__main__":
    unittest.main()