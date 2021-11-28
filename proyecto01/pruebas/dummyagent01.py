from spade import agent, quit_spade


class DummyAgent(agent.Agent):
    async def setup(self):
        print("Hello World! I'm agent {}".format(str(self.jid)))

def test():
    dummy = DummyAgent("rarias@chatterboxtown.us", "rarias")
    future = dummy.start()
    future.result()

    dummy.stop()
    quit_spade()


if __name__ == "__main__":
    test()