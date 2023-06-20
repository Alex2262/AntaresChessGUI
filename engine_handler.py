
import subprocess
import time
import threading

from game_handler import GameState
from move import get_uci_from_move


class Engine:

    def __init__(self, main_state, engine_file):
        self.main_state = main_state
        self.engine_file = engine_file
        self.stopped = True
        self.info = {
            "name":"",
            "author":"",
            "depth":0,
            "evaluation":0,
            "evaluation_type":"cp",
            "nodes":0,
            "pv":"",
                     }
        self.engine_process = None
        self.thread = None
        self.connection_successful = False

    def write(self, input_text):
        self.engine_process.stdin.write(input_text)
        self.engine_process.stdin.flush()

    def connect(self):
        self.engine_process = subprocess.Popen([self.engine_file], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                          universal_newlines=True)

        self.connection_successful = False

        start_time = time.time()

        self.write("uci\n")

        while True:
            response = self.engine_process.stdout.readline()
            tokens = response.strip().split()
            if len(tokens) >= 3 and tokens[0] == "id":
                if tokens[1] == "name":
                    self.info["name"] = response[8:].strip()
                elif tokens[1] == "author":
                    self.info["author"] = response[10:].strip()

            if response.strip() == "uciok":
                break

            if (time.time() - start_time) * 1000 >= 10000:
                return

        self.write("ucinewgame\n")
        self.write("isready\n")

        while True:
            response = self.engine_process.stdout.readline()
            if response.strip() == "readyok":
                break

            if (time.time() - start_time) * 1000 >= 10000:
                return

        self.connection_successful = True

    def listen(self):

        while True:
            if self.stopped:
                break

            response = self.engine_process.stdout.readline().strip()
            tokens = response.split()

            if len(tokens) < 1:
                continue

            if tokens[0] == "info":
                if "depth" in tokens:
                    depth_index = tokens.index("depth") + 1

                    if len(tokens) > depth_index:
                        self.info["depth"] = int(tokens[depth_index])

                if "score" in tokens:
                    score_index = tokens.index("score") + 2

                    if len(tokens) > score_index:
                        self.info["evaluation"] = int(tokens[score_index])
                        self.info["evaluation_type"] = tokens[score_index - 1]

                if "pv" in tokens:
                    pv_index = tokens.index("pv") + 1

                    if len(tokens) > pv_index:
                        self.info["pv"] = tokens[pv_index]

                if "nodes" in tokens:
                    nodes_index = tokens.index("nodes") + 1

                    if len(tokens) > nodes_index:
                        self.info["nodes"] = int(tokens[nodes_index])

            elif tokens[0] == "bestmove":
                self.stopped = True
                break

    def start_analysis(self):

        if not self.stopped:
            self.stop_analysis()

        fen = self.main_state.fen
        command = "position fen " + fen

        moves = self.main_state.move_archive

        if len(moves) > 0:
            command += " moves"
            for move in moves:
                command += " " + get_uci_from_move(move)

        command += "\n"
        # print(command)

        self.write(command)
        self.write("isready\n")
        self.write("go infinite\n")

        self.stopped = False
        self.thread = threading.Thread(target=self.listen, args=())
        self.thread.start()

    def stop_analysis(self):
        if self.stopped and self.thread is None:
            return

        self.write("stop\n")

        self.stopped = True

        self.thread.join()
        self.thread = None
