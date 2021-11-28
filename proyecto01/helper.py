def sanitize_sender_name(sender_name):
    #parts = sender_name.split('/')
    parts = sender_name.split('@')
    return parts[0]


def check_file_name(file_name: str) -> bool:
    if file_name is None:
        return False

    if len(file_name) < 3:
        return False

    # if "." not in file_name:
    #     return False

#     parts = file_name.split(".")

#     if len(parts) > 2:
#         return False

#     if len(parts[0]) < 1 or len(parts[1]) < 1:
#         return False

    return True


def check_file_ext(file_ext: str) -> bool:
    if file_ext is None:
        return False

    if len(file_ext) < 6 and len(file_ext) > 2:
        return False

    if "." in file_ext:
        return False

    return True