import normalAgent
from libs.agent import configNormalAgent as config

config.sf_path = "/DATA/maestria/12.CloudFlexible/Material"  # shared files
config.directory_agent = "directory_agent"
config.agent_user = "rarias"  # es xmpp_user
config.agent_pass = "rarias"  # es xmpp_pass
config.trace = True

if __name__ == "__main__":
    normalAgent.main()