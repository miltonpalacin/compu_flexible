import os
dirname = os.path.dirname(__file__)

db_path = os.path.join(dirname, 'db_directoryagent.db')
xmpp_server = "chatterboxtown.us"
agent_user = ""  # es xmpp_user
agent_pass = ""  # es xmpp_pass


def xmpp_agent():
    return agent_user + "@" + xmpp_server