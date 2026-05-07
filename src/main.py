import os, shutil, sys

from htmlblocks import markdown_to_html_node, extract_title
from textnode import TextNode


def main():

    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    else:
        basepath = "/"

    # first check if path exist - yes->Delete - No->Create
    
    path = ""
    root_content_path = "./content/"
    root_template = "./template.html"
    root_public = "./docs/"
    root_static = "./static/"

    if os.path.exists(root_public):
        print("cleaned up old files!")
        shutil.rmtree(root_public)
    if not os.path.exists(root_public):
        print(f"created new empty work folder {root_public}")
        os.mkdir(root_public)

    generate_website(root_content_path, root_template, root_public, basepath)
    copy_files(path, root_static, root_public)

    #generate_page("./content/index.md","./template.html","./public/index.html")

    
def generate_website(content_root, template_root, dest_root, basepath):

    print(f"I AM IN THE FOLLOWING {content_root}")
    files_to_convert = os.listdir(f"{content_root}")
    print("\n\nThese files need to be converted/coppied!")
    print(files_to_convert)
    for item in files_to_convert:
            new_content_root = f"{content_root}{item}"
            new_dest_root = f"{dest_root}{item}/"
            #if files_to_convert == []:
                #print("empty folder!!!!!")
                #break
            if os.path.isfile(f"{content_root}{item}"):
                generate_page(f"{content_root}{item}", template_root, f"{dest_root}{str(item)[:-3]}.html", basepath)
                print(f"converted {content_root}{item} into {dest_root}{str(item)[:-3]}.html")    
            elif os.path.isfile(f"{new_content_root}") == False:
                #content_root += f"{item}/"
                #dest_root += f"{item}/"
                os.makedirs(f"{new_dest_root}", exist_ok=True)
                #print(f"created dir {dest_root}") 
                #print(f"moving into dir {content_root}")
                generate_website(f"{new_content_root}/", template_root, new_dest_root, basepath)

def generate_page(from_path, template_path, dest_path, basepath):
    print(f"\nGenerating page from {from_path}\nto {dest_path} using {template_path}\n")
    
    with open(from_path) as f:
        markdown = f.read()
    with open(template_path) as f:
        template = f.read()
    
    html_nodes = markdown_to_html_node(markdown)
    html_page = html_nodes.to_html()

    title = extract_title(markdown)

    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", html_page)
    template = template.replace('href="/', f'href="{basepath}')
    final_page = template.replace('src="/', f'src="{basepath}')


    with open(f"{dest_path}", "w") as f:
        f.write(final_page)

def copy_files(path, root_static, root_public):
        files_to_copy = os.listdir(f"{root_static}{path}")
        print("\nThese files need to be coppied!")
        print(files_to_copy)
        for item in files_to_copy:
            if files_to_copy == []:
                print("empty folder")
                break
            if os.path.isfile(f"{root_static}{path}{item}"):
                shutil.copy(f"{root_static}{path}{item}", f"{root_public}{path}")
                print(f"{root_static}{path}{item} successfully coppied to {root_public}{path}")
            if os.path.isfile(f"{root_static}{path}{item}") == False:
                path += f"{item}/"
                os.mkdir(f"{root_public}{path}")
                print(f"created dir {root_public}{path}")
                print(f"moving into dir {root_static}{path}")
                copy_files(path, root_static, root_public)
    


if __name__ == "__main__":
    main()
