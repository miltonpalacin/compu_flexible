from os import listdir, mkdir, path
from os.path import isfile, join


def get_files_list(folder_path: str) -> str:
    only_files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
    my_file_list = ','.join(only_files)
    return my_file_list


def check_shared_dir(shared_files_path: str):
    if path.exists(shared_files_path):
        return

    # create two simple files
    mkdir(shared_files_path)
    f = open(shared_files_path + "/file_1.txt", "a")
    f.write("file 1 for test")
    f.close()
    f = open(shared_files_path + "/file_2.txt", "a")
    f.write("file 2 for test")
    f.close()


def sanitize_sender_name(sender_name):
    parts = sender_name.split('/')
    return parts[0]


def check_file_name(file_name: str) -> bool:
    if file_name is None:
        return False

    if len(file_name) < 3:
        return False

    if "." not in file_name:
        return False

    parts = file_name.split(".")

    if len(parts) > 2:
        return False

    if len(parts[0]) < 1 or len(parts[1]) < 1:
        return False

    return True



