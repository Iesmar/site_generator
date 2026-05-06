import os, shutil

from textnode import TextNode

def main():
    # first check if path exist - yes->Delete - No->Create
    if os.path.exists("./public"):
        print("cleaned up old files!")
        shutil.rmtree("./public")
    if not os.path.exists("./public"):
        print("created new empty work folder (./public).")
        os.mkdir("./public")
    path = ""
    copy_files(path)


def copy_files(path):
        files_to_copy = os.listdir(f"./static/{path}")
        print("\nThese files need to be coppied!")
        print(files_to_copy)
        for item in files_to_copy:
            if files_to_copy == []:
                print("empty folder")
                break
            if os.path.isfile(f"./static/{path}{item}"):
                copy_this_to(item, path)    
            if os.path.isfile(f"./static/{path}{item}") == False:
                path += f"{item}/"
                os.mkdir(f"./public/{path}")
                print(f"created dir ./public/{path}")
                print(f"moving into dir ./static/{path}")
                copy_files(path)
                

def copy_this_to(file, path):
    shutil.copy(f"./static/{path}{file}", f"./public/{path}")
    print(f"{file} successfully coppied to ./public/{path}")


if __name__ == "__main__":
    main()
