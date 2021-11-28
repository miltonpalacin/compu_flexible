#from templates import make_message, make_metadata_with_body_template, make_metadata_template
#from credentials import xmpp_user_1, xmpp_pass_1
#import utilities
import helper
#import fileHelper
import dbDirectoryAgentHelper as dbHelper
import messageHelper
import configDirectoryAgent as config

import datetime
import time
import asyncio
from spade import quit_spade
from spade.agent import Agent
#from spade.behaviour import PeriodicBehaviour
from spade.behaviour import CyclicBehaviour

#agentsDirectory = []
#filesList = {}


class DirectoryAgent(Agent):

    class FilesRegister(CyclicBehaviour):
        async def run(self):
            files_msg = await self.receive()
            if files_msg:
                if files_msg.body is not None:
                    sender_name = helper.sanitize_sender_name(str(files_msg.sender))
                    dbHelper.activate_agent(sender_name)
                    files = messageHelper.decode_array(files_msg.body)
                    public_files = dbHelper.save_files_directory(sender_name, files)
                    coded_message = messageHelper.encode_array(public_files)

                    confirm_template = messageHelper.public_confirm_template(body=coded_message)
                    msg = messageHelper.make_message(confirm_template, to=str(files_msg.sender))
                    await self.send(msg)
                    print("Data of files was published from the user ", sender_name)
                    print('-'*50)
            await asyncio.sleep(1)
#     class RequestForFilesList(PeriodicBehaviour):
#         async def run(self):
#             request_template = make_metadata_with_body_template(performative='requestFiles', ontology='give_data', body='sendFileList')
#             for ag in agentsDirectory:
#                 msg = make_message(request_template, to=ag)
#                 await self.send(msg)
#                 print("Requesting files to ", ag)

#         async def on_end(self):
#             await self.agent.stop()

#         async def on_start(self):
#             print("Starting behaviour that asks for files lists")

#     class WaitForFilesListResponse(CyclicBehaviour):
#         async def run(self):
#             answer = await self.receive()
#             if answer:
#                 sender_name = str(answer.sender)
#                 # update files list for this user
#                 filesList[sender_name] = answer.body.split(',')
#                 print('Answer received from ', sender_name)

#     class ReceiveJoinRequest(CyclicBehaviour):
#         async def run(self):
#             request = await self.receive()
#             if request:
#                 sender_name = str(request.sender)
#                 if sender_name not in agentsDirectory:
#                     agentsDirectory.append(sender_name)
#                     # save files list received from this user
#                     filesList[sender_name] = request.body.split(',')
#                     print("Request to join network received from new user ", sender_name)

    async def setup(self):
        print("="*80)
        print(f"Directory Agent started at {datetime.datetime.now().time()}")
        print("="*80)

        files_register_template = messageHelper.files_register_template()
        self.add_behaviour(behaviour=self.FilesRegister(), template=files_register_template)

#         request_join_template = make_metadata_template(performative='join', ontology='request')
#         self.add_behaviour(
#             behaviour=self.ReceiveJoinRequest(),
#             template=request_join_template)

#         answer_template = make_metadata_template(performative='sendFileList', ontology='data')
#         self.add_behaviour(
#             behaviour=DirectoryAgent.WaitForFilesListResponse(),
#             template=answer_template
#         )

#         start_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
#         self.add_behaviour(self.RequestForFilesList(period=20, start_at=start_at))


if __name__ == "__main__":
    # sender = DirectoryAgent(xmpp_user_1, xmpp_pass_1)
    # future = sender.start()
    directory_agent = DirectoryAgent(config.xmpp_agent(), config.agent_pass)
    future = directory_agent.start()
    future.result()

    while directory_agent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            directory_agent.stop()
            break
    print('Agents finished')
    quit_spade()
