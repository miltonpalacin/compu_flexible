# sf_path = "/DATA/temp/others"  # shared files
sf_path = "/DATA/code/python/comflex/proyecto01/"  # shared files
db_path = "db_normalagent.db"  # data base
directory_agent = "directory_agent"
xmpp_server = "chatterboxtown.us"
agent_user = "rarias"  # es xmpp_user
agent_pass = "rarias"  # es xmpp_pass

# agent_user = "mpalacin"  # es xmpp_user
# agent_pass = "mpalacin"  # es xmpp_pass

text_search = ''
ask_file_name = False
ask_file_ext = False
files_found = None
trace = False


def xmpp_agent():
    return agent_user + "@" + xmpp_server


def xmpp_directory():
    return directory_agent + "@" + xmpp_server