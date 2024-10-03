import tarfile
import time


class Node:
    def __init__(self, name, parent=None, info=None):
        self.name = name
        self.children = []
        self.parent = parent
        self.info = info if info else dict()

    def add_child(self, child):
        self.children.append(child)

    def find_node(self, path):
        if path.startswith('/'):
            return self.get_root().find_node("/".join(path.split("/")[1:]))

        current_name = path.split("/")[0]

        if path == "":
            return self

        if current_name == "..":
            if self.parent is None:
                return None
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

    def print_tree(self, indent=0, lasts=None):
        if lasts is None:
            lasts = [True]
        string = "".join("│  " if not lasts[i] else "   " for i in range(indent))
        if lasts[-1]:
            string += "└"
        else:
            string += "├"
        string += self.name + "\n"
        for i, child in enumerate(self.children):
            string += child.print_tree(indent + 1, [*lasts, i == len(self.children) - 1])
        return string

    def get_root(self):
        return self.parent.get_root() if self.parent else self

    def get_full_path(self):
        full_path = self.name
        if self.parent:
            full_path = self.parent.get_full_path() + "/" + full_path
        return full_path

    def list_children(self):
        pass


class File(Node):
    pass


class Directory(Node):

    def list_children(self, full_format=False):
        result = ""
        for child in self.children:
            permissions = child.info.get("permissions", "N/A")
            file_type = child.info.get("file_type", "N/A")
            user = child.info.get("user", "N/A")
            group = child.info.get("group", "N/A")
            size = child.info.get("size", "N/A")
            modification_time = child.info.get("modification_time", "N/A")
            name = child.name
            result += (str(octal_to_symbolic(permissions)) + "\t")
            result += (str(file_type) + "\t")
            result += (str(user) + "\t")
            result += (str(group) + "\t")
            result += (str(size) + "\t")
            result += (str(modification_time) + "\t")
            result += (str(name) + "\n")
        return result


def octal_to_symbolic(octal_str):
    mapping = {
        '0': '---',  # нет прав
        '1': '--x',  # только execute
        '2': '-w-',  # только write
        '3': '-wx',  # write и execute
        '4': 'r--',  # только read
        '5': 'r-x',  # read и execute
        '6': 'rw-',  # read и write
        '7': 'rwx',  # read, write и execute
    }
    symbolic_mode = ''.join([mapping[digit] for digit in octal_str])
    return symbolic_mode


