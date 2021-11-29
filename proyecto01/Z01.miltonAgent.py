import NormalAgent

NormalAgent.shared_files_path = "/DATA/code/python/comflex/proyecto01"  # shared files
agent_user = "mpalacin"  # es xmpp_user
agent_pass = "mpalacin"  # es xmpp_pass

if __name__ == "__main__":
    NormalAgent.main(agent_user, agent_pass)