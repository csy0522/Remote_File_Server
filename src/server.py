# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 21:35:32 2020

@author: CSY
"""

import socket
import os
from datetime import datetime
from datetime import timedelta
import threading
import time
from collections import deque
import select
import argparse
from ipaddress import ip_address
from mar_unmar_shall import __marshall__ as __mar__
from mar_unmar_shall import __unmarshall__ as __unmar__

"""
Everything except for the last three are Strings
CUR == current time
status = the status that will be printed at the end of operation
timeout = timeouts for operations
"""
WALL = "==============="
END_OF_REQUEST = "================ END ================"
HIST_FILE = "Server_Client_History.txt"
CLIENT_FILE = "Clients.txt"
DATA_DIR = "../data/"
CUR = datetime.now()
STATUS = {
    1: "\033[1;32;40mSUCCEEDED\033[0m",
    0: "\033[1;31;40mFAILED\033[0m",
    2: "\033[1;33;40mTIMEOUT\033[0m",
}
TIMEOUT = 60

"""
This Class creates a local file server on the argument specified.
This server gives the access to the clients who know the hostname 
and the port number of this server.
The operations this server providees includes:
    Read, Write, Monitor, Rename, Replace, Create, Erase, Delete, LS, and Disappear
Detailed explanations will be written on top of each functions.
"""
class Server:
    def __init__(self, serv_dir):
        self.serv_dir_ = self.__find_directory__(serv_dir)
        self.port_ = None
        self.socket_ = None
        self.history_ = self.__create_file__(DATA_DIR, HIST_FILE)
        self.client_file_ = self.__create_file__(DATA_DIR, CLIENT_FILE)
        self.client_ = ""
        self.clients_ = deque()
        self.client_req_ = ""
        self.server_msg_ = ""
        self.req_file_ = ""
        self.status_ = 0
        self.time_thread_ = threading.Thread(target=self.__update_time__, daemon=True)
        self.time_thread_.start()

    """
    This operation allows the clients to print 
    a file from offset till the number of bytes specified.
    """
    def __READ__(self, client):
        self.req_file_, offset, b2r = (
            self.__receive__(),
            self.__receive__(int),
            self.__receive__(int),
        )
        if self.status_ == 2 or self.status_ == None:
            return

        print('\n\t{} "{}"\n'.format(self.client_req_, self.req_file_))
        if self.__check_server_directory__(self.req_file_):
            with open(self.serv_dir_ + self.req_file_) as f:
                content = f.read()
                if offset > len(content):
                    self.server_msg_ = (
                        'Your "offset" exceeded the length of file content.\n'
                    )
                elif offset + b2r > len(content):
                    self.server_msg_ = 'Your length of "bytes to read" exceeded the length of file content.\n'
                else:
                    if b2r == -1:
                        b2r = len(content)
                    self.server_msg_ = content[offset : offset + b2r]
                    self.status_ = 1
                f.close()

        self.__send__(self.server_msg_, client)
        self.__send__(self.status_, client)
        if self.status_ == 1:
            self.__send__(len(content), client)

    """
    This operation allows the clients to insert 
    a string starting from the offset.
    """
    def __WRITE__(self, client):
        self.req_file_, offset, b2w = (
            self.__receive__(),
            self.__receive__(int),
            self.__receive__(),
        )
        if self.status_ == 2 or self.status_ == None:
            return

        print('\n\t{} "{}"\n'.format(self.client_req_, self.req_file_))
        if self.__check_server_directory__(self.req_file_):
            with open(self.serv_dir_ + self.req_file_) as f:
                content = f.read()
                if offset > len(content):
                    self.server_msg_ = (
                        '\nYour "offset" exceeded the length of file content\n'
                    )
                else:
                    self.server_msg_ = "%s%s%s" % (
                        content[:offset],
                        b2w,
                        content[offset:],
                    )
                    with open(self.serv_dir_ + self.req_file_, "w") as ff:
                        ff.write(self.server_msg_)
                        ff.close()
                    self.status_ = 1
                f.close()

        self.__send__(self.server_msg_, client)
        self.__send__(self.status_, client)

    """
    This operation allows the clients to "observe" the updates / changes
    made to a specific file during a period of time.
    """
    def __MONITOR__(self, client):
        self.req_file_, mon_time = self.__receive__(), self.__receive__(int)
        if self.status_ == 2 or self.status_ == None:
            return

        print('\n\t{} "{}"\n'.format(self.client_req_, self.req_file_))
        if self.__check_server_directory__(self.req_file_):
            if mon_time < TIMEOUT:
                self.__send__(1, client)

                ori_file = open(self.serv_dir_ + self.req_file_)
                ori_content = ori_file.read()
                ori_file.close()

                monitor_thread_ = threading.Thread(
                    target=self.__monitoring__,
                    args=(self.req_file_, ori_content, mon_time, client),
                )
                monitor_thread_.start()
                self.status_ = 1
            else:
                self.__send__(0, client)
                self.server_msg_ = (
                    "Monitoring time must be smaller than timeout (< %d seconds)"
                    % (TIMEOUT)
                )
                self.__send__(self.server_msg_, client)
        else:
            self.__send__(0, client)
            self.__send__(self.server_msg_, client)

    """
    This is an assistnant function for MONITOR operation.
    It constantly receives the updates / changes of the file specified.
    """
    def __monitoring__(self, file, ori_content, mon_time, client):
        global CUR
        des = datetime.now() + timedelta(seconds=mon_time)
        new_file = None
        while CUR < des:
            time.sleep(0.5)
            try:
                new_file = open(self.serv_dir_ + file)
                new_content = new_file.read()
                new_file.close()
            except FileNotFoundError:
                self.__send__(2, client)
                break
            if ori_content != new_content:
                ori_content = new_content
                self.__send__(1, client)
                self.__send__(ori_content, client)
        if CUR >= des:
            self.__send__(0, client)

    """
    This operation allows the clients to rename
    a file specified.
    """
    def __RENAME__(self, client):
        self.req_file_, new_name = self.__receive__(), self.__receive__()
        if self.status_ == 2 or self.status_ == None:
            return

        print('\n\t{} "{}"\n'.format(self.client_req_, self.req_file_))
        if self.__check_server_directory__(self.req_file_):
            file_type_idx = self.req_file_.rfind(".")
            file_type = self.req_file_[file_type_idx:]
            if new_name[-len(file_type) :] != file_type:
                self.server_msg_ = "\nThe file must be the same type.\n"
            else:
                os.rename(self.serv_dir_ + self.req_file_, self.serv_dir_ + new_name)
                self.status_ = 1
                self.server_msg_ = '"%s" -> "%s"\n' % (self.req_file_, new_name)

        self.__send__(self.server_msg_, client)
        self.__send__(self.status_, client)

    """
    This operation allows the clients to replace
    a part of content with another string specified from the offset.
    """
    def __REPLACE__(self, client):
        self.req_file_, offset, b2w = (
            self.__receive__(),
            self.__receive__(int),
            self.__receive__(),
        )
        if self.status_ == 2 or self.status_ == None:
            return

        print('\n\t{} "{}"\n'.format(self.client_req_, self.req_file_))
        if self.__check_server_directory__(self.req_file_):
            with open(self.serv_dir_ + self.req_file_) as f:
                content = f.read()
                if offset >= len(content):
                    self.server_msg_ = (
                        '\nYour "offset" exceeded the length of file content'
                    )
                else:
                    last_idx = offset + len(b2w)
                    self.server_msg_ = "%s%s%s" % (
                        content[:offset],
                        b2w,
                        content[last_idx:],
                    )
                    with open(self.serv_dir_ + self.req_file_, "w") as ff:
                        ff.write(self.server_msg_)
                        ff.close()
                    self.status_ = 1
                f.close()

        self.__send__(self.server_msg_, client)
        self.__send__(self.status_, client)

    """
    This operation allows the clients to create
    new files in the local server directory.
    """
    def __CREATE__(self, client):
        self.req_file_, content = self.__receive__(), self.__receive__()
        if self.status_ == 2 or self.status_ == None:
            return

        print('\n\t{} "{}"\n'.format(self.client_req_, self.req_file_))

        if not self.__check_server_directory__(self.req_file_):
            self.__send__(0, client)
            file_type_idx = self.req_file_.rfind(".")
            file_type = self.req_file_[file_type_idx:]
            if file_type != ".txt":
                self.server_msg_ = '\nThe file must be in ".txt" type.'
            else:
                new_file = open(self.serv_dir_ + self.req_file_, "w")
                if content != None:
                    new_file.write(content)
                    new_file.close()
                else:
                    new_file.close()
                self.status_ = 1
                self.server_msg_ = '\nFile "%s" Created.' % (self.req_file_)
        else:
            self.__send__(1, client)
            self.__overwrite__(client)

        self.__send__(self.server_msg_, client)
        self.__send__(self.status_, client)

    """
    This is an assistnant function for CREATE % Rename operation.
    It asks the clients if it wants to overwrite an existing file.
    """
    def __overwrite__(self, client):
        self.server_msg_ = (
            'The file "%s" already exists in the server directory.\n\
    Do you want to overwrite it[Y/n]: '
            % (self.req_file_)
        )
        self.__send__(self.server_msg_, client)

        answer = self.__receive__()
        if self.status_ == 2 or self.status_ == None:
            return

        yes = ["", "y", "yes"]
        if answer.lower() in yes:
            content = self.__receive__()
            if self.status_ == 2 or self.status_ == None:
                return
            new_file = open(self.serv_dir_ + self.req_file_, "w")
            if content != None:
                new_file.write(content)
                new_file.close()
            else:
                new_file.close()
            self.status_ = 1
            self.server_msg_ = '\nFile "%s" Created.' % (self.req_file_)
        else:
            self.server_msg_ = '\nFile "%s" Not Created.' % (self.req_file_)

    """
    This operation allows the clients to erase
    a chunk of string starting from the offset to the number of bytes specified.
    """
    def __ERASE__(self, client):
        self.req_file_, offset, b2e = (
            self.__receive__(),
            self.__receive__(int),
            self.__receive__(int),
        )
        if self.status_ == 2 or self.status_ == None:
            return

        print('\n\t{} "{}"\n'.format(self.client_req_, self.req_file_))
        if self.__check_server_directory__(self.req_file_):
            with open(self.serv_dir_ + self.req_file_) as f:
                content = f.read()
                if offset >= len(content):
                    self.server_msg_ = (
                        '\nYour "offset" exceeded the length of file content.\n'
                    )
                elif offset + b2e > len(content):
                    self.server_msg_ = '\nYour length of "bytes to read" exceeded the length of file content.\n'
                else:
                    if b2e == -1:
                        b2e = len(content)
                    self.server_msg_ = "%s%s" % (content[:offset], content[b2e:])
                    with open(self.serv_dir_ + self.req_file_, "w") as ff:
                        ff.write(self.server_msg_)
                        ff.close()
                    self.status_ = 1
                f.close()

        self.__send__(self.server_msg_, client)
        self.__send__(self.status_, client)

    """
    This operation allows the clients to remove
    a file from the local server directory.
    """
    def __DELETE__(self, client):
        self.req_file_ = self.__receive__()
        if self.status_ == 2 or self.status_ == None:
            return

        print('\n\t{} "{}"\n'.format(self.client_req_, self.req_file_))

        if self.__check_server_directory__(self.req_file_):
            os.remove(self.serv_dir_ + self.req_file_)
            self.server_msg_ = '\nFile "%s" removed.' % (self.req_file_)
            self.status_ = 1

        self.__send__(self.server_msg_, client)
        self.__send__(self.status_, client)

    """
    This operation allows the clients to see
    every available files in the local server directory.
    """
    def __LS__(self, client):
        self.server_msg_ = "List all files on Server Directory"
        print("\n\t" + self.server_msg_ + "\n")
        ##        self.req_file_ = "ALL"

        files = "\n" + "==========" + " Server Directory " + "==========" + "\n"
        for c in os.listdir(self.serv_dir_):
            files += "\t" + c + "\n"
        files += END_OF_REQUEST + "\n"
        self.__send__(files, client)
        self.status_ = 1
        self.__send__(self.status_, client)

    """
    This operation allows the clients to remove
    themselves from the "clients list",
    and exit the client program.
    """
    def __DISAPPEAR__(self, client):
        print("\n\t%s from clients list\n" % (self.client_req_))
        self.clients_.remove(client)
        self.status_ = 1
        self.__send__(self.status_, client)

    """
    This function sends msg to client.
    """
    def __send__(self, msg, client):
        if type(msg) != str:
            msg = str(msg)
        bufsize = self.__get_bufsize__(msg)
        self.socket_.sendto(__mar__(bufsize), client)
        self.socket_.sendto(__mar__(msg), client)

    """
    This function receives a message sent by the client.
    An optimal bufsize is received first, and the message is received
    based on the optimal bufsize.
    if timeout, return a specific value for status update.
    """
    def __receive__(self, d=str, c=False):
        timeout = select.select([self.socket_], [], [], TIMEOUT)
        if timeout[0]:
            bufsize, client = self.socket_.recvfrom(12)
            message, client = self.socket_.recvfrom(__unmar__(bufsize, int))
            message = __unmar__(message, d)
            if c:
                return message, client
            return message
        else:
            self.status_ = 2

    """
    This function calculates a optimal bufsize for a message
    to be sent to the clients.
    """
    def __get_bufsize__(self, msg):
        k = 1
        while k < len(msg):
            k = k * 2
        return k

    """
    This function creates a new socket for the server
    and binds the host with a port specified from one of the arguments.
    """
    def __create_socket__(self, port):
        print("Creating UDP socket...")
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        print(
            "Connecting socket to...\n - host: {} \n - Ip: {} \n - port: {}".format(
                socket.gethostname(), socket.gethostbyname(socket.gethostname()), port
            )
        )
        sock.bind((socket.gethostname(), port))
        print("Socket created")
        return sock

    """
    This function creates file in the directory specified.
    It checks if the file exists in the directory, and if
    the file does not exist, it creates the file.
    """
    def __create_file__(self, directory, filename, content=None):
        if self.__file_exist__(directory, filename):
            existing = open(directory + filename)
            existing.close()
            return existing
        else:
            new_file = open(directory + filename, "w")
            if content != None:
                new_file.write(content)
                new_file.close()
            else:
                new_file.close()
                return new_file

    """
    This function checks if a certain file exists
    in the local server directory.
    """
    def __check_server_directory__(self, filename):
        p = False
        if self.__file_exist__(self.serv_dir_, filename):
            p = True
        else:
            self.server_msg_ = (
                'The file "%s" does not exist in the server directory.\n' % (filename)
            )
        return p

    """
    This functions checks if a certain file 
    exists in the directory specified.
    """
    def __file_exist__(self, directory, filename):
        return os.path.isfile(directory + filename)

    """
    This function records the new client who requested
    to do any operation available above.
    """
    def __record_client__(self, client):
        if self.__file_exist__(DATA_DIR, CLIENT_FILE):
            f = open(DATA_DIR + CLIENT_FILE, "r")
            if client + "\n" in f:
                f.close()
            else:
                self.client_file_ = open(DATA_DIR + CLIENT_FILE, "a")
                self.client_file_.write(client + "\n")
                self.client_file_.close()

    """
    This function adds a client to the client list
    that is specifically for one-copy-semantic system.
    """
    def __append_client__(self, client):
        try:
            for c in list(self.clients_):
                if client[0] == c[0]:
                    self.clients_.remove(c)
            self.clients_.appendleft(client)
        except ValueError:
            self.clients_.appendleft(client)

    """
    This function records a history of operations
    requested by the clients.
    It is saved in "data" directory.
    """
    def __record__(self, client):
        self.history_ = open(DATA_DIR + HIST_FILE, "a")
        succ = "Succeeded"
        if self.status_ == 0:
            succ = "Failed"
        elif self.status_ == 2:
            succ = "Timeout"
        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if (
            self.status_ == 2
            or self.client_req_ == "DISAPPEAR"
            or self.client_req_ == "LS"
        ):
            self.history_.write(
                "Client: "
                + client[0]
                + "\tPort: "
                + str(self.port_)
                + "\tRequest: "
                + self.client_req_
                + "\t"
                + succ
                + "\tTime: "
                + curr_time
                + "\n"
            )
        else:
            self.history_.write(
                "Client: "
                + client[0]
                + "\tPort: "
                + str(self.port_)
                + "\tRequest: "
                + self.client_req_
                + ' file "'
                + self.req_file_
                + '" '
                + succ
                + "\tTime: "
                + curr_time
                + "\n"
            )
        self.history_.close()

    """
    This function sets the path that exists to the server directory.
    """
    def __find_directory__(self, dir_list):
        for d in dir_list:
            if os.path.exists(d):
                return d

    """
    This function constantly updates the current time.
    """
    def __update_time__(self):
        global CUR
        while True:
            CUR = datetime.now()
            time.sleep(0.1)

    """
    This function starts the server.
    Since the server is in a while loop,
    it will continuously receive request from any clients.
    """
    def __start__(self):
        while True:
            self.status_ = 0
            print("\nWaiting to receive message...\n")
            try:
                self.client_req_, client = self.__receive__(c=True)
            except TypeError:
                continue
            self.__record_client__(client[0])
            self.__append_client__(client)
            print('Client "%s" requested to:' % (client[0]))
            ##            req = threading.Thread(
            ##                eval("self.__" + self.client_req_ + "__")(client))
            ##            req.start()
            eval("self.__" + self.client_req_ + "__")(client)

            self.server_msg_ = "-------------------- %s --------------------" % (
                STATUS[self.status_]
            )
            print(self.server_msg_)
            self.__record__(client)

    """
    This function gets arguments.
    Since this was designed for a back-up plan,
    it will not be used for this project.
    """
    def __get_args__(self):
        parser = argparse.ArgumentParser(description="Specify Port number.")
        parser.add_argument("port", nargs="?", help="set a port number for the host")
        args = parser.parse_args()
        return args

    """
    This function processes arguments.
    Since this was designed for a back-up plan,
    it will not be used for this project.
    """
    def __process_args__(self, args):
        if args.port == None:
            print("You need to specify the port number.")
            print("Type '--help' for help")
            exit()
        else:
            try:
                args.port = int(args.port)
                self.port_ = args.port
                self.socket_ = self.__create_socket__(self.port_)
            except ValueError:
                print("The value must be integer!")
                print("Please try again!")
                exit()
            except PermissionError:
                print("The port is reserved!")
                print("Please choose a different port number!")
                exit()


"""
MAIN
Before running, please specify:
    - server directory
"""
if __name__ == "__main__":

    """
    Since the server directory changes every time the PCs are switched,
    this list contains all the potential server directories
    and it will automatically set one that exists to
    the server directory.
    """
    server_directories = []

    """Server Directory in Linux Machine"""
    linux_machine_directory = (
        "./../Server_Directory/"
    )

    """Server Directory in Windows Machine"""
    windows_machine_directory = (
        r"C:\Users\CSY\Desktop\Spring 2020\git\Remote_File_Server\Server_Directory\\"
    )

    """Put a potential Server Directory below ... """

    """Adding all the potential server directories to the list"""
    server_directories.append(linux_machine_directory)
    server_directories.append(windows_machine_directory)

    server = Server(server_directories)

    server.__process_args__(server.__get_args__())

    server.__start__()
