import click
import os
import shutil
import re
import yaml

name_re = re.compile(r"[A-Z]+")
number_re = re.compile(r"^[+-]?\d+(\.\d+)?([eE][+-]?\d+)?$")
constant_usage_re = re.compile(r"\+\([A-Z]+\)")


def get_dict_from_symbol(parts, i):
    counter = 1
    dict_parts = ["{"]
    while i < len(parts) and counter != 0:
        if parts[i] == "{":
            counter += 1
        if parts[i] == "}":
            counter -= 1
        dict_parts.append(parts[i])
        i += 1

    dict_parts = dict_parts[1:]
    dict_parts = dict_parts[:len(dict_parts) - 1]

    dict_text = " ".join(dict_parts)

    return dict_text, i


class Root:
    def __init__(self, text):
        self.constants = {}
        self.dictionaries = []

        parts = text.split(" ")

        i = 0
        while i < len(parts):
            part = parts[i]
            if part == "NB.": # Комментарий
                i += 1
                while i < len(parts) and parts[i] != "|":
                    i += 1
                i += 1
            elif bool(name_re.match(part)): # Константы
                name = part

                if i + 2 >= len(parts) or parts[i + 1] != "is": # Если после константы не следует is, то это ошибка
                    click.echo(f"Ошибка чтения файла! Создана константа без значения: {name}")
                    exit(1)
                else:
                    if parts[i + 2] == "{": # Если значение константы начинается с фигурной скобки, то это словарь
                        i += 3
                        dict_text, i = get_dict_from_symbol(parts, i)
                        self.constants[name] = Dictionary(dict_text, False, self) # Словарь на верхнем уровне

                    elif bool(number_re.match(parts[i + 2])): # Если значение константы - это число, то это число :)
                        try:
                            self.constants[name] = int(parts[i + 2])
                        except Exception as e:
                            self.constants[name] = float(parts[i + 2])
                        i += 3
            elif part == "{": # На новой строке начался словарь
                i += 1
                dict_text, i = get_dict_from_symbol(parts, i)
                self.dictionaries.append(Dictionary(dict_text, True, self))  # Словарь на верхнем уровне
            else: # Ошибка
                click.echo(f"Ошибка чтения файла! Неизвестная строка: {part}")
                exit(1)

        for d in self.dictionaries:
            d.compile_constants(self.constants)

    @property
    def json(self) -> dict:
        data = {}
        for d in self.dictionaries:
            d_data = d.json
            for key in d_data:
                data[key] = d_data[key]

        return data

    def yaml(self, yaml_file):
        string = yaml.dump(self.json)
        with open(yaml_file, 'w') as f:
            f.write(string)



class Dictionary:
    def __init__(self, text, can_use_constants=False, root=None):
        self.text = text
        self.root = root
        self.can_use_constants = can_use_constants
        self.data = {}

        parts = text.split(" ")

        i = 0
        while i < len(parts):
            part = parts[i]
            if part == "NB.":  # Комментарий
                i += 1
                while i < len(parts) and parts[i] != "|":
                    i += 1
                i += 1
            elif bool(name_re.match(part)):  # Ключи
                name = part

                if i + 2 >= len(parts) or parts[i + 1] != "=>":  # Если после ключа не следует =>, то это ошибка
                    click.echo(f"Ошибка чтения файла! Создан ключ без значения: {name}")
                    exit(1)
                else:
                    if parts[i + 2] == "{":  # Если значение ключа начинается с фигурной скобки, то это словарь
                        i += 3
                        dict_text, i = get_dict_from_symbol(parts, i)
                        self.data[name] = Dictionary(dict_text, self.can_use_constants, self.root)  # Словарь на верхнем уровне

                    elif bool(number_re.match(parts[i + 2])):  # Если значение ключа - это число, то это число :)
                        try:
                            self.data[name] = int(parts[i + 2])
                        except Exception as e:
                            self.data[name] = float(parts[i + 2])
                        i += 3
                    elif bool(constant_usage_re.match(parts[i + 2])): # Если значение ключа - это константа
                        self.data[name] = Constant(parts[i + 2])
                        i += 3
                    else:
                        click.echo(f"Ошибка чтения файла! Неверный токен: {parts[i + 2]}")
                        exit(1)
            else:  # Ошибка
                click.echo(f"Ошибка чтения файла! Неизвестная строка: {part}")
                exit(1)

    def compile_constants(self, constants):
        for key in self.data:
            if isinstance(self.data[key], Constant):
                self.data[key] = constants[self.data[key].name]
            if isinstance(self.data[key], Dictionary):
                self.data[key].compile_constants(constants)

    @property
    def json(self) -> dict:
        data = {}
        for key in self.data:
            if isinstance(self.data[key], Dictionary):
                data[key] = self.data[key].json
            else:
                data[key] = self.data[key]
        return data


class Constant:
    def __init__(self, name):
        self.name = name.replace("+(", "").replace(")", "")


@click.command()
@click.argument('source_file', type=click.Path(exists=True), required=True)
@click.argument('destination_file', type=click.Path(), required=True)
def convert(source_file, destination_file):
    """
    Конвертирует SOURCE_FILE в DESTINATION_FILE.
    """
    # Проверка на существование исходного файла
    if not os.path.isfile(source_file):
        click.echo(f"Ошибка: Файл '{source_file}' не существует.")
        return

    try:
        with open(source_file) as f:
            full_text = ""
            for string in f.readlines():
                if string.startswith("NB."):
                    string += " | "
                full_text += string + "\n"
            full_text = full_text.replace("\n", " ")
            full_text = full_text.replace("\r", " ")
            full_text = full_text.replace("\t", " ")
            full_text = full_text.replace("=>", " => ")
            full_text = full_text.replace("}", " } ")
            full_text = full_text.replace("{", " { ")
            full_text = full_text.replace(")", ") ")
            full_text = full_text.replace("+(", " +(")

            while "  " in full_text:
                full_text = full_text.replace("  ", " ")

            full_text = full_text.rstrip()
            full_text = full_text.lstrip()

            root = Root(full_text)
            root.yaml(destination_file)
    except Exception as e:
        click.echo(f"Ошибка при конвертации файла: {e}")

if __name__ == "__main__":
    convert()
