import xml.etree.ElementTree as ET

def read_config(file_path):
    # Парсим XML-файл
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Извлекаем значения из XML по тегам
    visualization_program_path = root.find('visualizationProgramPath').text
    repository_path = root.find('repositoryPath').text
    result_code_file_path = root.find('resultCodeFilePath').text

    # Возвращаем словарь с данными
    return {
        "visualization_program_path": visualization_program_path,
        "repository_path": repository_path,
        "result_code_file_path": result_code_file_path
    }


# Пример использования
config = read_config("config.xml")
print("Путь к анализируемому репозиторию:", config["repository_path"])
print("Путь к файлу-результату в виде кода:", config["result_code_file_path"])

import git
import os
from graphviz import Digraph


def list_files_for_commit(repo_path):
    """
    Получаем список файлов и папок для указанного коммита.
    """
    repo = git.Repo(repo_path)
    sha = repo.rev_parse('origin/main')
    commit = repo.commit(sha)

    files = []

    for item in commit.tree.traverse():
        files.append(item.path)

    return files


def create_graph_for_commit(files):
    """
    Создаем граф с помощью Graphviz, где узлы - это папки и файлы.
    """
    dot = Digraph(comment='Files and Directories Graph')
    added_nodes = set()

    for file_path in files:
        path_parts = file_path.split("/")

        for i in range(0, len(path_parts)):
            parent = os.sep.join(path_parts[:i])
            child = os.sep.join(path_parts[:i + 1])
            if parent not in added_nodes:
                dot.node(parent, label=os.path.basename(parent) if os.path.basename(parent) != '' else "Repository")
                added_nodes.add(parent)
            if child not in added_nodes:
                dot.edge(parent, child)
                dot.node(child, label=os.path.basename(child))
                added_nodes.add(child)

    return dot


def visualize_graph(dot, graph_file):
    """
    Визуализируем граф с помощью graphviz.
    """
    dot.render(graph_file.split(".")[0], format='png', cleanup=True)
    with open(graph_file, "w") as f:
        f.write(dot.source)
    print(dot.source)


repo_path = config["repository_path"]

files = list_files_for_commit(repo_path)
dot = create_graph_for_commit(files)
visualize_graph(dot, config["result_code_file_path"])

