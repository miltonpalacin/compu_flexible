from templates import make_metadata_template, make_reply
from credentials import xmpp_user_2, xmpp_pass_2
import time
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from os import listdir, mkdir
from os.path import isfile, join
from os import path

shared_files_path = "./shared_files"


class ReceiverAgent(Agent):

    class WaitForRequest(CyclicBehaviour):

        def get_files_list(self):
            only_files = [f for f in listdir(shared_files_path) if isfile(join(shared_files_path, f))]
            my_file_list = ' '.join(only_files)
            return my_file_list

        async def run(self):
            msg = await self.receive()
            if msg:
                file_list = self.get_files_list()
                answer_template = make_metadata_template(performative='inform', ontology='data', body=file_list)
                reply = make_reply(msg, answer_template)
                await self.send(reply)
                print("Request received, answer with file list was sent")

    async def setup(self):
        print("Hello! I'm waiting for a request")
        request_template = make_metadata_template(performative='request', ontology='give_data', body='sendFileList')
        self.add_behaviour(self.WaitForRequest(), template=request_template)


def check_shared_dir():
    if path.exists(shared_files_path):
        return

    mkdir(shared_files_path)
    f = open(shared_files_path + "/file_1.txt", "a")
    f.write("file 1 for test")
    f.close()
    f = open(shared_files_path + "/file_2.txt", "a")
    f.write("file 2 for test")
    f.close()


if __name__ == "__main__":
    check_shared_dir()
    server = ReceiverAgent(xmpp_user_2, xmpp_pass_2)
    future = server.start()
    future.result()

    while server.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            server.stop()
            break
    print('Agents finished')
    quit_spade()
