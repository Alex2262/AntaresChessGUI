
import subprocess
import time
import threading

from move import get_uci_from_move


class Engine:

    def __init__(self, main_state, engine_file):
        self.main_state = main_state
        self.engine_file = engine_file
        self.stopped = True
        self.hard_stop = False
        self.listen_complete = True

        self.options = {
            "threads":1,
            "hash":64,
            "multi_pv":1
        }

        self.info = {
            "name":"",
            "author":"",
            "depth":0,
            "scores":[0],
            "score_types":["cp"],
            "nodes":0,
            "pvs":[""],
            "bestmove":""
        }

        self.engine_process = None
        self.thread = None
        self.connection_successful = False
        self.analysing = False

    def write(self, input_text):
        try:
            self.engine_process.stdin.write(input_text)
            self.engine_process.stdin.flush()
        except:
            pass

    def set_options(self):
        self.write("setoption name Threads value " + str(self.options["threads"]) + "\n")
        self.write("setoption name Hash value " + str(self.options["hash"]) + "\n")
        self.write("setoption name MultiPV value " + str(self.options["multi_pv"]) + "\n")

    def set_multi_pv(self, new_multi_pv):
        new_multi_pv = max(1, new_multi_pv)

        self.options["multi_pv"] = new_multi_pv
        self.info["pvs"] = [""] * new_multi_pv
        self.info["scores"] = [0] * new_multi_pv
        self.info["score_types"] = ["cp"] * new_multi_pv

        if self.analysing:
            self.stop()
            self.start_analysis()  # will set options
        else:
            self.set_options()

    def set_thread_count(self, new_thread_count):
        new_thread_count = max(1, new_thread_count)

        self.options["threads"] = new_thread_count
        self.options["hash"] = 64 * new_thread_count

        if self.analysing:
            self.stop()
            self.start_analysis()  # will set options
        else:
            self.set_options()

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

        self.listen_complete = False

        while True:

            if self.stopped:
                self.write("stop\n")

            if self.hard_stop:
                break

            response = self.engine_process.stdout.readline().strip()
            tokens = response.split()

            # print(response)

            if len(tokens) < 1:
                continue

            if tokens[0] == "info":
                current_pv = 0

                if "multipv" in tokens:
                    multi_pv_index = tokens.index("multipv") + 1
                    if len(tokens) > multi_pv_index:
                        current_pv = int(tokens[multi_pv_index]) - 1
                    else:
                        current_pv = 0

                if "depth" in tokens:
                    depth_index = tokens.index("depth") + 1

                    if len(tokens) > depth_index:
                        self.info["depth"] = int(tokens[depth_index])

                if "score" in tokens:
                    score_index = tokens.index("score") + 2

                    if len(tokens) > score_index:
                        self.info["scores"][current_pv] = int(tokens[score_index])
                        self.info["score_types"][current_pv] = tokens[score_index - 1]

                if "pv" in tokens:
                    pv_index = tokens.index("pv") + 1
                    self.info["pvs"][current_pv] = ""
                    while pv_index < len(tokens):
                        if len(tokens[pv_index]) < 4:
                            break

                        if not tokens[pv_index][0].isalpha():
                            break
                        if not tokens[pv_index][1].isdigit():
                            break
                        if not tokens[pv_index][0].isalpha():
                            break
                        if not tokens[pv_index][1].isdigit():
                            break

                        self.info["pvs"][current_pv] += tokens[pv_index] + " "

                        pv_index += 1

                if "nodes" in tokens:
                    nodes_index = tokens.index("nodes") + 1

                    if len(tokens) > nodes_index:
                        self.info["nodes"] = int(tokens[nodes_index])

            elif tokens[0] == "bestmove":
                bestmove_index = tokens.index("bestmove") + 1

                if len(tokens) > bestmove_index:
                    self.info["bestmove"] = tokens[bestmove_index]

                self.stopped = True
                break

        self.listen_complete = True

    def start_analysis(self):

        if not self.stopped:
            self.stop()

        self.analysing = True

        self.set_options()

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
        self.info["depth"] = 0
        self.thread = threading.Thread(target=self.listen, args=())
        self.thread.start()

    def stop(self):

        if self.stopped and self.thread is None:
            return

        if not self.stopped:
            self.write("stop\n")

        ping_counts = 0
        while not self.listen_complete:
            time.sleep(0.01)

            ping_counts += 1

            if ping_counts > 1000:  # 10 second wait and no engine response
                self.hard_stop = True

        self.hard_stop = False
        self.stopped = True
        self.analysing = False

        self.thread.join()
        self.thread = None

    def think(self, allocated_time):

        if not self.stopped:
            self.stop()

        fen = self.main_state.fen
        command = "position fen " + fen

        # moves = self.main_state.move_archive

        '''
        if len(moves) > 0:
            command += " moves"
            for move in moves:
                command += " " + get_uci_from_move(move)
        '''

        command += "\n"
        # print(command)

        self.write(command)
        self.write("isready\n")

        self.write("go wtime " + str(allocated_time) + " btime " + str(allocated_time) + "\n")

        self.stopped = False
        self.info["depth"] = 0

        self.listen()


