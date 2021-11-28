from libs.cross import helper
from libs.directory import dbDirectoryAgentHelper as dbHelper
from libs.cross import messageHelper
from libs.directory import configDirectoryAgent as config

import datetime
import time
import asyncio
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour


config.agent_user = "directory_agent"  # es xmpp_user
config.agent_pass = "directory_agent"  # es xmpp_pass


class DirectoryAgent(Agent):

    class FilesRegister(CyclicBehaviour):
        async def run(self):
            files_msg = await self.receive()
            if files_msg:
                if files_msg.body is not None:
                    sender_name = helper.sanitize_sender_name(str(files_msg.sender))
                    dbHelper.activate_agent(sender_name)
                    files = messageHelper.decode_array(files_msg.body)
                    is_ok = dbHelper.save_files_directory(sender_name, files)
                    #coded_message = messageHelper.encode_array(public_files)
                    message = "Sucessful" if is_ok else "Something went wrong"

                    confirm_template = messageHelper.public_confirm_template(body=message)
                    msg = messageHelper.make_message(confirm_template, to=str(files_msg.sender))
                    await self.send(msg)
                    if is_ok:
                        print("Data of files were published from the agent", sender_name)
                    else:
                        print("Data of files were not published from the agent", sender_name)
                    print('-'*50)
            await asyncio.sleep(1)

    class SearchFile(CyclicBehaviour):
        async def run(self):
            searh_msg = await self.receive()
            if searh_msg:
                if searh_msg.body is not None:
                    print("Request for a file received")
                    sender_name = helper.sanitize_sender_name(str(searh_msg.sender))

                    search_arr = messageHelper.decode_array(searh_msg.body)
                    search_files = dbHelper.search_for_file(sender_name, search_arr)
                    coded_message = messageHelper.encode_array(search_files)

                    answer_template = messageHelper.receive_agent_list_template(body=coded_message)
                    msg = messageHelper.make_message(answer_template, to=str(searh_msg.sender))
                    await self.send(msg)
                    print("Answer for agent list for a file was sent to ", sender_name)
                    print('-'*50)
            await asyncio.sleep(1)

    async def setup(self):
        print("="*80)
        print(f"Directory Agent started at {datetime.datetime.now().time()}")
        print("="*80)

        files_register_template = messageHelper.files_register_template()
        self.add_behaviour(behaviour=self.FilesRegister(), template=files_register_template)

        request_file_agent_list_template = messageHelper.request_file_agent_list_template()
        self.add_behaviour(behaviour=self.SearchFile(), template=request_file_agent_list_template)


if __name__ == "__main__":
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
