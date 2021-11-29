import psutil
from libs.cross import helper
from libs.agent import fileHelper
from libs.agent import dbNormalAgentHelper as dbHelper
from libs.cross import messageHelper
from libs.agent import configNormalAgent as config
import time
import datetime
import asyncio
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.behaviour import PeriodicBehaviour


class NormalAgent(Agent):

    class FilesPublication(PeriodicBehaviour):
        async def run(self):
            config.trace and print('File data publication submission request ')
            # procesar todos los archivos a compartir
            files = fileHelper.agent_file_list(config.agent_user, config.sf_path)
            # Guardando todo en base de datos
            public_files = dbHelper.save_initial_agent_files(files)
            coded_message = messageHelper.encode_array(public_files)

            join_template = messageHelper.files_register_template(body=coded_message)
            msg = messageHelper.make_message(join_template, to=config.xmpp_directory())
            await self.send(msg)
            config.trace and print('Publication request sent ')
            config.trace and print('-'*50)

            self.exit_code = "Publication request sent"

    class PublicConfirm(CyclicBehaviour):
        async def run(self):
            files_msg = await self.receive()
            if files_msg:
                sender_name = helper.sanitize_sender_name(str(files_msg.sender))
                if files_msg.body is not None:
                    message = str(files_msg.body)
                    config.trace and print("Publication confirmation has been received from",
                                           "'" + sender_name + "'", "to", "'" +
                                           config.agent_user + "':", message)
                    config.trace and print('-'*50)

            await asyncio.sleep(1)

    class FileRequest(CyclicBehaviour):
        async def run(self):
            if config.ask_file_ext or config.ask_file_name:
                search = messageHelper.encode_array([config.text_search, config.ask_file_ext])
                config.ask_file_ext = False
                config.ask_file_name = False
                config.index_file = -1
                config.trace and print("Sending file request to directory")

                request_file_template = messageHelper.request_file_agent_list_template(search)
                msg = messageHelper.make_message(request_file_template, to=config.xmpp_directory())
                await self.send(msg)
                config.trace and print('Request to directory was sent')
                config.trace and print('-'*50)
                self.exit_code = "file request sent"

            await asyncio.sleep(1)

    class ReceiveAgentsList(CyclicBehaviour):

        async def run(self):
            files_msg = await self.receive()
            if files_msg:
                if files_msg.body is not None:
                    config.files_found = messageHelper.decode_array(files_msg.body)
                    config.trace and print(f"Response: {len(config.files_found)} files found for request of '{config.agent_user}'")
                    config.trace and print('-'*50)

            await asyncio.sleep(1)

    ###########################################################################
    # REQUEST FOR FILE
    ###########################################################################
    class RequestDownloadAgentFile(CyclicBehaviour):
        async def run(self):
            if config.selected_file:
                file_code = config.selected_file["code"]
                agents_receive = config.selected_file["agent"]

                config.trace and print("Requesting file to a peer ...")
                config.trace and print('-'*50)

                answer_template = messageHelper.send_file_template(file_code)
                msg = messageHelper.make_message(answer_template, to=config.xmpp_peer(agents_receive))
                config.selected_file = None
                await self.send(msg)

                self.exit_code = "Dowload request sent"

            await asyncio.sleep(1)

    class DownloadAgentFile(CyclicBehaviour):
        async def run(self):
            request = await self.receive()

            if request:
                config.trace and print("Downloading file from a peer")
                message = request.body

                if message is None:
                    config.trace and print("File couldn't be downloaded from peer")
                    return

                messageHelper.decode_file(config.sf_path, message)
                config.trace and print("File was downloaded successfully")
                config.trace and print('-'*50)

            await asyncio.sleep(1)

    class UploadAgentFile(CyclicBehaviour):
        async def run(self):
            request = await self.receive()
            if request:
                config.trace and print("Uploading file...")
                message = request.body

                if message is None:
                    config.trace and print("File couldn't be uploaded")
                    return
                file_code = str(message)
                selected_file = dbHelper.get_file_info(file_code)
                file_path = selected_file["path"]

                filename = selected_file["name"] + "." + selected_file["ext"]
                message = messageHelper.encode_file(filename, file_path)

                answer_template = messageHelper.receive_file_template(message)
                reply = messageHelper.make_reply(request, answer_template)
                await self.send(reply)

                config.trace and print("File was uploaded successfully")
                config.trace and print('-'*50)

            await asyncio.sleep(1)

    ################################################################################################################
    # REQUEST CPU POWER
    ################################################################################################################

    class RequestCpuBorrow(CyclicBehaviour):
        async def run(self):
            #global ask_cpu
            if config.ask_cpu:
                config.ask_cpu = False
                print("Sending request for CPU...")
                request_file_template = messageHelper.request_cpu_template()
                msg = messageHelper.make_message(request_file_template, to=config.xmpp_directory())
                await self.send(msg)
                print('request for CPU was sent')
                self.exit_code = "cpu request sent"
            await asyncio.sleep(1)

    class ReceiveCpuBorrow(CyclicBehaviour):
        async def run(self):

            request = await self.receive()
            if request:
                if request.body is None or request.body == '':
                    print("There is no peer available to borrow some CPU")
                    config.finish_cpu_borrow = True
                    return
                peer_id = request.body
                peer_request_template = messageHelper.request_cpu_exec_template("content to execute")
                msg = messageHelper.make_message(peer_request_template, to=config.xmpp_peer(peer_id))
                await self.send(msg)
                print("Request for CPU to a peer was sent")
            await asyncio.sleep(1)

    class ReceiveExecuteResult(CyclicBehaviour):
        async def run(self):
            response = await self.receive()
            #print(response)
            if response:
                result = response.body
                print("Result received: ", result)
                config.finish_cpu_borrow = True
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
                print("Request for CPU percentage was received from ", requestor_name)
                message = "$$".join([requestor_name, str(cpu_per)])
                cpu_per_request_template = messageHelper.response_cpu_per_template(message)
                msg = messageHelper.make_message(cpu_per_request_template, to=config.xmpp_directory())
                await self.send(msg)
                print("CPU percentage was sent")
            await asyncio.sleep(1)

    class ReceiveExecutionRequest(CyclicBehaviour):
        async def run(self):
            request = await self.receive()
            if request:
                username = helper.sanitize_sender_name(str(request.sender))
                print("A request for execution was received from ", username)
                # do the execution
                answer_template = messageHelper.receive_cpu_result_template("Executed Successfully")
                msg = messageHelper.make_message(answer_template, to=config.xmpp_peer(username))
                await self.send(msg)
                print("Result was sent")
            await asyncio.sleep(1)

    async def setup(self):
        start_at = datetime.datetime.now() + datetime.timedelta(seconds=1)
        # cada 10 segundos
        self.add_behaviour(behaviour=self.FilesPublication(period=120, start_at=start_at))

        public_confirm_template = messageHelper.public_confirm_template()
        self.add_behaviour(behaviour=self.PublicConfirm(), template=public_confirm_template)

        self.add_behaviour(behaviour=self.FileRequest())

        receive_agent_list_template = messageHelper.receive_agent_list_template()
        self.add_behaviour(behaviour=self.ReceiveAgentsList(), template=receive_agent_list_template)

        self.add_behaviour(behaviour=self.RequestDownloadAgentFile())

        receive_file_template = messageHelper.receive_file_template()
        self.add_behaviour(behaviour=self.DownloadAgentFile(), template=receive_file_template)

        send_file_template = messageHelper.send_file_template()
        self.add_behaviour(behaviour=self.UploadAgentFile(), template=send_file_template)

        ################################################################################################################
        # REQUEST CPU POWER
        ################################################################################################################

        self.add_behaviour(self.RequestCpuBorrow())
        receive_cpu_template = messageHelper.receive_cpu_template()
        self.add_behaviour(behaviour=self.ReceiveCpuBorrow(), template=receive_cpu_template)
        receive_result_template = messageHelper.receive_cpu_result_template()
        self.add_behaviour(behaviour=self.ReceiveExecuteResult(), template=receive_result_template)

        ################################################################################################################
        # GIVE CPU POWER
        ################################################################################################################
        my_template = messageHelper.receive_cpu_per_template()
        self.add_behaviour(behaviour=self.ReceiveCpuPerRequest(), template=my_template)
        my_template = messageHelper.request_cpu_exec_template()
        self.add_behaviour(behaviour=self.ReceiveExecutionRequest(), template=my_template)


def main_with_trace(normal_agent):
    while normal_agent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            normal_agent.stop()
            break


def main_without_trace(normal_agent):
    opt = 0
    while normal_agent.is_alive():

        try:
            time.sleep(2)

            if config.files_found:
                print("="*80)
                print("Choose one of the files and  the end peer:")
                for index, file in enumerate(config.files_found):
                    print(f"[{index + 1}] {file['name']}.{file['ext']} from {file['agent']}")
                opt = int(input("Enter option: "))

                config.selected_file = config.files_found[opt - 1]
                print("Selected:", f"{config.selected_file['name']}.{config.selected_file['ext']} from {config.selected_file['agent']}")

                config.files_found = None
                opt = 0
                continue

            elif opt in [1, 2, 3]:
                print("Unsuccessful search!")

            print("="*80)
            print("Choose one of the following options:")
            print("(1) Search for a file by name")
            print("(2) Search for a file by extension")
            print("(3) Search of cpu for executing a program")
            print("(4) End this peer")
            opt = int(input("Enter option: "))

            if opt not in range(1, 5):
                print("Please choose a valid option")
                continue

            if opt == 1:
                # do the search
                print("You have chosen to make a search, it might take a while.")
                config.text_search = input("Enter filename or parte of name: ")
                if not helper.check_file_name(config.text_search):
                    print("Please enter a valid name")
                    config.text_search = ""
                    continue

                config.ask_file_name = True
                time.sleep(1)
                continue

            if opt == 2:
                # do the search
                print("You have chosen to make a search, it might take a while.")
                config.text_search = input("Enter file extension o part of extension: ")
                if not helper.check_file_ext(config.text_search):
                    print("Please enter a valid extension")
                    config.text_search = ""
                    continue

                config.ask_file_ext = True
                time.sleep(1)
                continue

            if opt == 3:
                # do the search
                filepath = input("Enter the path of the file you wish to execute:")
                if not helper.check_file_path(filepath):
                    print("Please enter a valid filepath")
                    filepath = ""
                    continue
                config.finish_cpu_borrow = False
                config.ask_cpu = True
                # give the agent time to complete
                while not config.finish_cpu_borrow:
                    time.sleep(1)

            if opt == 4:
                print("Stopping ... ")
                print("Bye bye")
                normal_agent.stop()
                break

        except KeyboardInterrupt:
            normal_agent.stop()
            break


def main():
    print("="*80)
    print('Welcome to the P2P network')
    print("="*80)

    normal_agent = NormalAgent(config.xmpp_agent(), config.agent_pass)
    future = normal_agent.start()
    future.result()

    if config.trace:
        main_with_trace(normal_agent)
    else:
        main_without_trace(normal_agent)

    print("\nNormal Agent finished")

    quit_spade()
