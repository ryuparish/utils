# R: This creates a json object that has the document given as the "text" and the website link given as "metadata"


# Also, remember to add alias add="<Path to this program>" to .bash_profile or .bashrc
import json
from sys import argv
def main():
    if(len(argv) != 3):
        print("Usage: add <document> <website link>")
        exit(1)
    entry = {}
    # document
    entry["text"] = argv[1]
    # website link
    entry["metadata"] = argv[2]
    entry = json.dumps(entry)

    # R: You must hard code the filename here
    with open("cledge_doc1.txt", "a+") as file_object:
        file_object.seek(0)
        data = file_object.read(100)
        if(len(data) > 0):
            file_object.write("\n")
        file_object.write(entry)

if __name__ == "__main__":
    main()
