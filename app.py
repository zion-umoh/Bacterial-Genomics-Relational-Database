import os

def getOrganismFiles():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_dir = os.path.join(base_dir, "input_files")
    return [
        f for f in os.listdir(input_dir)
        if not f.startswith(".") and os.path.isfile(os.path.join(input_dir, f))
    ]


def generate_sql():
    files = getOrganismFiles()
    for f in files:
        print(f)
    #TODO: Add your code



if __name__ == "__main__":
    generate_sql()

