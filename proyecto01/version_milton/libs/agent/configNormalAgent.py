import os
dirname = os.path.dirname(__file__)

sf_path = ""  # shared files
db_path = os.path.join(dirname, 'db_normalagent.db')
directory_agent = ""
xmpp_server = "chatterboxtown.us"
agent_user = ""  # es xmpp_user
agent_pass = ""  # es xmpp_pass

text_search = ''
ask_file_name = False
ask_file_ext = False
files_found = None
trace = False
selected_file = None

ask_cpu = False
finish_file_download = False
finish_cpu_borrow = False


def xmpp_agent():
    return agent_user + "@" + xmpp_server


def xmpp_peer(agent):
    return agent + "@" + xmpp_server


def xmpp_directory():
    return directory_agent + "@" + xmpp_server