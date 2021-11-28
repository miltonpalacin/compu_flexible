from os import listdir, mkdir, path
from os.path import isfile, join


def get_files_list(folder_path: str):
    only_files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
    my_file_list = ','.join(only_files)
    return my_file_list


def check_shared_dir(shared_files_path):
    if path.exists(shared_files_path):
        return

    mkdir(shared_files_path)
    f = open(shared_files_path + "/file_1.txt", "a")
    f.write("file 1 for test")
    f.close()
    f = open(shared_files_path + "/file_2.txt", "a")
    f.write("file 2 for test")
    f.close()


