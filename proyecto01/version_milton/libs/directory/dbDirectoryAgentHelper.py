import sqlite3
from sqlite3 import Error
from libs.directory import configDirectoryAgent as config


sql_activate_user = "UPDATE user " + \
                "SET state = 's' " + \
                "WHERE agent = ?"

sql_agents = "SELECT agent " + \
            "FROM user " + \
            "WHERE agent <> ?"

sql_create_user = "INSERT INTO user " + \
               "(agent, state) " + \
               "VALUES (?, 's')"

sql_select_user = "SELECT agent FROM user " + \
               "WHERE agent = ?"


sql_insert_file = "INSERT INTO files_directory " + \
              "(code, agent, name, ext, size, owner) " + \
              "VALUES (?, ?, ?, ?, ?, ?)"

sql_delete_file = "DELETE FROM files_directory " + \
                  "WHERE code = ? and agent = ?"

sql_delete_all = "DELETE FROM files_directory WHERE agent = ?"


sql_select_name_search = "SELECT code, agent, name, ext, size " + \
                         "FROM files_directory " + \
                         "WHERE UPPER(name) LIKE UPPER('%'||?||'%') " + \
                         "AND agent != ?"

sql_select_ext_search = "SELECT code, agent, name, ext, size " + \
                        "FROM files_directory " + \
                        "WHERE UPPER(ext) LIKE UPPER('%'||?||'%') " + \
                        "AND agent != ?"


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

    try:
        con = sqlite3.connect(config.db_path)
        cur = con.cursor()

        cur.execute(sql_delete_all, (agent,))
        for file in files:
            cur.execute(sql_insert_file, (file["code"], agent,
                        file["name"], file["ext"],
                        file["size"], file["owner"]))

        con.commit()

        return True
    except Error:
        raise
    finally:
        con.close()

    return False


def search_for_file(agent, search_arr):
    files_found = []
    try:
        con = sqlite3.connect(config.db_path)
        cur = con.cursor()

        search = search_arr[0]
        by_ext = search_arr[1]

        if by_ext:
            cur.execute(sql_select_ext_search, (search, agent))
        else:
            cur.execute(sql_select_name_search, (search, agent))

        rows = cur.fetchall()
        for row in rows:
            new_row = {}
            new_row["code"] = row[0]
            new_row["agent"] = row[1]
            new_row["name"] = row[2]
            new_row["ext"] = row[3]
            new_row["size"] = row[4]
            files_found.append(new_row)

        con.commit()

    except Error:
        raise
    finally:
        con.close()

    return files_found


def get_users(agent):
    agents_found = []
    try:
        con = sqlite3.connect(config.db_path)
        cur = con.cursor()

        cur.execute(sql_agents, (agent, ))
        rows = cur.fetchall()

        for row in rows:
            new_row = {}
            new_row["agent"] = row[0]
            agents_found.append(new_row)

        con.commit()

    except Error:
        raise
    finally:
        con.close()

    return agents_found