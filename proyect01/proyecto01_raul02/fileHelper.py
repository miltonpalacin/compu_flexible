import glob
import os
from imohash import hashfile


def fileList(path):
    files = []
    for file in glob.glob(os.path.join(path, "*.*")):
        if not os.path.isdir(file):
            row = {}
            # solo los primero 128k iniciales.
            row["code"] = hashfile(file, hexdigest=True)
            row["name"], row["ext"] = os.path.splitext(os.path.basename(file))
            row["name"]
            row["size"] = os.stat(file).st_size
            files.append(row)
    return files
