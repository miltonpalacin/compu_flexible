def sanitize_sender_name(sender_name):
    #parts = sender_name.split('/')
    parts = sender_name.split('@')
    return parts[0]


def check_file_name(file_name: str) -> bool:
    if file_name is None:
        return False

    if len(file_name) < 2:
        return False

    return True


def check_file_ext(file_ext: str) -> bool:
    if file_ext is None:
        return False

    if len(file_ext) > 5 and len(file_ext) == 0:
        return False

    if "." in file_ext:
        return False

    return True


def check_file_path(my_path):
    if my_path is None:
        return False

    if len(my_path) < 3:
        return False

    return True