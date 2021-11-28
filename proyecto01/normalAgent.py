import helper
import fileHelper
import dbNormalAgentHelper as dbHelper
import messageHelper
import configNormalAgent as config
import time
import datetime
import asyncio
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
#from spade.behaviour import OneShotBehaviour
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
                    files = messageHelper.decode_array(files_msg.body)
                    dbHelper.confirm_agent_pub(files)
                    config.trace and print("Publication confirmation has been received from",
                          "'" + sender_name + "'", "to", "'" + config.agent_user + "'")
                    config.trace and print('-'*50)
            await asyncio.sleep(1)

    class FileRequest(CyclicBehaviour):
        async def run(self):
            if config.ask_file_ext or config.ask_file_name:
                search = messageHelper.encode_array([config.text_search, config.ask_file_ext])
                config.ask_file_ext = False
                config.ask_file_name = False
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

    async def setup(self):
        start_at = datetime.datetime.now() + datetime.timedelta(seconds=1)
        # cada 10 segundos
        self.add_behaviour(behaviour=self.FilesPublication(period=10, start_at=start_at))

        public_confirm_template = messageHelper.public_confirm_template()
        self.add_behaviour(behaviour=self.PublicConfirm(), template=public_confirm_template)

        self.add_behaviour(behaviour=self.FileRequest())

        receive_agent_list_template = messageHelper.receive_agent_list_template()
        self.add_behaviour(behaviour=self.ReceiveAgentsList(), template=receive_agent_list_template)


if __name__ == "__main__":
    print("="*80)
    print('Welcome to the P2P network')
    print("="*80)

    normal_agent = NormalAgent(config.xmpp_agent(), config.agent_pass)
    future = normal_agent.start()
    future.result()

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

                print(config.files_found[opt - 1])

                config.files_found = None
                continue
            elif opt in [1, 2]:
                print("Unsuccessful search!")

            print("="*80)
            print("Choose one of the following options:")
            print("(1) Search for a file by name")
            print("(2) Search for a file by extension")
            print("(3) End this peer")
            opt = int(input("Enter option: "))

            if opt not in range(1, 4):
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
                print("Stopping ... ")
                print("Bye bye")
                normal_agent.stop()
                break

        except KeyboardInterrupt:
            normal_agent.stop()
            break
    print("\nNormal Agent finished")

#         try:
#             time.sleep(1)
#         except KeyboardInterrupt:
#             normal_agent.stop()
#             break
#     print('Agents finished')

    quit_spade()
