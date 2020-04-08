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
from mar_unmar_shall import __marshall__ as __mar__
from mar_unmar_shall import __unmarshall__ as __unmar__

'''
Everything except for the last three are Strings
CUR == current time
status = the status that will be printed at the end of operation
timeout = timeouts for operations
'''
WALL = "==============="
END_OF_REQUEST = "================ END ================"
HIST_FILE = "Server_Client_History.txt"
CLIENT_FILE = "Clients.txt"
DATA_DIR = "../data/"
CUR = datetime.now()
STATUS={1:"\033[1;32;40mSUCCEEDED\033[0m",
        0: "\033[1;31;40mFAILED\033[0m",
        2: "\033[1;33;40mTIMEOUT\033[0m"}
TIMEOUT = 10

'''
This Class creates a local file server on the argument specified.
This server gives the access to the clients who know the hostname 
and the port number of this server.
The operations this server providees includes:
    Read, Write, Monitor, Rename, Replace, Create, Erase, Delete, LS, and Disappear
Detailed explanations will be written on top of each functions.
'''
class Server():
    
    def __init__(self, host,port,serv_dir):
        self.host_ = host
        self.port_ = port
        self.serv_dir_ = serv_dir
        self.socket_ = self.__create_socket__(self.host_, self.port_)
        self.history_ = self.__create_file__(DATA_DIR,HIST_FILE)
        self.client_file_ = self.__create_file__(DATA_DIR,CLIENT_FILE)
        self.client_ = ""
        self.clients_ = deque()
        self.client_req_ = ""
        self.server_msg_ = ""
        self.req_file_ = ""
        self.status_ = 0
        self.time_thread_ = threading.Thread(target=self.__update_time__,daemon=True)
        self.time_thread_.start()

    


    '''
    This operation allows the clients to print 
    a file from offset till the number of bytes specified.
    '''
    def __READ__(self):
        self.req_file_,offset,b2r = self.__receive__(),self.__receive__(),self.__receive__()
        if self.status_ == 2 or self.status_ == None: return

        print("\n\t{} \"{}\"\n".format(
            __unmar__(self.client_req_),__unmar__(self.req_file_)))
        if self.__check_server_directory__(self.req_file_):
            with open(
                self.serv_dir_ + __unmar__(self.req_file_)) as f:
                content = f.read()
                if int(__unmar__(offset,int)) > len(content):
                    self.server_msg_ = "Your \"offset\" exceeded the length of file content.\n"
                elif __unmar__(offset,int) + __unmar__(b2r,int) > len(content):
                    self.server_msg_ = "Your length of \"bytes to read\" exceeded the length of file content.\n"
                else:
                    if __unmar__(b2r,int) == -1:
                        b2r = __mar__(len(content)-__unmar__(offset,int))
                    self.server_msg_ = content[__unmar__(offset,int):
                                  __unmar__(offset,int) + 
                                  __unmar__(b2r,int)]
                    self.status_ = 1
                f.close()
                
        self.__send__(self.server_msg_)
        self.__send__(self.status_)
        



        
    '''
    This operation allows the clients to insert 
    a string starting from the offset.
    '''
    def __WRITE__(self):
        self.req_file_,offset,b2w = self.__receive__(),self.__receive__(),self.__receive__()
        if self.status_ == 2 or self.status_ == None: return

        print("\n\t{} \"{}\"\n".format(
            __unmar__(self.client_req_),__unmar__(self.req_file_)))
        if self.__check_server_directory__(self.req_file_):
            with open(
                    self.serv_dir_+__unmar__(self.req_file_)) as f:
                content = f.read()
                if __unmar__(offset,int) > len(content):
                    self.server_msg_ = "\nYour \"offset\" exceeded the length of file content\n"
                else:
                    self.server_msg_ = "\nServer File: \n%s%s%s" % (
                        content[:__unmar__(offset, int)],
                        __unmar__(b2w),
                        content[__unmar__(offset, int):])
                    with open(
                            self.serv_dir_+__unmar__(self.req_file_), 'w') as ff:
                        ff.write(self.server_msg_)
                        ff.close()
                    self.status_ = 1
                f.close()
                
        self.__send__(self.server_msg_)
        self.__send__(self.status_)
                
        if self.status_ == 1:
            self.__one_copy_semantics__(
                __unmar__(self.req_file_),
                __unmar__(offset,int),
                __unmar__(b2w))
            


            
    '''
    This operation allows the clients to "observe" the updates / changes
    made to a specific file during a period of time.
    '''
    def __MONITOR__(self):
        self.req_file_,mon_time = self.__receive__(),self.__receive__()
        if self.status_ == 2 or self.status_ == None: return

        print("\n\t{} \"{}\"\n".format(
            __unmar__(self.client_req_),__unmar__(self.req_file_)))
        if self.__check_server_directory__(self.req_file_):
            
            now = datetime.now()
            des = now + timedelta(seconds=__unmar__(mon_time, int))
    
            ori_file = open(self.serv_dir_+__unmar__(self.req_file_))
            ori_content = ori_file.read()
            ori_file.close()
            
            monitor_thread_ = threading.Thread(target=self.__monitoring__,
                                            args=(self.req_file_,ori_content,des))
            monitor_thread_.start()
            self.status_ = 1

    '''
    This is an assistnant function for MONITOR operation.
    It constantly receives the updates / changes of the file specified.
    '''
    def __monitoring__(self,filename,ori_content,des):
        global CUR
        self.server_msg_ = "\nMonitoring...\n"
        self.__send__(self.server_msg_)
        while CUR < des:
            new_file = open(
                self.serv_dir_+__unmar__(filename))
            new_content = new_file.read()
            if ori_content != new_content:
                self.__send__(1)
                self.server_msg_ = "File \"%s\" Updated.\n" % (
                    __unmar__(filename))
                self.__send__(self.server_msg_)
                self.server_msg_ = "Updated Content: \n%s" % (
                    new_content)
                self.__send__(self.server_msg_)
                ori_content = new_content
            new_file.close()
        self.__send__(0)
        self.server_msg_ = "...End of Monitoring.\n"
        self.__send__(self.server_msg_)
            


        
    '''
    This operation allows the clients to rename
    a file specified.
    '''
    def __RENAME__(self):
        self.req_file_,new_name = self.__receive__(),self.__receive__()
        if self.status_ == 2 or self.status_ == None: return

        print("\n\t{} \"{}\"\n".format(
            __unmar__(self.client_req_),__unmar__(self.req_file_)))
        if self.__check_server_directory__(self.req_file_):
            file_type_idx = __unmar__(self.req_file_).rfind('.')
            file_type = __unmar__(self.req_file_)[file_type_idx:]
            if __unmar__(new_name)[-len(file_type):] != file_type:
                self.server_msg_ = "\nThe file must be the same type.\n"
            else:
                os.rename(
                    self.serv_dir_+__unmar__(self.req_file_),
                    self.serv_dir_+__unmar__(new_name))
                self.status_ = 1
                self.server_msg_ = "\"%s\" -> \"%s\"\n" % (
                    __unmar__(self.req_file_),__unmar__(new_name))
                
        self.__send__(self.server_msg_)
        self.__send__(self.status_)
        
        if self.status_ == 1:
            self.__one_copy_semantics__(
                __unmar__(self.req_file_),
                __unmar__(new_name))
            
        
    '''
    This operation allows the clients to replace
    a part of content with another string specified from the offset.
    '''
    def __REPLACE__(self):
        self.req_file_,offset,b2w = self.__receive__(),self.__receive__(),self.__receive__()
        if self.status_ == 2 or self.status_ == None: return

        print("\n\t{} \"{}\"\n".format(
            __unmar__(self.client_req_),__unmar__(self.req_file_)))
        if self.__check_server_directory__(self.req_file_):
            with open(
                    self.serv_dir_+__unmar__(self.req_file_)) as f:
                content = f.read()
                if __unmar__(offset, int) >= len(content):
                    self.server_msg_ = "\nYour \"offset\" exceeded the length of file content"
                else:
                    last_idx = __unmar__(offset,int)+len(
                        __unmar__(b2w))
                    self.server_msg_ = "\nServer File: \n%s%s%s" % (
                        content[:__unmar__(offset, int)],
                        __unmar__(b2w),
                        content[last_idx:])
                    with open(
                            self.serv_dir_+__unmar__(self.req_file_), 'w') as ff:
                        ff.write(self.server_msg_)
                        ff.close()
                    self.status_ = 1
                f.close()
                
        self.__send__(self.server_msg_)
        self.__send__(self.status_)
        
        if self.status_ == 1:
            self.__one_copy_semantics__(
                __unmar__(self.req_file_),
                __unmar__(offset,int),
                __unmar__(b2w))

        
    '''
    This operation allows the clients to create
    new files in the local server directory.
    '''
    def __CREATE__(self):
        self.req_file_,content = self.__receive__(),self.__receive__()
        if self.status_ == 2 or self.status_ == None: return

        print("\n\t{} \"{}\"\n".format(
            __unmar__(self.client_req_),__unmar__(self.req_file_)))
        
        if not self.__check_server_directory__(self.req_file_):
            self.__send__(0)
            file_type_idx = __unmar__(self.req_file_).rfind('.')
            file_type = __unmar__(self.req_file_)[file_type_idx:]
            if file_type != ".txt":
                self.server_msg_ = "\nThe file must be in \".txt\" type."
            else:
                new_file = open(self.serv_dir_+__unmar__(self.req_file_), 'w')
                if __unmar__(content) != None:
                    new_file.write(__unmar__(content))
                    new_file.close()
                else:
                    new_file.close()
                self.status_ = 1
                self.server_msg_ = "\nFile \"%s\" Created." % (__unmar__(self.req_file_))
        else:
            self.__send__(1)
            self.__overwrite__()
            
        self.__send__(self.server_msg_)
        self.__send__(self.status_)

            
    '''
    This is an assistnant function for CREATE % Rename operation.
    It asks the clients if it wants to overwrite an existing file.
    '''
    def __overwrite__(self):
        self.server_msg_ = "The file \"%s\" already exists in the server directory.\n\
    Do you want to overwrite it[Y/n]: " % (__unmar__(self.req_file_))
        self.__send__(self.server_msg_)
        
        answer = self.__receive__()
        if self.status_ == 2 or self.status_ == None: return
        
        if __unmar__(answer) == ""\
        or __unmar__(answer).lower() == 'y'\
        or __unmar__(answer).lower() == 'yes':
            content = self.__receive__()
            if self.status_ == 2 or self.status_ == None: return
            new_file = open(self.serv_dir_+__unmar__(self.req_file_), 'w')
            if __unmar__(content) != None:
                new_file.write(__unmar__(content))
                new_file.close()
            else:
                new_file.close()
            self.status_ = 1
            self.server_msg_ = "\nFile \"%s\" Created." % (__unmar__(self.req_file_))
        else:
            self.server_msg_ = "\nFile \"%s\" Not Created." % (__unmar__(self.req_file_))

            
        
    '''
    This operation allows the clients to erase
    a chunk of string starting from the offset to the number of bytes specified.
    '''
    def __ERASE__(self):
        self.req_file_,offset,b2e = self.__receive__(),self.__receive__(),self.__receive__()
        if self.status_ == 2 or self.status_ == None: return
        
        print("\n\t{} \"{}\"\n".format(
            __unmar__(self.client_req_),__unmar__(self.req_file_)))
        if self.__check_server_directory__(self.req_file_):
            with open(
                    self.serv_dir_+__unmar__(self.req_file_)) as f:
                content = f.read()
                if int(__unmar__(offset,int)) >= len(content):
                    self.server_msg_ = "\nYour \"offset\" exceeded the length of file content.\n"
               
                elif __unmar__(offset,int) + __unmar__(b2e,int) > len(content):
                    self.server_msg_ = "\nYour length of \"bytes to read\" exceeded the length of file content.\n"
                
                else:
                    if __unmar__(b2e,int) == -1:
                        b2e = __mar__(len(content))
                    self.server_msg_ = "\nServer File: \n%s%s" % (
                        content[:__unmar__(offset,int)] + \
                        content[__unmar__(b2e,int):])
                    with open(
                            self.serv_dir_+__unmar__(self.req_file_), 'w') as ff:
                        ff.write(self.server_msg_)
                        ff.close()
                    self.status_ = 1
                f.close()
                
        self.__send__(self.server_msg_)
        self.__send__(self.status_)
            
        if self.status_ == 1:
            self.__one_copy_semantics__(
                __unmar__(self.req_file_),
                __unmar__(offset,int),
                __unmar__(b2e))
        
    
    '''
    This operation allows the clients to remove
    a file from the local server directory.
    '''
    def __DELETE__(self):
        self.req_file_ = self.__receive__()
        if self.status_ == 2 or self.status_ == None: return
        
        print("\n\t{} \"{}\"\n".format(
            __unmar__(self.client_req_),__unmar__(self.req_file_)))

        if self.__check_server_directory__(self.req_file_):
            os.remove(
                self.serv_dir_+__unmar__(self.req_file_))
            self.server_msg_ = "\nFile \"%s\" removed." % (
                __unmar__(self.req_file_))
            self.status_ = 1
            
        self.__send__(self.server_msg_)
        self.__send__(self.status_)
        

    '''
    This operation allows the clients to see
    every available files in the local server directory.
    '''
    def __LS__(self):
        self.server_msg_ = "List all files on Server Directory"
        print('\n\t' + self.server_msg_ + '\n')
        self.req_file_ = __mar__("ALL")

        files = '\n' + "==========" + " Server Directory " + "==========" + '\n'
        for c in os.listdir(self.serv_dir_):
            files += '\t'+c+'\n'
        files += END_OF_REQUEST + '\n'
        self.__send__(files)
        self.status_ = 1
        self.__send__(self.status_)
    
    
    
    '''
    This operation allows the clients to remove
    themselves from the "clients list",
    and exit the client program.
    '''
    def __DISAPPEAR__(self):
        print("\n\t%s from clients list\n" % (__unmar__(self.client_req_)))
        self.clients_.remove(self.client_)
        self.status_ = 1
        self.__send__(self.status_)





    '''
    This function updates the file that exists
    in cache of all the clients.
    It is executed when one file is updated through any client.
    '''
    def __one_copy_semantics__(self,filename,arg1,arg2=None):
        messages = [filename]
        if arg2 == None:
            messages.append(arg1)
        else:
            messages.append(str(arg1))
            messages.append(str(arg2))
        if len(self.clients_) > 1:
            for cli in list(self.clients_)[1:]:
                for msg in messages:
                    bufsize = self.__get_bufsize__(msg)
                    self.socket_.sendto(__mar__(bufsize),cli)
                    self.socket_.sendto(__mar__(msg),cli)
 
    
    
    '''
    This function sends msg to client.
    '''
    def __send__(self,msg):
        if type(msg) != str:
            msg = str(msg)
        bufsize = self.__get_bufsize__(msg)
        self.socket_.sendto(__mar__(bufsize),self.client_)
        self.socket_.sendto(__mar__(msg),self.client_)


    '''
    This function receives a message sent by the client.
    An optimal bufsize is received first, and the message is received
    based on the optimal bufsize.
    if timeout, return a specific value for status update.
    '''
    def __receive__(self):
        timeout = select.select([self.socket_],[],[],TIMEOUT)
        if timeout[0]:
            bufsize,self.client_ = self.socket_.recvfrom(12)
            msg,self.client_ = self.socket_.recvfrom(__unmar__(bufsize,int))
            return msg
        else:
            self.status_ = 2

    
    '''
    This function calculates a optimal bufsize for a message
    to be sent to the clients.
    '''
    def __get_bufsize__(self,msg):
        k = 1
        while k < len(msg):
            k = k * 2
        return k
    
    
    '''
    This function creates a new socket for the server
    and binds the host with a port specified from one of the arguments.
    '''
    def __create_socket__(self, host, port):
        print("Creating UDP socket...")
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        print("Connecting socket to...\n - host: {} \n - port {}".format(host,port))
        sock.bind((host, port))
        print("Socket created")
        return sock
    
    
    '''
    This function creates file in the directory specified.
    It checks if the file exists in the directory, and if
    the file does not exist, it creates the file.
    '''
    def __create_file__(self,directory,filename,content=None):
        if self.__file_exist__(directory,filename):
            existing = open(directory+filename)
            existing.close()
            return existing
        else:
            new_file = open(directory+filename, 'w')
            if content != None:
                new_file.write(content)
                new_file.close()
            else:
                new_file.close()
                return new_file
            
            
    '''
    This function checks if a certain file exists
    in the local server directory.
    '''
    def __check_server_directory__(self,filename):
        p = False
        if self.__file_exist__(self.serv_dir_,__unmar__(filename)):
            p = True
        else:
            self.server_msg_ = "\nThe file \"%s\" does not exist in the server directory.\n" % (
                __unmar__(filename))
        return p
            
    
    '''
    This functions checks if a certain file 
    exists in the directory specified.
    '''
    def __file_exist__(self,directory,filename):
        return os.path.isfile(directory+filename)
            
    
    
    '''
    This function records the new client who requested
    to do any operation available above.
    '''
    def __record_client__(self,client):
        if self.__file_exist__(DATA_DIR,CLIENT_FILE):
            f = open(DATA_DIR+CLIENT_FILE,'r')
            if client+'\n' in f:
                f.close()
            else:
                self.client_file_ = open(DATA_DIR+CLIENT_FILE,'a')
                self.client_file_.write(client+'\n')
                self.client_file_.close()
        
        
        
    '''
    This function adds a client to the client list
    that is specifically for one-copy-semantic system.
    '''
    def __append_client__(self,client):
        try:
            self.clients_.remove(client)
            self.clients_.appendleft(client)
        except ValueError:
            self.clients_.appendleft(client)

    '''
    This function records a history of operations
    requested by the clients.
    It is saved in "data" directory.
    '''
    def __record__(self):
        self.history_ = open(DATA_DIR+HIST_FILE,'a')
        succ = 'Succeeded'
        if self.status_ == 0:
            succ = 'Failed'
        elif self.status_ == 2:
            succ = 'Timeout'
        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.status_ == 2 or __unmar__(self.client_req_) == "DISAPPEAR":
            self.history_.write("Client: " + 
            self.client_[0] + "\tPort: " +
            str(self.port_) + "\tRequest: " + 
            __unmar__(self.client_req_) +
            '\t' + succ + "\tTime: " + curr_time + "\n")
        else:
            self.history_.write("Client: " + 
                self.client_[0] + "\tPort: " +
                str(self.port_) + "\tRequest: " + 
                __unmar__(self.client_req_) +
                " file \"" + __unmar__(self.req_file_) + "\" " + 
                succ + "\tTime: " + curr_time + "\n")
        self.history_.close()
        
        
    '''
    This function constantly updates the current time.
    '''
    def __update_time__(self):
        global CUR
        while True:
            CUR = datetime.now()
            time.sleep(0.2)



    '''
    This function starts the server.
    Since the server is in a while loop,
    it will continuously receive request from any clients.
    '''
    def __start__(self):
        
        global CUR
        while True:
            self.status_ = 0
            print("\nWaiting to receive message...\n")
            self.client_req_ = self.__receive__()
            if self.client_req_ == None: continue
            self.__record_client__(self.client_[0])
            self.__append_client__(self.client_)
            print("Client \"%s\" requested to:" % (self.client_[0]))
            req = threading.Thread(
                eval("self.__" + __unmar__(self.client_req_) + "__")())
            req.start()

            self.server_msg_ = ("-------------------- %s --------------------" % (
                STATUS[self.status_]))
            print(self.server_msg_)
            self.__record__()



'''
Before running, please specify:
    1. hostname
    2. port number
    3. server directory
'''
if __name__ == "__main__":
    hostname = socket.gethostname()
    port_number = 9999
    server_directory = "/home/csy/Documents/git/Remote_File_Server/Server_Directory/"
    
    serv = Server(hostname,port_number,server_directory)

    serv.__start__()
    
