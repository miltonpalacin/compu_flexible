import NormalAgent

NormalAgent.shared_files_path = "/DATA/maestria/12.CloudFlexible/Material"  # shared files
agent_user = "rarias"  # es xmpp_user
agent_pass = "rarias"  # es xmpp_pass

if __name__ == "__main__":
    NormalAgent.main(agent_user, agent_pass)