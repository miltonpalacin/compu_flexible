import normalAgent
from libs.agent import configNormalAgent as config

config.sf_path = "/DATA/code/python/comflex/proyecto01"  # shared files
config.directory_agent = "directory_agent"
config.agent_user = "mpalacin"  # es xmpp_user
config.agent_pass = "mpalacin"  # es xmpp_pass
config.trace = False

if __name__ == "__main__":
    normalAgent.main()