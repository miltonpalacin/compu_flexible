from templates import make_message, make_metadata_template, make_file_list_template
from credentials import xmpp_user_1, xmpp_pass_1, xmpp_user_2

import datetime
import time
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, PeriodicBehaviour

agentsDirectory = []


class SenderAgent(Agent):
    class AskForFiles(PeriodicBehaviour):
        async def run(self):
            request_template = make_metadata_template(performative='request', ontology='give_data', body='sendFileList')
            msg = make_message(request_template, to=xmpp_user_2)
            await self.send(msg)
            print("Request for files list was sent!")
            answer_template = make_file_list_template(performative='inform', ontology='data')
            self.agent.add_behaviour(
                behaviour=SenderAgent.WaitForResponse(),
                template=answer_template
            )

        async def on_end(self):
            await self.agent.stop()

        async def on_start(self):
            print("Starting behaviour that asks for files lists")

    class WaitForResponse(OneShotBehaviour):
        async def run(self):
            answer = await self.receive(timeout=5)
            if answer:
                print('Answer received!: ', answer.body)
            else:
                print('Answer did not arrived after 5 seconds. Finishing request')

    async def setup(self):
        print(f"Sender Agent started at {datetime.datetime.now().time()}")
        start_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
        b = self.AskForFiles(period=10, start_at=start_at)
        self.add_behaviour(b)


if __name__ == "__main__":
    sender = SenderAgent(xmpp_user_1, xmpp_pass_1)
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
