import templates
from credentials import xmpp_user_1
import utilities
import time
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from os import path
import base64

shared_files_path = "./shared_files"
directory_agent = xmpp_user_1
filename = ''
file_list = []
ask_file = False


class NormalAgent(Agent):

    class RequestFileAgentsList(CyclicBehaviour):
        async def run(self):
            global ask_file
            if ask_file:
                ask_file = False
                print("Sending file request to directory")
                request_file_template = templates.request_file_agent_list_template(filename)
                msg = templates.make_message(request_file_template, to=directory_agent)
                await self.send(msg)
                print('Request to directory was sent')
                self.exit_code = "file request sent"

    class ReceiveAgentsList(CyclicBehaviour):

        async def run(self):
            file_list_response = await self.receive()
            if file_list_response:
                if file_list_response.body is not None and len(file_list_response.body.split("###")) > 0:
                    agents_id = file_list_response.body.split("###")
                    owner = agents_id[0]
                    # try to download file from a peer
                    print("Requesting file to a peer ...")
                    answer_template = templates.send_file_template(filename)
                    msg = templates.make_message(answer_template, to=owner)
                    await self.send(msg)
                else:
                    print("There is no agent that has the file. Sorry :(")
                    return

    class ReceiveFileFromPeer(CyclicBehaviour):
        async def run(self):
            request = await self.receive()
            if request:
                print("Downloading file from a peer")
                message = request.body

                if message is None or len(message.split("$$$$$")) < 3:
                    print("File couldn't be downloaded from peer")
                    return
                contents = message.split("$$$$$")
                file_name = contents[1] + "." + contents[2]
                complete_file_name = shared_files_path + "/" + file_name
                f = open(complete_file_name, "w+")
                base64_message = contents[0]
                base64_bytes = base64_message.encode('ascii')
                message_bytes = base64.b64decode(base64_bytes)
                file_content = message_bytes.decode('ascii')
                f.write(file_content)
                f.close()
                request_template = templates.update_file_list_template(file_name)
                msg = templates.make_message(request_template, to=directory_agent)
                await self.send(msg)
                print("File was downloaded successfully")

    class SendFileToPeer(CyclicBehaviour):
        async def run(self):
            request = await self.receive()
            if request:
                file_name = request.body
                if file_name == '':
                    return
                # print("File ", file_name, " was requested for download")
                complete_file_path = shared_files_path + "/" + file_name
                message = ''
                if path.exists(complete_file_path):
                    f = open(complete_file_path, "r")
                    content = f.read()
                    message_bytes = content.encode('ascii')
                    base64_bytes = base64.b64encode(message_bytes)
                    content = base64_bytes.decode('ascii')
                    name, ext = file_name.split(".")
                    message = "$$$$$".join([content, name, ext])
                answer_template = templates.receive_file_template(message)
                reply = templates.make_reply(request, answer_template)
                await self.send(reply)
                # print("File ", file_name, " was sent to a peer")

    class JoinNetwork(OneShotBehaviour):
        async def run(self):
            print('Joining P2P network')
            files_list = utilities.get_files_list(shared_files_path)
            join_template = templates.join_network_template(body=files_list)
            msg = templates.make_message(join_template, to=directory_agent)
            await self.send(msg)
            # print('Join request sent')
            self.exit_code = "Join request sent"

    class WaitForFileListRequest(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            if msg:
                my_file_list = utilities.get_files_list(shared_files_path)
                answer_template = templates.file_list_response_template(body=my_file_list)
                reply = templates.make_reply(msg, answer_template)
                await self.send(reply)
                # print("Request received, answer with file list was sent")

    async def setup(self):
        self.add_behaviour(behaviour=self.JoinNetwork())
        request_template = templates.file_list_request_template()
        self.add_behaviour(behaviour=self.WaitForFileListRequest(), template=request_template)
        send_file_template = templates.send_file_template()
        self.add_behaviour(behaviour=self.SendFileToPeer(), template=send_file_template)
        receive_agent_list_template = templates.receive_agent_list_template()
        self.add_behaviour(behaviour=self.ReceiveAgentsList(), template=receive_agent_list_template)
        self.add_behaviour(behaviour=self.RequestFileAgentsList())
        send_file_template = templates.receive_file_template()
        self.add_behaviour(self.ReceiveFileFromPeer(), template=send_file_template)


if __name__ == "__main__":
    print('Welcome to the P2P network')
    xmpp_user = input("Enter your username: ")
    xmpp_pass = input("Enter your password: ")
    xmpp_user = xmpp_user + "@chatterboxtown.us"

    utilities.check_shared_dir(shared_files_path)
    normalAgent = NormalAgent(xmpp_user, xmpp_pass)
    future = normalAgent.start(auto_register=True)
    future.result()

    while normalAgent.is_alive():
        try:
            time.sleep(2)
            print("Choose one of the following options:")
            print("1. Search for a file")
            print("2. End this peer")
            opt = int(input("Enter option: "))

            if opt not in range(1, 3):
                print("Please choose a valid option")
                continue

            if opt == 1:
                # do the search
                print("You have chosen to make a search, it might take a while.")
                filename = input("Enter filename: ")
                if not utilities.check_file_name(filename):
                    print("Please enter a valid name")
                    filename = ""
                    continue

                ask_file = True

            if opt == 2:
                print("Stopping ... ")
                print("Bye bye")
                normalAgent.stop()
                break

        except KeyboardInterrupt:
            normalAgent.stop()
            break
    print("\nNormal Agent finished")
    quit_spade()
