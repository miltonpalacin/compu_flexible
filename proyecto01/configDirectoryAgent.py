db_path = "db_directoryagent.db"  # data base
xmpp_server = "chatterboxtown.us"
agent_user = "directory_agent"  # es xmpp_user
agent_pass = "directory_agent"  # es xmpp_pass


def xmpp_agent():
    return agent_user + "@" + xmpp_server