from FileTree import Directory, File
import tarfile
import time
import os


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


def build_tree(path_to_archive, username):
    system_name = os.path.basename(path_to_archive)
    file_tree = Directory(system_name)
    tar_path = path_to_archive
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
                    'user': username,
                    'group': username,
                    'size': member.size,
                    'file_type': get_file_type_number(member)
                }

                parent_node = file_tree.find_node(path)
                if parent_node is not None:
                    parent_node.add_child(
                        File(name, parent_node, info) if member.isfile() else Directory(name, parent_node, info),
                    )
    file_tree.name = "/"
    return file_tree