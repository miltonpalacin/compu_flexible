import helper
import fileHelper
import dbNormalAgentHelper as dbHelper
import messageHelper 
# from messageHelper import encode_array, decode_array
import configNormalAgent as config
import time
import datetime
import asyncio
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
#from spade.behaviour import OneShotBehaviour
from spade.behaviour import PeriodicBehaviour


# from credentials import xmpp_user_1
# shared_files_path = "./shared_files"
# directory_agent = xmpp_user_1
# shared_files_path = ""
# directory_agent = ""


class NormalAgent(Agent):

    class FilesPublication(PeriodicBehaviour):
        async def run(self):
            print('File data publication submission request ')
            # procesar todos los archivos a compartir
            files = fileHelper.agent_file_list(config.agent_user, config.sf_path)
            # Guardando todo en base de datos
            public_files = dbHelper.save_initial_agent_files(files)
            coded_message = messageHelper.encode_array(public_files)

            join_template = messageHelper.files_register_template(body=coded_message)
            msg = messageHelper.make_message(join_template, to=config.xmpp_directory())
            await self.send(msg)
            print('Publication request sent ')
            print('-'*50)

            self.exit_code = "Publication request sent"

    class PublicConfirm(CyclicBehaviour):
        async def run(self):
            files_msg = await self.receive()
            if files_msg:
                sender_name = helper.sanitize_sender_name(str(files_msg.sender))
                if files_msg.body is not None:
                    files = messageHelper.decode_array(files_msg.body)
                    dbHelper.confirm_agent_pub(files)
                    print("Publication confirmation has been received from",
                          "'" + sender_name + "'", "to", "'" + config.agent_user + "'")
                    print('-'*50)
            await asyncio.sleep(1)

#     class ChangePublic(PeriodicBehaviour):
#         async def run(self):
#             print('Sending changes of public files to directory')
#             # procesar todos los archivos a compartir
#             files = fileHelper.agent_file_list(config.agent_user, config.sf_path)
#             if files:
#                 # Guardando todo en base de datos
#                 public_files = dbHelper.save_initial_agent_files(files)
#                 coded_message = messageHelper.encode_array(public_files)

#                 join_template = messageHelper.join_network_template(body=coded_message)
#                 msg = messageHelper.make_message(join_template, to=config.xmpp_directory())
#                 await self.send(msg)
#                 print('Changes sent')

#             self.exit_code = "Changes sent"

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
        start_at = datetime.datetime.now() + datetime.timedelta(seconds=1)
        # cada 10 segundos
        self.add_behaviour(behaviour=self.FilesPublication(period=10, start_at=start_at))

        public_confirm_template = messageHelper.public_confirm_template()
        self.add_behaviour(behaviour=self.PublicConfirm(), template=public_confirm_template)


if __name__ == "__main__":
    print("="*80)
    print('Welcome to the P2P network')
    print("="*80)

    # xmpp_user = input("Enter your username: ")
    # xmpp_pass = input("Enter your password: ")
    # shared_files_path = input("Enter your shared files path: ")
    # xmpp_user = xmpp_user + "@chatterboxtown.us"

    # opcional/comentar
    # utilities.check_shared_dir(shared_files_path)
    normal_agent = NormalAgent(config.xmpp_agent(), config.agent_pass)
    future = normal_agent.start()
    future.result()

    while normal_agent.is_alive():
        try:
            time.sleep(2)
            print("Choose one of the following options:")
            print("1. Search for a file by name")
            print("1. Search for a file by extension")
            print("2. End this peer")
            opt = int(input("Enter option: "))

            if opt not in range(1, 3):
                print("Please choose a valid option")
                continue

            if opt == 1:
                # do the search
                print("You have chosen to make a search, it might take a while.")
                filename = input("Enter filename or parte of name: ")
                if not helper.check_file_name(filename):
                    print("Please enter a valid name")
                    filename = ""
                    continue

                ask_file = True

            if opt == 2:
                # do the search
                print("You have chosen to make a search, it might take a while.")
                filename = input("Enter file name o part of name: ")
                if not utilities.check_file_name(filename):
                    print("Please enter a valid name")
                    filename = ""
                    continue

                ask_file = True

            if opt == 2:
                # do the search
                print("You have chosen to make a search, it might take a while.")
                filename = input("Enter file extension: ")
                if not utilities.check_file_name(filename):
                    print("Please enter a valid fin")
                    filename = ""
                    continue

                    
            if opt == 2:
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
