import sqlite3
from sqlite3 import Error
import configDirectoryAgent as config


sql_activate_user = "UPDATE user " + \
                "SET state = 's' " + \
                "WHERE agent = ?"

sql_create_user = "INSERT INTO user " + \
               "(agent, state) " + \
               "VALUES (?, 's')"

sql_select_user = "SELECT agent FROM user " + \
               "WHERE agent = ?"


sql_insert_file = "INSERT INTO files_directory " + \
              "(code, agent, name, ext, size, owner) " + \
              "VALUES (?, ?, ?, ?, ?, ?)"

sql_update_file = "UPDATE files_directory " + \
              "SET name = ?, ext = ?, size = ?, owner = ?" + \
              "WHERE code = ? and agent = ?"

sql_delete_file = "DELETE FROM files_directory " + \
                  "WHERE code = ? and agent = ?"

sql_delete_all = "DELETE FROM files_directory"


def activate_agent(agent):
    try:
        con = sqlite3.connect(config.db_path)
        cur = con.cursor()

        cur.execute(sql_select_user, (agent, ))
        if not cur.fetchone():
            cur.execute(sql_create_user, (agent, ))
        else:
            cur.execute(sql_activate_user, (agent, ))

        con.commit()

    except Error:
        raise
    finally:
        con.close()


def save_files_directory(agent, files):
    public_array = []
    try:
        con = sqlite3.connect(config.db_path)
        cur = con.cursor()

        if len(files) > 0:
            if files[0] == "delete_all":
                cur.execute(sql_delete_all)
            else:
                for file in files:
                    if file["cru"] == "c":
                        cur.execute(sql_insert_file, (file["code"], agent,
                                    file["name"], file["ext"],
                                    file["size"], file["owner"]))
                        public_array.append(file)
                    elif file["cru"] == "u":
                        cur.execute(sql_update_file, (file["name"], file["ext"],
                                                      file["size"], file["owner"],
                                                      file["code"], agent))
                    elif file["cru"] == "r":
                        cur.execute(sql_delete_file, (file["code"], agent))

        con.commit()

    except Error:
        raise
    finally:
        con.close()

    return public_array