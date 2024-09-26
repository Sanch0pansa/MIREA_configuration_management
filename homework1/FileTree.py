import os
import tarfile
from collections import defaultdict

from debugpy.common.timestamp import current


class Node:
    def __init__(self, name):
        self.name = name
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def find_node(self, path):
        current_name = path.split("/")[0]
        if self.name != current_name:
            return None
        if self.name == path:
            return self
        for child in self.children:
            res = child.find_node("/".join(path.split("/")[1:]))
            if res:
                return res
        return None

    def print_tree(self, indent=0):
        """Рекурсивно выводим дерево"""
        print('\t' * indent + self.name)
        for child in self.children:
            child.print_tree(indent + 1)



class File(Node):
    pass


class Directory(Node):
    pass

file_tree = Node("system")
tar_path = "system2.tar"
with tarfile.open(tar_path, 'r') as tar_ref:
    for member in tar_ref.getmembers():
        # Пропускаем корневую директорию, если она есть
        if "/" in member.name:
            path = "/".join(member.name.split("/")[:-1])
            name = member.name.split("/")[-1]

            parent_node = file_tree.find_node(path)
            if parent_node is not None:
                parent_node.add_child(
                    File(name) if member.isfile() else Directory(name)
                )

file_tree.print_tree()
