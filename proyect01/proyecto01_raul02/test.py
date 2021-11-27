import fileHelper
import dbHelper
import configNormalAgent as config
import hashlib
import base64
from ast import literal_eval




# dbHelper.save_initial_files(config.db_path, files)




arr = [{"q": 1, "w": "qw"}, {"q": 2, "w": "er"}]
# print(str(arr))
# print(hashlib.md5(str(arr)))


def hashFor(data):
    # Prepare the project id hash
    hashId = hashlib.md5()
    print(repr(data))
    hashId.update(repr(data).encode('utf-8'))

    return hashId.hexdigest()


def encode(data):
    msg = repr(data)
    print(msg)
    print("-"*100)
    msg = msg.encode('utf-8')
    print(msg)
    print("-"*100)
    msg = base64.b64encode(msg)
    print(msg)
    print("-"*100)
    return msg


def decode(msg):
    data = base64.b64decode(msg)
    print(data)
    print("-"*100)
    data = data.decode('utf-8')
    print(data)
    print("-"*100)
    return literal_eval(data)


data1 = ['abc', 'de']
data2 = ['a', 'bcde']
print(hashFor(data1) + ':', data1)
print(hashFor(data2) + ':', data2)

# s = "['a',['b','c','d'],'e']"
s = '[{"q": 1, "w": "qw"}, {"q": 2.23, "w": "er"}]'
print(literal_eval(s))

files = fileHelper.file_list(config.agent_user, config.sf_path)
# files.append({'code': '{{aá', 'path': 'b@·~', 'name': '&%$', 'ext': '.', 'size': 23212.23})
for file in files:
    print(file)

msg = encode(files)
print(msg)
arr = decode(msg)
arr.append({'code': 'a', 'path': 'b', 'name': 'c', 'ext': 'd', 'size': 12.23})
print(arr)
