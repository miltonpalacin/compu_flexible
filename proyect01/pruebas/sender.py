import time
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message


class SenderAgent(Agent):
    class InformBehav(OneShotBehaviour):
        async def run(self):
            print("InformBehav running")
            msg = Message(to="rarias@chatterboxtown.us")     # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")       # Set the language of the message content
            msg.body = """ Desarrollar un sistema sencillo en el que los peers puedan compartir archivos multimedia y 
                            poder de cómputo. Los archivos multimedia tienen un peer dueño (quien los publica por
                            primera vez) y los demás peers podrán acceder a dichos archivos ya sea desde el dueño, desde
                            cualquier otro peer que tenga una copia o simultáneamente de varios peers. Esto implica que
                            cuando se registra un archivo para compartir o se hace una copia, un Agente Directorio debe
                            estar al tanto. Cuando un peer solicita un archivo, ya sea por nombre exacto, por parte del
                            nombre, por tipo de archivo (fotos, vídeos, pdf, la clasificación la determinan Uds.), el
                            Directorio debe mostrarle al peer solicitante las copias disponibles en ese momento y si es
                            posible, recomendando la mejor (porque está más cerca, porque tiene mejor conexión, etc.) . La
                            transferencia debería realizarse de peer a peer (sin que pase por el Directorio). Para compartir
                            poder de cómputo, un peer solicitará este recurso y el Directorio le mostrará los peers cuyo
                            porcentaje de CPU esté por debajo de 40% (esto implica que eventualmente los peers que
                            ofrecen poder de cómputo informan al Directorio su estado o el Directorio pregunta a todos los
                            peers el estado cuando crea conveniente). El peer solicitante enviará un script de compilación y
                            ejecución de su programa y el código fuente. El peer receptor, ejecutará el script y cuando
                            finalice publicará en el Directorio un archivo con el resultado."""                    # Set the message content

            await self.send(msg)
            print("Message sent!")

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

            # stop agent from behaviour
            await self.agent.stop()

    async def setup(self):
        print("SenderAgent started")
        self.b = self.InformBehav()
        self.add_behaviour(self.b)


if __name__ == "__main__":
    agent = SenderAgent("mpalacin@chatterboxtown.us", "mpalacin")
    future = agent.start()
    future.result()

    while agent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            agent.stop()
            break
    print("Agent finished with exit code: {}".format(agent.b.exit_code))