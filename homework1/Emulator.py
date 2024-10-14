from build_tree import build_tree
import os
import csv
from datetime import datetime
from FileTree import Directory, File


def parse_command(command):
    parts = command.split()
    command = parts[0]
    args = dict()
    i = 1
    unnamed_args = 0
    while i < len(parts):
        if parts[i].startswith("-"):
            arg = parts[i].lstrip("-")

            args[arg] = True
            if i < len(parts) - 1:
                arg_value = parts[i + 1]
                if arg_value.startswith("-"):
                    pass
                elif arg_value.startswith("\""):
                    arg_value = ""
                    i += 1
                    while i < len(parts) and not parts[i].endswith("\""):
                        arg_value += parts[i] + " "
                        i += 1

                    arg_value += parts[i]
                    arg_value = arg_value.replace("\"", "")

                args[arg] = arg_value
        else:
            args[str(unnamed_args)] = parts[i]
            unnamed_args += 1
        i += 1
    return command, args


def print_table(items, columns=3, column_width=20):
    rows = (len(items) + columns - 1) // columns  # Вычисляем количество строк
    for row in range(rows):
        for col in range(columns):
            idx = row + col * rows
            if idx < len(items):
                print(f"{items[idx]:<{column_width}}", end=" ")  # Выводим элемент с отступом
        print()  # Переход на новую строку


class Emulator:
    def __init__(self, username, path_to_tar, path_to_logs):
        self.username = username
        self.path_to_tar = path_to_tar
        self.path_to_logs = path_to_logs

        os.makedirs(os.path.dirname(self.path_to_logs), exist_ok=True)
        with open(self.path_to_logs, "w") as file:
            writer = csv.DictWriter(file, fieldnames=["user", "folder", "cmd", "result"], delimiter=',')
            writer.writeheader()

        self.file_tree = build_tree(
            self.path_to_tar,
            self.username,
        )
        self.current_node = self.file_tree
        self.alive = True

    def log(self, user, folder, cmd, result):
        with open(self.path_to_logs, "a") as file:
            writer = csv.writer(file, delimiter=",")
            writer.writerow([user, folder, cmd, result])

    def run_emulator(self):
        while self.alive:
            cur_path = self.current_node.name
            enter_text = self.username + "@" + self.username + ":" + cur_path + "$ "
            command_text = input(enter_text)
            self.run_command(command_text)

    def run_cd(self, args):
        result = ""
        finding_node = args.get("0", None)
        if finding_node is None:
            self.current_node = self.file_tree
        else:
            new_node = self.current_node.find_node(finding_node)
            if new_node is None:
                result += "cd: no such file or directory: " + finding_node
                print(result)
            elif not isinstance(new_node, Directory):
                result += "cd: not a directory: " + finding_node
                print(result)
            else:
                self.current_node = new_node
        return result

    def run_exit(self, _):
        self.alive = False

    def run_ls(self, args):
        node = self.current_node
        if args.get("0", None):
            path = args.get("0", None)
            if node.find_node(path) is not None:
                node = node.find_node(path)
        if args.get("l", None):
            result = node.list_children()
            print(result, end="")
            return result.replace("\n", "<br>")
        else:
            elements = [row.name for row in node.children]
            print_table(elements)

            return " ".join(elements)

    def run_who(self, args):
        result = ""
        if 'a' in args:

            name = self.username
            line = "console"
            time = datetime.now().strftime("%Y-%m-%d %H:%M")
            idle = '00:00'
            pid = '0000'

            result += f"{name:<10} {line:<10} {time:<20} {idle:<10} {pid:<10}"

        # Если аргумент -a не передан, выводим сокращённую информацию
        else:

            name = self.username
            line = "console"
            time = datetime.now().strftime("%Y-%m-%d %H:%M")

            result += f"{name:<10} {line:<10} {time:<20}"
        print(result)
        return result

    def run_tree(self, args):
        result = self.current_node.print_tree()
        print(result)
        return result.replace("\n", "<br>")

    def run_command(self, command_text):
        command, args = parse_command(command_text)
        from_folder = self.current_node.get_full_path()
        result = ""
        if command == "cd":
            result = self.run_cd(args)
        elif command == "ls":
            result = self.run_ls(args)
        elif command == "who":
            result = self.run_who(args)
        elif command == "tree":
            result = self.run_tree(args)
        elif command == "exit":
            result = self.run_exit(args)

        self.log(self.username, from_folder, command_text, result)