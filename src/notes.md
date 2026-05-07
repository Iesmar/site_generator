tag = "h2"
text = "Hello **world**"
children = text_to_children(text)
node = ParentNode(tag, children)

"# Heading"

"This is a paragraph with two sentences."

"> first line\n> second line"

"- item one\n- item two"

"1. first\n2. second\n3. third"

"```\npython\nprint('hi')\n```"