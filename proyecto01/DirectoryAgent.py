import templates
import sqlite3
from credentials import xmpp_user_1, xmpp_pass_1
import utilities
import datetime
import time
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour, CyclicBehaviour
import random
import asyncio

DB_NAME = "directoryAgent.db"
cpu_req = {}


class DirectoryAgent(Agent):

    ################################################################################################################
    # REQUEST CPU POWER
    ################################################################################################################
    class ReceiveCpuRequest(CyclicBehaviour):
        @staticmethod
        def get_users(username):
            conn = sqlite3.connect(DB_NAME)
            conn_obj = conn.cursor()
            rows = conn_obj.execute("SELECT * FROM agents where username <> '" + username + "'").fetchall()
            conn.close()
            agents = []
            if len(rows) < 1:
                return agents

            # we choose just 5 agents randomly
            if len(rows) > 5:
                rows  = random.sample(population=rows, k=5)

            for row in rows:
                agents.append(row[0])

            return agents

        async def run(self):
            request = await self.receive()
            if request:
                print("Request for CPU was received")
                username = utilities.sanitize_sender_name(str(request.sender))
                agents = self.get_users(username)
                if len(agents) < 1:
                    answer_template = templates.receive_cpu_template()
                    msg = templates.make_message(answer_template, to=username)
                    await self.send(msg)
                    print("No agents were found")
                    return
                global cpu_req
                cpu_req[username] = [len(agents), -1.0, '']
                for ag in agents:
                    request_template = templates.receive_cpu_per_template(username)
                    msg = templates.make_message(request_template, to=ag)
                    await self.send(msg)
                print("Requests for CPU were sent to ", agents)
            await asyncio.sleep(1)

    class ReceiveCpuPer(CyclicBehaviour):
        async def run(self):
            request = await self.receive()
            if request:
                global cpu_req
                username, percentage = request.body.split("$$")
                sender_name = utilities.sanitize_sender_name(str(request.sender))
                print("A CPU percentage was received from ", sender_name, " to ", username)
                if username not in cpu_req:
                    return
                request_left, max_cpu_per, max_cpu_user = cpu_req[username]
                percentage = float(percentage)
                if max_cpu_per < percentage:
                    max_cpu_per = percentage
                    max_cpu_user = sender_name
                if request_left == 1:
                    del cpu_req[username]
                    answer_template = templates.receive_cpu_template(max_cpu_user)
                    msg = templates.make_message(answer_template, to=username)
                    await self.send(msg)
                    print("CPU percentage was sent to ", username)
                else:
                    cpu_req[username] = [request_left-1, max_cpu_per, max_cpu_user]
                #return
            await asyncio.sleep(1)
    ################################################################################################################
    # REQUEST FILE LIST
    ################################################################################################################

    class RequestForFilesList(PeriodicBehaviour):
        @staticmethod
        def get_users():
            conn = sqlite3.connect(DB_NAME)
            conn_obj = conn.cursor()
            rows = conn_obj.execute("SELECT * FROM agents").fetchall()
            agents = []
            for row in rows:
                agents.append(row[0])
            conn.close()
            return agents

        async def run(self):
            request_template = templates.file_list_request_template()
            agents = self.get_users()
            for ag in agents:
                msg = templates.make_message(request_template, to=ag)
                await self.send(msg)
                print("Requesting files to ", ag)

        async def on_end(self):
            await self.agent.stop()

        # async def on_start(self):
            # print("Starting behaviour that asks for files lists")

    class WaitForFilesListResponse(CyclicBehaviour):
        @staticmethod
        def update_files(username, files):
            conn = sqlite3.connect(DB_NAME)
            conn_obj = conn.cursor()
            conn_obj.execute("DELETE FROM files_directory where username = '" + username + "'")
            for file in files:
                if not utilities.check_file_name(file):
                    continue
                conn_obj.execute("INSERT INTO files_directory (username, filename, active) VALUES (?, ?, ?)",
                                 (username, file, 1))
            conn.commit()
            conn.close()

        async def run(self):
            answer = await self.receive()
            if answer:
                sender_name = utilities.sanitize_sender_name(str(answer.sender))
                # update files list for this user
                if answer.body is not None:
                    file_list = answer.body.split(',')
                    self.update_files(sender_name, file_list)
                print('Answer received from ', sender_name)
            await asyncio.sleep(1)

    ################################################################################################################
    # JOIN NETWORK
    ################################################################################################################

    class ReceiveJoinRequest(CyclicBehaviour):

        @staticmethod
        def insert_user(username):
            conn = sqlite3.connect(DB_NAME)
            conn_obj = conn.cursor()
            conn_obj.execute("INSERT INTO agents (username, active) VALUES (?, ?)", (username, 1))
            conn.commit()
            conn.close()

        @staticmethod
        def get_users():
            conn = sqlite3.connect(DB_NAME)
            conn_obj = conn.cursor()
            rows = conn_obj.execute("SELECT * FROM agents").fetchall()
            agents = []
            for row in rows:
                agents.append(row[0])
            conn.close()
            return agents

        @staticmethod
        def insert_files(username, files):
            conn = sqlite3.connect(DB_NAME)
            conn_obj = conn.cursor()
            conn_obj.execute("DELETE FROM files_directory where username = '" + username + "'")
            for file in files:
                if not utilities.check_file_name(file):
                    continue
                conn_obj.execute("INSERT INTO files_directory (username, filename, active) VALUES (?, ?, ?)",
                                 (username, file, 1))
            conn.commit()
            conn.close()

        async def run(self):
            request = await self.receive()
            if request:
                sender_name = utilities.sanitize_sender_name(str(request.sender))
                directory = self.get_users()
                if sender_name not in directory:
                    self.insert_user(sender_name)
                    if request.body is not None and len(request.body.split(',')) > 0:
                        file_list = request.body.split(',')
                        self.insert_files(sender_name, file_list)
                    print("Request to join network received from new user ", sender_name)
            await asyncio.sleep(1)

    ################################################################################################################
    # REQUEST FOR FILE
    ################################################################################################################

    class ReceiveRequestForFile(CyclicBehaviour):
        @staticmethod
        def search_for_file(file_name, username) -> list:
            conn = sqlite3.connect(DB_NAME)
            username = utilities.sanitize_sender_name(username)
            conn_obj = conn.cursor()
            conn_obj.execute("SELECT * FROM files_directory where filename = ? and username <> ?",
                             (file_name, username))
            rows = conn_obj.fetchall()
            agents = []
            for row in rows:
                agents.append(row[0])
            conn.close()
            return agents
            # return agentsDirectory

        async def run(self):
            request = await self.receive()
            if request:
                print("Request for a file received")
                file_name = request.body
                agent_list = self.search_for_file(file_name=file_name, username=str(request.sender))
                agent_list = '###'.join(agent_list)
                answer_template = templates.receive_agent_list_template(body=agent_list)
                msg = templates.make_message(answer_template, to=str(request.sender))
                await self.send(msg)
                print("Answer for agent list for a file was sent")
            await asyncio.sleep(1)

    class AddDownloadedFile(CyclicBehaviour):
        @staticmethod
        def insert_file(username, file):
            conn = sqlite3.connect(DB_NAME)
            conn_obj = conn.cursor()
            conn_obj.execute("DELETE FROM files_directory where username = ? and filename = ?", (username, file))

            if utilities.check_file_name(file):
                conn_obj.execute("INSERT INTO files_directory (username, filename, active) VALUES (?, ?, ?)",
                                 (username, file, 1))
            conn.commit()
            conn.close()

        async def run(self):
            request = await self.receive()
            if request:
                file_name = request.body
                sender_name = utilities.sanitize_sender_name(str(request.sender))
                self.insert_file(sender_name, file_name)
            await asyncio.sleep(1)

    async def setup(self):
        print(f"Directory Agent started at {datetime.datetime.now().time()}")

        request_join_template = templates.join_network_template()
        self.add_behaviour(
            behaviour=self.ReceiveJoinRequest(),
            template=request_join_template)

        answer_template = templates.file_list_response_template()
        self.add_behaviour(
            behaviour=DirectoryAgent.WaitForFilesListResponse(),
            template=answer_template
        )

        receive_file_request_template = templates.request_file_agent_list_template()
        self.add_behaviour(behaviour=self.ReceiveRequestForFile(), template=receive_file_request_template)

        start_at = datetime.datetime.now() + datetime.timedelta(seconds=3)
        self.add_behaviour(self.RequestForFilesList(period=60, start_at=start_at))

        update_file_template = templates.update_file_list_template()
        self.add_behaviour(self.AddDownloadedFile(), update_file_template)

        ################################################################################################################
        # REQUEST CPU POWER
        ################################################################################################################
        my_template = templates.request_cpu_template()
        self.add_behaviour(behaviour=self.ReceiveCpuRequest(), template=my_template)

        my_template = templates.response_cpu_per_template()
        self.add_behaviour(behaviour=self.ReceiveCpuPer(), template=my_template)



def connect_database():
    conn = sqlite3.connect(DB_NAME)
    cursor_obj = conn.cursor()
    cursor_obj.execute(
        "CREATE TABLE IF NOT EXISTS agents(username text PRIMARY KEY, active int)")
    cursor_obj.execute(
        "CREATE TABLE IF NOT EXISTS files_directory(username text, filename text, active int)")
    cursor_obj.execute("DELETE FROM agents")
    cursor_obj.execute("DELETE FROM files_directory")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    connect_database()

    directoryAgent = DirectoryAgent(xmpp_user_1, xmpp_pass_1)
    future = directoryAgent.start()
    # sender.web.start(hostname="127.0.0.1", port="10000")
    future.result()

    while directoryAgent.is_alive():
        try:
            time.sleep(2)
        except KeyboardInterrupt:
            directoryAgent.stop()
            break
    print("\nDirectory Agent has finished")
    quit_spade()
