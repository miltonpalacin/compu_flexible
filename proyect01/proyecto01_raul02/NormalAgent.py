#from templates import make_metadata_with_body_template, make_reply, make_message
import utilities
import configNormalAgent as config
import time
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour


# from credentials import xmpp_user_1
# shared_files_path = "./shared_files"
# directory_agent = xmpp_user_1
#shared_files_path = ""
#directory_agent = ""


class NormalAgent(Agent):

    class JoinNetwork(OneShotBehaviour):
        async def run(self):
            print('Sending request to join network')
            
            files_list = utilities.get_files_list(shared_files_path)
            join_template = make_metadata_with_body_template(performative='join', ontology='request', body=files_list)
            msg = make_message(join_template, to=directory_agent)
            await self.send(msg)
            print('Join request sent')
            self.exit_code = "Join request sent"

    # class WaitForFileListRequest(CyclicBehaviour):
    #     async def run(self):
    #         msg = await self.receive()
    #         if msg:
    #             file_list = utilities.get_files_list(shared_files_path)
    #             answer_template = make_metadata_with_body_template(performative='sendFileList', ontology='data', body=file_list)
    #             reply = make_reply(msg, answer_template)
    #             await self.send(reply)
    #             print("Request received, answer with file list was sent")

    async def setup(self):
        self.add_behaviour(self.JoinNetwork())
        #request_template = make_metadata_with_body_template(performative='requestFiles', ontology='give_data', body='sendFileList')
        #self.add_behaviour(self.WaitForFileListRequest(), template=request_template)


if __name__ == "__main__":
    print("="*50)
    print('Welcome to the P2P network')
    print("="*50)
    # xmpp_user = input("Enter your username: ")
    # xmpp_pass = input("Enter your password: ")
    # shared_files_path = input("Enter your shared files path: ")
    # xmpp_user = xmpp_user + "@chatterboxtown.us"

    # opcional/comentar
    # utilities.check_shared_dir(shared_files_path)
    normalAgent = NormalAgent(config.xmpp_user, config.xmpp_pass)
    future = normalAgent.start()
    future.result()

    while normalAgent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            normalAgent.stop()
            break
    print('Agents finished')
    quit_spade()
