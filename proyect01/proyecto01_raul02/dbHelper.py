import sqlite3
from sqlite3 import Error
import fileHelper


# def open(db_path):
#     try:
#         con = sqlite3.connect(path)
#     except Error:
#         raise
#     finally:
#         con.close()
#     return con

select_by_code = "SELECT code, owner, public FROM shared_file where code = ?"
select_all = "SELECT code FROM shared_file"
insert_file = "INSERT INTO shared_file " + \
              "(code, agent, name, path, ext, size, owner, public) " + \
              "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"


def save_initial_files(db_path, files):
    final_array = []
    try:
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute(select_all)
        rows = cur.fetchall()

        del_files = []
        upd_files = []
        for row in rows:
            # Verificar para actualizar
            code = row[0]
            delete = True
            for index, file in enumerate(files):
                if file["code"] == code:
                    upd_row = fileHelper.file_attr(file["agent"], file["path"])
                    upd_row["owner"] = row[1]
                    upd_row["public"] = row[1]
                    upd_files.append(upd_row)
                    del files[index]
                    delete = False
                    break
            # Verificar par eliminar
            if delete:
                del_row = {}
                del_row["code"] = code
                del_row["agent"] = ""
                del_row["path"] = ""
                del_row["name"] = ""
                del_row["ext"] = ""
                del_row["size"] = 0
                del_row["cru"] = "r"  # remove
                del_files.append(del_row)

        # Insertar registro
        for file in files:
            cur.execute(insert_file, (file["code"], file["agent"],
                        file["name"], file["path"], file["ext"],
                        file["size"], "s", "n"))
            con.commit()
            final_array.append(file)

        # Actualizar registro
        for file in files:
            cur.execute(update_file, (file["code"], file["name"],
                                      file["ext"], file["size"], 
                                      file["owner"]"s", "n"))
            con.commit()
            final_array.append(file)

    except Error:
        raise
    finally:
        con.close()

    return final_array
