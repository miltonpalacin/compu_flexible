from templates import make_message, make_metadata_with_body_template, make_metadata_template
from credentials import xmpp_user_1, xmpp_pass_1
import utilities
import datetime
import time
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour, CyclicBehaviour

agentsDirectory = []
filesList = {}


class DirectoryAgent(Agent):
    class RequestForFilesList(PeriodicBehaviour):
        async def run(self):
            request_template = make_metadata_with_body_template(performative='requestFiles', ontology='give_data', body='sendFileList')
            for ag in agentsDirectory:
                msg = make_message(request_template, to=ag)
                await self.send(msg)
                print("Requesting files to ", ag)

        async def on_end(self):
            await self.agent.stop()

        async def on_start(self):
            print("Starting behaviour that asks for files lists")

    class WaitForFilesListResponse(CyclicBehaviour):
        async def run(self):
            answer = await self.receive()
            if answer:
                sender_name = str(answer.sender)
                # update files list for this user
                filesList[sender_name] = answer.body.split(',')
                print('Answer received from ', sender_name)

    class ReceiveJoinRequest(CyclicBehaviour):
        async def run(self):
            request = await self.receive()
            if request:
                sender_name = str(request.sender)
                if sender_name not in agentsDirectory:
                    agentsDirectory.append(sender_name)
                    # save files list received from this user
                    filesList[sender_name] = request.body.split(',')
                    print("Request to join network received from new user ", sender_name)

    async def setup(self):
        print(f"Directory Agent started at {datetime.datetime.now().time()}")

        request_join_template = make_metadata_template(performative='join', ontology='request')
        self.add_behaviour(
            behaviour=self.ReceiveJoinRequest(),
            template=request_join_template)

        answer_template = make_metadata_template(performative='sendFileList', ontology='data')
        self.add_behaviour(
            behaviour=DirectoryAgent.WaitForFilesListResponse(),
            template=answer_template
        )

        start_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
        self.add_behaviour(self.RequestForFilesList(period=20, start_at=start_at))


if __name__ == "__main__":
    sender = DirectoryAgent(xmpp_user_1, xmpp_pass_1)
    future = sender.start()
    future.result()

    while sender.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            sender.stop()
            break
    print('Agents finished')
    quit_spade()
