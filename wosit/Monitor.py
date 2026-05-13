import os
import time
from threading import Thread
from multiprocessing import Queue

import socket


class ClientSocket:
    
    def __init__(self, sock_type, address):
        self.__sock_type = sock_type
        self.__address = address

    
    def send(self, data):
        """
        Connect to socket and send data.
        """
        with socket.socket(self.__sock_type, socket.SOCK_STREAM) as sock:
            sock.connect(self.__address)
            sock.sendall(data)


class Monitor:
    def __init__(self, stages):

        # self.__sock_type = socket.AF_INET # Make it also work with AF_UNIX for supported systems
        # self.__sock_addr = ("127.0.0.1", 6776)
        self.__sock_type = socket.AF_UNIX
        self.__sock_addr = ("/tmp/wosit_socket")

        self.__sock = self.__sock = socket.socket(self.__sock_type, socket.SOCK_STREAM)

        self.__notif_q = Queue()

        self.__tasks_dict = self.__buildGraphDict(stages=stages)
        self.__findParents(self.__tasks_dict)

        # Bind monitor queue to tasks
        for id, tdct in self.__tasks_dict.items():
            task = tdct["task"]
            task.addMonitor(ClientSocket(sock_type=self.__sock_type, address=self.__sock_addr))
            task.quiet = True

        self.__completed = {}
        self.__tot_nb = len(self.__tasks_dict)

        self.__running = True

        self.__pollingThread = Thread(target=self.__pollThread, args=(self.__sock,))
        self.__pollingThread.start()



    def __buildGraphDict(self, stages):
        graph_dct = {}
        for lvl, stage in stages.items():
            for t in stage:
                task_id = t.getId()
                graph_dct[task_id] = {
                    "id": task_id,
                    "level": lvl,
                    "name": t.getName(),
                    "children_ids": t.getChildrenIds(),
                    "task": t
                }

        return graph_dct
    

    # def getNotifyQueue(self):
    #     return self.__notif_q


    def __findParents(self, graph_dict):
        # For each task in graph
        for id, task in graph_dict.items():
            found_parents = []
            
            # Parse all tasks in graph to find parent / child relation
            for t_id, t_task in graph_dict.items():
                if id in t_task["children_ids"]:
                    found_parents.append(t_id)

            task["parents_ids"] = found_parents


    
    def __pollThread(self, sock):
        # self.__sock = socket.socket(self.__sock_type, socket.SOCK_STREAM)
        with sock:
            sock.bind(self.__sock_addr)
            sock.listen()

            while self.__running:
                try:
                    conn, addr = sock.accept()
                    with conn:
                        data = conn.recv(1024)
                        if data:
                            tid = int.from_bytes(data, byteorder='little')
                            self.__readNotifications(tid=tid)
                except OSError:
                    pass



    def close(self):
        self.__running = False
        self.__sock.shutdown(socket.SHUT_RDWR)
        self.__sock.close()
        self.__pollingThread.join()


    def __readNotifications(self, tid):
        # while not self.__notif_q.empty():
        #     tid  = self.__notif_q.get()
        if tid is None:
            return

        # Insert update code here
        if not tid in self.__tasks_dict:
            raise ValueError(f"Oh no! Task id \"{tid}\" has been lost somewhere!")
        
        task = self.__tasks_dict[tid]
        exec_status = task["task"].getExecStatus()

        if exec_status is not None or True:
            self.__completed[tid] = task


            self.displayCmakeStyle(
                taskname = task["name"],
                exec_status = exec_status,
                nb_completed = len(self.__completed),
                total = self.__tot_nb
            )

            # Insert code to update all tasks here
    
    

    def displayCmakeStyle(self, taskname, exec_status, nb_completed, total):
        percentage = int(nb_completed*100 / total)
        print(f"""[{percentage:3}%] \033[92m{taskname}\033[0m""")


    def __del__(self):
        if self.__sock_type == socket.AF_UNIX:
            if os.path.exists(self.__sock_addr):
                os.remove(self.__sock_addr)