import re
from enum import Enum

from textnode import TextNode, TextType
from htmlnode import ParentNode, LeafNode, text_to_textnodes, text_node_to_html_node

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERD_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"



def markdown_to_blocks(markdown):

    segments_clean_blocks = [segment.strip() for segment in markdown.strip().split("\n\n")]
    ### DOES NOT REMOVE - in block whitespaces.
    return segments_clean_blocks
                
def block_to_block_type(block):
    
    if block.startswith("#"):
        hashcount = 0
        for i in range(0, len(block)):
            if block[i] == "#":
                hashcount += 1
            else:
                break
            ### extra features ###
            #if hashcount >=7 : # This can be implimanted later.
            #    pass
                #raise Exception ("Heading level over 6")
            #elif block[i+1] != " ": # This can be implimanted later.
            #    pass
                #raise Exception ("Heading detected but no SPACE")
            ### End ###
        if (len(block) > hashcount) and (block[hashcount] == " ") and (hashcount <= 6):
            return BlockType.HEADING
        else:
            pass
    
    
    if block.startswith(">"):
        lines = block.split("\n")
        quotecount = 0
        for line in lines:
            if line.startswith(">"):
                quotecount += 1
        if quotecount == len(lines):
            return BlockType.QUOTE
        
    if block.startswith("- "):
        lines = block.split("\n")
        pointcount = 0
        for line in lines:
            if line.startswith("- "):
                pointcount += 1
        if pointcount == len(lines):
            return BlockType.UNORDERD_LIST
    
    if block.startswith("1. "):
        lines = block.split("\n")
        count = 1
        for line in lines:
            if line.startswith(f"{count}. "):
                count += 1        
        if (count - 1) == len(lines):
            return BlockType.ORDERED_LIST

    if block.startswith("```\n") and block.endswith("\n```"):
        return BlockType.CODE

    else: # It can only be a Paragraph.
        return BlockType.PARAGRAPH

def markdown_to_html_node(markdown):
    blocks_in_markdown = markdown_to_blocks(markdown)

    html_nodes = []

    for block in blocks_in_markdown:
        block_type = block_to_block_type(block)
        if block_type == BlockType.HEADING: 
            
            level = 0
            while block[level] == "#":
                level += 1
            
            text_in_block = block[level+1:]
            children_in_block = text_to_children(text_in_block) # helper function that scans text->procceses into list.
            node = ParentNode(f"h{level}", children_in_block)
            
            html_nodes.append(node)
        
        elif block_type == BlockType.CODE:
            text_in_block = TextNode(block[4:-3], TextType.TEXT)
            text_in_html = text_node_to_html_node(text_in_block)
            inner_html_code = ParentNode("code", [text_in_html])      # [] text_in_html - needed - ParentNode expect. list
            outer_html_code = ParentNode("pre", [inner_html_code])    # [] text_in_html - needed - ParentNode expect. list

            html_nodes.append(outer_html_code)
        
        elif block_type == BlockType.QUOTE:
            lines = block.split("\n")

            cleaned_lines = []
            for line in lines:
                cleaned_lines.append(line[1:].strip())
            
            outer_html_code # QUOTES dont have a inner code line its just <blockquote>
            for line1 in cleaned_lines:
                text_line = TextNode(line1, TextType.TEXT)
                text_in_html = text_node_to_html_node(text_line)
                outer_html_code = ParentNode("blockquote", [text_in_html]) # [] text_in_html - needed - ParentNode expect. list
                html_nodes.append(outer_html_code) # append in for loop - multiple quotes possible.

        elif block_type == BlockType.UNORDERD_LIST:
            lines = block.split("\n")
            
            cleaned_lines = []
            for line in lines:
                cleaned_lines.append(line[2:].strip())
            
            inner_html_code = []
            for line1 in cleaned_lines:
                li_children = text_to_children(line1) ###
                inner_html_code.append(ParentNode("li", li_children))
                
            
            outer_html_code = ParentNode("ul", inner_html_code)

            html_nodes.append(outer_html_code)
        
        elif block_type == BlockType.ORDERED_LIST:
            lines = block.split("\n")
            
            cleaned_lines = []
            level = 0
            for line in lines:
                level += 1
                cleaned_lines.append(line.removeprefix(f"{level}. ").strip())
            
            inner_html_code = []
            for line1 in cleaned_lines:
                li_children = text_to_children(line1) ###
                inner_html_code.append(ParentNode("li", li_children))
            
            outer_html_code = ParentNode("ol", inner_html_code)

            html_nodes.append(outer_html_code)
        
        elif block_type == BlockType.PARAGRAPH:
            lines = block.replace("\n", " ")
            children = text_to_children(lines)
            outer_html_code = ParentNode("p", children)
            html_nodes.append(outer_html_code)
    
    return ParentNode("div", html_nodes) #Final Return!!!! div needed to close everything properl!
    
def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for node in text_nodes:
        children.append(text_node_to_html_node(node))
    return children

def extract_title(markdown):
    blocks_in_markdown = markdown_to_blocks(markdown)

    for block in blocks_in_markdown:
        block_type = block_to_block_type(block)
        if block_type == BlockType.HEADING: 
            
            if block[:2] == "# ":
                return block[2:]
    raise Exception("No header found")
