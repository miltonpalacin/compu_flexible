import os
dirname = os.path.dirname(__file__)

db_path = os.path.join(dirname, 'db_directoryagent.db')
xmpp_server = "chatterboxtown.us"
agent_user = ""  # es xmpp_user
agent_pass = ""  # es xmpp_pass
cpu_req = {}


def xmpp_agent():
    return agent_user + "@" + xmpp_server


def xmpp_peer(agent):
    return agent + "@" + xmpp_server