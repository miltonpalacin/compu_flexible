import sqlite3
from sqlite3 import Error
from libs.agent import fileHelper
from libs.agent import configNormalAgent as config

sql_select_all = "SELECT code, agent, name, path, ext, " + \
                 "size, owner FROM share_file " + \
                 "WHERE agent=?"

sql_insert_file = "INSERT INTO share_file " + \
              "(code, agent, name, path, ext, size, owner) " + \
              "VALUES (?, ?, ?, ?, ?, ?, ?)"

sql_update_file = "UPDATE share_file " + \
              "SET name = ?, ext = ?, size = ? " + \
              "WHERE code = ? and agent = ?"

sql_delete_file = "DELETE FROM share_file " + \
              "WHERE code = ? and agent = ?"

sql_public_file = "UPDATE share_file " + \
              "SET public = 's' " + \
              "WHERE code = ? and agent = ?"


def save_initial_agent_files(files):
    public_array = []
    try:

        con = sqlite3.connect(config.db_path)
        cur = con.cursor()
        cur.execute(sql_select_all, (config.agent_user, ))
        rows = cur.fetchall()

        if len(rows) == 0 and len(files) == 0:
            public_array = ["delete_all"]
        else:
            del_files = []
            upd_files = []
            for row in rows:
                # Verificar para actualizar
                code = row[0]
                delete = True
                for index, file in enumerate(files):
                    if file["code"] == code:
                        upd_row = file

                        #public = row[7]
                        #upd = False if public == "s" else True
                        if file["name"] != row[2] or file["ext"] != row[4] \
                           or file["size"] != row[5]:
                            upd_row = fileHelper.agent_file_attr(file["agent"], file["path"])
                            upd_files.append(upd_row)
                            #upd = True
                        #if upd:

                        #upd_row["cru"] = "c"
                        upd_row["owner"] = row[6]
                        public_array.append(upd_row)

                        del files[index]
                        delete = False
                        break
                # Verificar para eliminar
                if delete:
                    del_files.append(code)
                    # if row[6] == "s":
                    #     del_row = fileHelper.agent_empty_attr()
                    #     del_row["code"] = code
                    #     del_row["cru"] = "r"
                    #     del_row["owner"] = ""
                    #     public_array.append(del_row)

            # Insertar registro
            for file in files:
                cur.execute(sql_insert_file, (file["code"], file["agent"],
                            file["name"], file["path"], file["ext"],
                            file["size"], "s"))
                #file["cru"] = "c"
                file["owner"] = "s"
                public_array.append(file)

            # Actualizar registro
            for file in upd_files:
                cur.execute(sql_update_file, (file["name"], file["ext"],
                                              file["size"], file["code"],
                                              config.agent_user))

            for code in del_files:
                cur.execute(sql_delete_file, (code, config.agent_user))

        con.commit()

    except Error:
        raise
    finally:
        con.close()

    return public_array


# def confirm_agent_pub(files):
#     try:
#         con = sqlite3.connect(config.db_path)
#         cur = con.cursor()

#         for file in files:
#             cur.execute(sql_public_file, (file["code"], config.agent_user))
#         con.commit()

#     except Error:
#         raise
#     finally:
#         con.close()
