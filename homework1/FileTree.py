import tarfile

from debugpy.common.timestamp import current


class Node:
    def __init__(self, name, parent=None):
        self.name = name
        self.children = []
        self.parent = parent

    def add_child(self, child):
        self.children.append(child)

    def find_node(self, path):
        current_name = path.split("/")[0]

        if path == "":
            return self

        if current_name == "..":
            return self.parent.find_node("/".join(path.split("/")[1:]))

        if current_name == ".":
            if path == ".":
                return self
            else:
                return self.find_node("/".join(path.split("/")[1:]))

        for child in self.children:
            if child.name == path:
                return child
            if child.name == current_name:
                return child.find_node("/".join(path.split("/")[1:]))
        return None

    def print_tree(self, indent=0):
        print('\t' * indent + self.name)
        for child in self.children:
            child.print_tree(indent + 1)

    def get_root(self):
        return self.parent.get_root() if self.parent else self

    def get_full_path(self):
        full_path = self.name
        if self.parent:
            full_path = self.parent.get_full_path() + "/" + full_path
        return full_path


class File(Node):
    pass


class Directory(Node):
    def print_tree(self, indent=0):
        print('\t' * indent + self.name + "/")
        for child in self.children:
            child.print_tree(indent + 1)

file_tree = Directory("system")
tar_path = "system2.tar"
with tarfile.open(tar_path, 'r') as tar_ref:
    for member in tar_ref.getmembers():
        # Пропускаем корневую директорию, если она есть
        if "/" in member.name:
            path = "/".join(member.name.split("/")[1:-1])
            name = member.name.split("/")[-1]

            parent_node = file_tree.find_node(path)
            if parent_node is not None:
                parent_node.add_child(
                    File(name, parent_node) if member.isfile() else Directory(name, parent_node),
                )

file_tree.print_tree()
cur = file_tree
while True:

    cd = input(f"[{cur.get_full_path()}] $")
    res = cur.find_node(cd)
    if res:
        cur = res