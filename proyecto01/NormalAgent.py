import templates
from credentials import xmpp_user_1
import utilities
import time
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from os import path
import base64
import psutil
import asyncio

shared_files_path = "./shared_files"
directory_agent = xmpp_user_1
filename = ''
filepath = ''
file_list = []
ask_file = False
ask_cpu = False
finish_file_download = False
finish_cpu_borrow = False


class NormalAgent(Agent):

    ################################################################################################################
    # REQUEST CPU POWER
    ################################################################################################################

    class RequestCpuBorrow(CyclicBehaviour):
        async def run(self):
            global ask_cpu
            if ask_cpu:
                ask_cpu = False
                print("Sending request for CPU...")
                request_file_template = templates.request_cpu_template()
                msg = templates.make_message(request_file_template, to=directory_agent)
                await self.send(msg)
                print('request for CPU was sent')
                self.exit_code = "cpu request sent"
            await asyncio.sleep(1)

    class ReceiveCpuBorrow(CyclicBehaviour):
        async def run(self):
            global finish_cpu_borrow
            request = await self.receive()
            if request:
                if request.body is None or request.body == '':
                    print("There is no peer available to borrow some CPU")
                    finish_cpu_borrow = True
                    return
                peer_id = request.body
                peer_request_template = templates.request_cpu_exec_template("content to execute")
                msg = templates.make_message(peer_request_template, to=peer_id)
                await self.send(msg)
                print("Request for CPU to a peer was sent")
            await asyncio.sleep(1)

    class ReceiveExecuteResult(CyclicBehaviour):
        async def run(self):
            response = await self.receive()
            if response:
                global finish_cpu_borrow
                result = response.body
                print("Result received: ", result)
                finish_cpu_borrow = True
            #else:
                # TODO add how much time to wait for response
            #    return
            await asyncio.sleep(1)

    ################################################################################################################
    # GIVE CPU POWER
    ################################################################################################################

    class ReceiveCpuPerRequest(CyclicBehaviour):
        async def run(self):
            request = await self.receive()
            if request:
                cpu_per = psutil.cpu_percent()
                requestor_name = request.body
                # print("Request for CPU percentage was received from ", requestor_name)
                message = "$$".join([requestor_name, str(cpu_per)])
                cpu_per_request_template = templates.response_cpu_per_template(message)
                msg = templates.make_message(cpu_per_request_template, to=directory_agent)
                await self.send(msg)
                # print("CPU percentage was sent")
            await asyncio.sleep(1)

    class ReceiveExecutionRequest(CyclicBehaviour):
        async def run(self):
            request = await self.receive()
            if request:
                username = utilities.sanitize_sender_name(str(request.sender))
                # print("A request for execution was received from ", username)
                # do the execution
                answer_template = templates.receive_cpu_result_template("Executed Successfully")
                msg = templates.make_message(answer_template, to=username)
                await self.send(msg)
                # print("Result was sent")
            await asyncio.sleep(1)

    ################################################################################################################
    # REQUEST FILE
    ################################################################################################################

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
            await asyncio.sleep(1)

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
                    global finish_file_download
                    finish_file_download = True
                    return
            await asyncio.sleep(1)

    class ReceiveFileFromPeer(CyclicBehaviour):
        async def run(self):
            request = await self.receive()
            if request:
                print("Downloading file from a peer")
                message = request.body
                global finish_file_download
                if message is None or len(message.split("$$$$$")) < 3:
                    print("File couldn't be downloaded from peer")
                    finish_file_download = True
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
                finish_file_download = True
            await asyncio.sleep(1)

    ################################################################################################################
    # SHARE FILES
    ################################################################################################################

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
            await asyncio.sleep(1)

    ################################################################################################################
    # JOIN NETWORK
    ################################################################################################################

    class JoinNetwork(OneShotBehaviour):
        async def run(self):
            print('Joining P2P network')
            files_list = utilities.get_files_list(shared_files_path)
            join_template = templates.join_network_template(body=files_list)
            msg = templates.make_message(join_template, to=directory_agent)
            await self.send(msg)
            # print('Join request sent')
            self.exit_code = "Join request sent"

    ################################################################################################################
    # SEND FILE LIST
    ################################################################################################################

    class WaitForFileListRequest(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            if msg:
                my_file_list = utilities.get_files_list(shared_files_path)
                answer_template = templates.file_list_response_template(body=my_file_list)
                reply = templates.make_reply(msg, answer_template)
                await self.send(reply)
                # print("Request received, answer with file list was sent")
            await asyncio.sleep(1)

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

        ################################################################################################################
        # REQUEST CPU POWER
        ################################################################################################################

        self.add_behaviour(self.RequestCpuBorrow())
        receive_cpu_template = templates.receive_cpu_template()
        self.add_behaviour(behaviour=self.ReceiveCpuBorrow(), template=receive_cpu_template)
        receive_result_template = templates.receive_cpu_result_template()
        self.add_behaviour(behaviour=self.ReceiveExecuteResult(), template=receive_result_template)

        ################################################################################################################
        # GIVE CPU POWER
        ################################################################################################################
        my_template = templates.receive_cpu_per_template()
        self.add_behaviour(behaviour=self.ReceiveCpuPerRequest(), template=my_template)
        my_template = templates.request_cpu_exec_template()
        self.add_behaviour(behaviour=self.ReceiveExecutionRequest(), template=my_template)


#if __name__ == "__main__":
# print('Welcome to the P2P network')
#     xmpp_user = input("Enter your username: ")
#     xmpp_pass = input("Enter your password: ")
#     xmpp_user = xmpp_user + "@chatterboxtown.us"
def main(user, passwd):
    print('Welcome to the P2P network')
    xmpp_user = user
    xmpp_pass = passwd
    xmpp_user = xmpp_user + "@chatterboxtown.us"

    utilities.check_shared_dir(shared_files_path)
    normalAgent = NormalAgent(xmpp_user, xmpp_pass)
    future = normalAgent.start(auto_register=True)
    future.result()

    while normalAgent.is_alive():
        try:
            time.sleep(1)
            print("Choose one of the following options:")
            print("1. Search for a file")
            print("2. Execute a program")
            print("3. End this peer")
            opt = int(input("Enter option: "))

            if opt not in range(1, 4):
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

                finish_file_download = False
                ask_file = True
                # give the agent time to complete
                while not finish_file_download:
                    time.sleep(0.05)

            if opt == 2:
                # do the search
                filepath = input("Enter the path of the file you wish to execute: ")
                if not utilities.check_file_path(filepath):
                    print("Please enter a valid filepath")
                    filepath = ""
                    continue
                finish_cpu_borrow = False
                ask_cpu = True
                # give the agent time to complete
                while not finish_cpu_borrow:
                    time.sleep(0.05)

            if opt == 3:
                print("Stopping ... ")
                print("Bye bye")
                normalAgent.stop()
                break

        except KeyboardInterrupt:
            normalAgent.stop()
            break
    print("\nNormal Agent finished")
    quit_spade()
