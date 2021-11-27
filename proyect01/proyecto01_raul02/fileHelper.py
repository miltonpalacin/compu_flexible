import glob
import os
from imohash import hashfile


def file_list(agent, path):
    files = []
    for file in glob.glob(os.path.join(path, "*.*")):
        if not os.path.isdir(file):
            row = {}
            # solo los primero 128k iniciales.
            row["code"] = hashfile(file, hexdigest=True)
            row["agent"] = agent
            row["path"] = file
            row["name"], row["ext"] = os.path.splitext(os.path.basename(file))
            row["ext"] = row["ext"][1:]
            row["size"] = os.stat(file).st_size
            files.append(row)
    return files


def file_attr(agent, path):
    files = glob.glob(path)
    row = {}
    if len(files) > 0:
        file = files[0]
        if not os.path.isdir(file):
            # solo los primero 128k iniciales.
            row["code"] = hashfile(file, hexdigest=True)
            row["agent"] = agent
            row["path"] = file
            row["name"], row["ext"] = os.path.splitext(os.path.basename(file))
            row["ext"] = row["ext"][1:]
            row["size"] = os.stat(file).st_size
    return row
