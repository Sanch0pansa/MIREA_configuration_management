import tarfile
import time

from debugpy.common.timestamp import current


class Node:
    def __init__(self, name, parent=None, info=None):
        self.name = name
        self.children = []
        self.parent = parent
        self.info = info if info else dict()

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

    def list_children(self):
        pass


class File(Node):
    pass


class Directory(Node):
    def print_tree(self, indent=0):
        print('\t' * indent + self.name + "/")
        for child in self.children:
            child.print_tree(indent + 1)

    def list_children(self, full_format=False):
        for child in self.children:
            permissions = child.info.get("permissions", "N/A")
            file_type = child.info.get("file_type", "N/A")
            user = child.info.get("user", "N/A")
            group = child.info.get("group", "N/A")
            size = child.info.get("size", "N/A")
            modification_time = child.info.get("modification_time", "N/A")
            name = child.name
            print(octal_to_symbolic(permissions), end="\t")
            print(file_type, end="\t")
            print(user, end="\t")
            print(group, end="\t")
            print(size, end="\t")
            print(modification_time, end="\t")
            print(name)


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


def get_file_type_number(member):
    if member.isdir():
        return 1  # directory
    elif member.isfile():
        return 2  # file
    elif member.issym():
        return 3  # symlink
    elif member.islnk():
        return 4  # hardlink
    elif member.ischr():
        return 5  # character device
    elif member.isblk():
        return 6  # block device
    elif member.isfifo():
        return 7  # FIFO
    elif member.issock():
        return 8  # socket
    else:
        return 0  # unknown

file_tree = Directory("system")
tar_path = "system2.tar"
with tarfile.open(tar_path, 'r') as tar_ref:
    for member in tar_ref.getmembers():
        # Пропускаем корневую директорию, если она есть
        if "/" in member.name:
            path = "/".join(member.name.split("/")[1:-1])
            name = member.name.split("/")[-1]

            mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(member.mtime))
            permissions = oct(member.mode)[-3:]  # Права в восьмеричном формате (например, '755')

            info = {
                'permissions': permissions,
                'modification_time': mod_time,
                'user': 'sanchopansa',
                'size': member.size,
                'file_type': get_file_type_number(member)
            }

            parent_node = file_tree.find_node(path)
            if parent_node is not None:
                parent_node.add_child(
                    File(name, parent_node, info) if member.isfile() else Directory(name, parent_node, info),
                )

file_tree.print_tree()
cur = file_tree
while True:

    cd = input(f"[{cur.get_full_path()}] $")
    if cd == "ls":
        cur.list_children()
    res = cur.find_node(cd)
    if res:
        cur = res