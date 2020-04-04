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
TIMEOUT = 60

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
        self.client_ = ""
        self.clients_ = deque()
        self.client_req_ = ""
        self.server_msg_ = ""
        self.req_file_ = ""
        self.status_ = 0
        self.history_ = self.__create_file__(DATA_DIR,HIST_FILE)
        self.client_file_ = self.__create_file__(DATA_DIR,CLIENT_FILE)
        self.time_thread_ = threading.Thread(target=self.__update_time__,daemon=True)
        self.time_thread_.start()
        

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
            bufsize,self.client_ = self.socket_.recvfrom(12)
            self.client_req_,self.client_ = self.socket_.recvfrom(__unmar__(bufsize,int))

            self.__record_client__(self.client_[0])
            self.__append_client__(self.client_)
            print("Client \"%s\" requested to:" % (self.client_[0]))
            
            req = threading.Thread(
                target = eval("self.__" + __unmar__(self.client_req_) + "__")())
            req.start()

            self.server_msg_ = ("-------------------- %s --------------------" % (
                STATUS[self.status_]))
            print(self.server_msg_)
            self.__record__()


    '''
    
    '''
    def __READ__(self):
        self.req_file_ = self.__receive__()
        if self.status_ == 2: return
        print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                     __unmar__(self.req_file_)))
        if self.__check_server_directory__(self.req_file_):
            self.server_msg_ = "\nYou requested to:\n\n%s %s %s\n\tfile: %s" % (
                WALL,
                __unmar__(self.client_req_),
                WALL,
                __unmar__(self.req_file_))
            self.__send__(self.server_msg_)
            
            offset = self.__receive__()
            if self.status_ == 2: return
            b2r = self.__receive__()
            if self.status_ == 2: return
        
            self.server_msg_ = "\tOffset: {}".format(__unmar__(offset))
            self.__send__(self.server_msg_)
            
            self.server_msg_ = "\tTotal bytes to read: {}\n{}\n".format(
                __unmar__(b2r,int),
                END_OF_REQUEST)
            self.__send__(self.server_msg_)
            
            with open(
                    self.serv_dir_+__unmar__(self.req_file_)) as f:
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
            self.__send__(str(self.status_))
        
        
    def __WRITE__(self):
        cache = self.__receive__()
        if self.status_ == 2: return
        if __unmar__(cache,int) == 0:
            self.req_file_ = self.__receive__()
            if self.status_ == 2: return
            print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                     __unmar__(self.req_file_)))
            offset = self.__receive__()
            if self.status_ == 2: return
            b2w = self.__receive__()
            if self.status_ == 2: return
            with open(
                self.serv_dir_+__unmar__(self.req_file_)) as f:
                content = f.read()
                f.close()
            self.server_msg_ = "%s%s%s" % (
                content[:__unmar__(offset, int)],
                __unmar__(b2w),
                content[__unmar__(offset, int):])
            with open(
                self.serv_dir_+__unmar__(self.req_file_), 'w') as ff:
                ff.write(self.server_msg_)
                ff.close()
            self.server_msg_ = "File \"%s\" in server_directory updated through client cache.\n" % (
                __unmar__(self.req_file_))
            self.__send__(self.server_msg_)
            self.status_ = 1
        else:
            self.req_file_ = self.__receive__()
            if self.status_ == 2: return
            print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                         __unmar__(self.req_file_)))
            if self.__check_server_directory__(self.req_file_):
    
                self.server_msg_ = "\nYou requested to:\n\n%s %s %s\n\tfile: %s" % (
                    WALL,
                    __unmar__(self.client_req_),
                    WALL,
                    __unmar__(self.req_file_))
                self.__send__(self.server_msg_)
                
                offset = self.__receive__()
                if self.status_ == 2: return
                b2w = self.__receive__()
                if self.status_ == 2: return
                
                self.server_msg_ = "\tOffset: {}".format(__unmar__(offset, int))
                self.__send__(self.server_msg_)
                
                self.server_msg_ = "\tSequence of bytes to write: %s\n%s\n" % (
                    __unmar__(b2w),
                    END_OF_REQUEST)
                self.__send__(self.server_msg_)
    
                with open(
                        self.serv_dir_+__unmar__(self.req_file_)) as f:
                    content = f.read()
                    if __unmar__(offset,int) > len(content):
                        self.server_msg_ = "Your \"offset\" exceeded the length of file content\n"
                    else:
                        self.server_msg_ = "%s%s%s" % (
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
                self.__send__(str(self.status_))
        if self.status_ == 1:
            self.__one_copy_semantics__(
                __unmar__(self.req_file_),
                __unmar__(offset,int),
                __unmar__(b2w))
            
    
    def __MONITOR__(self):
        self.req_file_ = self.__receive__()
        if self.status_ == 2: return
        print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                     __unmar__(self.req_file_)))
        if self.__check_server_directory__(self.req_file_):
    
            self.server_msg_ = "\nYou requested to:\n\n%s %s %s\n\tfile: %s" % (
                WALL,
                __unmar__(self.client_req_),
                WALL,
                __unmar__(self.req_file_))
            self.__send__(self.server_msg_)
    
            length = self.__receive__()
            if self.status_ == 2: return
    
            self.server_msg_ = "\tMonitoring Length: {}".format(
                __unmar__(length, int))
            self.__send__(self.server_msg_)
    
            now = datetime.now()
            des = now + timedelta(seconds=__unmar__(length, int))
            
            self.server_msg_ = "\tMonitoring Start Time: %s" % (
                str(now.time()))
            self.__send__(self.server_msg_)
            self.server_msg_ = "\tMonitoring End Time: %s\n%s\n" % (
                str(des.time()),
                END_OF_REQUEST)
            self.__send__(self.server_msg_)
    
            ori_file = open(self.serv_dir_+__unmar__(self.req_file_))
            ori_content = ori_file.read()
            ori_file.close()
            
            self.server_msg_ = "\nMonitoring...\n"
            self.__send__(self.server_msg_)
            
            monitor_thread_ = threading.Thread(target=self.__monitoring__,
                                            args=(self.req_file_,ori_content,des))
            monitor_thread_.start()
            
            self.status_ = 1

        
    def __monitoring__(self,filename,ori_content,des):
        global CUR
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
            
        
    def __RENAME__(self):
        cache = self.__receive__()
        if self.status_ == 2: return
        if __unmar__(cache,int) == 0:
            self.req_file_ = self.__receive__()
            if self.status_ == 2: return
            print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                     __unmar__(self.req_file_)))
            name = self.__receive__()
            if self.status_ == 2: return
            os.rename(
                self.serv_dir_+__unmar__(self.req_file_),
                self.serv_dir_+__unmar__(name))
            self.server_msg_ = "File \"%s\" in server_directory updated through client cache.\n" % (
                __unmar__(self.req_file_))
            self.__send__(self.server_msg_)
            self.status_ = 1
        else:
            self.req_file_ = self.__receive__()
            if self.status_ == 2: return
            print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                         __unmar__(self.req_file_)))
            if self.__check_server_directory__(self.req_file_):
        
                self.server_msg_ = "\nYou requested to:\n\n%s %s %s\n\tfile: %s" % (
                    WALL,
                    __unmar__(self.client_req_),
                    WALL,
                    __unmar__(self.req_file_))
                self.__send__(self.server_msg_)
                
                name = self.__receive__()
                if self.status_ == 2: return
                
                self.server_msg_ = "\tChange the file name to: %s\n%s\n" % (
                    __unmar__(name),
                    END_OF_REQUEST)
                self.__send__(self.server_msg_)
        
                file_type_idx = __unmar__(self.req_file_).rfind('.')
                file_type = __unmar__(self.req_file_)[file_type_idx:]
                
                if __unmar__(name)[-len(file_type):] != file_type:
                    self.server_msg_ = "The file must be the same type.\n"
                else:
                    os.rename(
                        self.serv_dir_+__unmar__(self.req_file_),
                        self.serv_dir_+__unmar__(name))
                    self.status_ = 1
                    self.server_msg_ = "\"%s\" -> \"%s\"\n" % (
                        __unmar__(self.req_file_),__unmar__(name))
                self.__send__(self.server_msg_)
                self.__send__(str(self.status_))
        if self.status_ == 1:
            self.__one_copy_semantics__(
                __unmar__(self.req_file_),
                __unmar__(name))
        
    
    def __REPLACE__(self):
        cache = self.__receive__()
        if self.status_ == 2: return
        if __unmar__(cache,int) == 0:
            self.req_file_ = self.__receive__()
            if self.status_ == 2: return
            print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                     __unmar__(self.req_file_)))
            offset = self.__receive__()
            if self.status_ == 2: return
            b2w = self.__receive__()
            if self.status_ == 2: return
            with open(
                self.serv_dir_+__unmar__(self.req_file_)) as f:
                content = f.read()
                f.close()
            self.server_msg_ = "%s%s%s" % (
                content[:__unmar__(offset, int)],
                __unmar__(b2w),
                content[__unmar__(offset, int)+len(__unmar__(b2w)):])
            with open(
                self.serv_dir_+__unmar__(self.req_file_), 'w') as ff:
                ff.write(self.server_msg_)
                ff.close()
            self.server_msg_ = "File \"%s\" in server_directory updated through client cache.\n" % (
                __unmar__(self.req_file_))
            self.__send__(self.server_msg_)
            self.status_ = 1
        else:
            self.req_file_ = self.__receive__()
            if self.status_ == 2: return
            print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                         __unmar__(self.req_file_)))
            if self.__check_server_directory__(self.req_file_):
        
                self.server_msg_ = "\nYou requested to:\n\n%s %s %s\n\tfile: %s" % (
                    WALL,
                    __unmar__(self.client_req_),
                    WALL,
                    __unmar__(self.req_file_))
                self.__send__(self.server_msg_)
                
                offset = self.__receive__()
                if self.status_ == 2: return
                b2w = self.__receive__()
                if self.status_ == 2: return
                
                self.server_msg_ = "\tOffset: {}".format(__unmar__(offset, int))
                self.__send__(self.server_msg_)
                
                self.server_msg_ = "\tSequence of bytes to write: %s\n%s\n" % (
                    __unmar__(b2w),
                    END_OF_REQUEST)
                self.__send__(self.server_msg_)
        
                with open(
                        self.serv_dir_+__unmar__(self.req_file_)) as f:
                    content = f.read()
                    if __unmar__(offset, int) >= len(content):
                        self.server_msg_ = "Your \"offset\" exceeded the length of file content"
                    else:
                        last_idx = __unmar__(offset,int)+len(
                            __unmar__(b2w))
                        self.server_msg_ = "%s%s%s" % (
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
                self.__send__(str(self.status_))
        if self.status_ == 1:
            self.__one_copy_semantics__(
                __unmar__(self.req_file_),
                __unmar__(offset,int),
                __unmar__(b2w))
        
    
    def __CREATE__(self):
        self.req_file_ = self.__receive__()
        if self.status_ == 2: return
        print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                     __unmar__(self.req_file_)))
        self.server_msg_ = "\nYou requested to:\n\n%s %s %s\n\tfile: %s\n%s\n" % (
            WALL,
            __unmar__(self.client_req_),
            WALL,
            __unmar__(self.req_file_),
            END_OF_REQUEST)
        self.__send__(self.server_msg_)
        file_type_idx = __unmar__(self.req_file_).rfind('.')
        file_type = __unmar__(self.req_file_)[file_type_idx:]
        if file_type != ".txt":
            self.__send__(0)
            self.server_msg_ = "The file type needs to be \".txt\".\n\
    Convertig file to \".txt\"...\n"
            self.__send__(self.server_msg_)
            new_file = __unmar__(self.req_file_)+".txt"
            
            if self.__file_exist__(
                self.serv_dir_,new_file):
                self.__send__(1)
                self.__overwrite__()
            else:
                self.__send__(0)
                content = self.__receive__()
                if self.status_ == 2: return
                self.__create_file__(
                        self.serv_dir_,new_file,__unmar__(content))
                self.status_ = 1
    
        elif self.__file_exist__(
            self.serv_dir_,__unmar__(self.req_file_)):
            self.__send__(2)
            
            self.__overwrite__()
        else:
            self.__send__(1)
            content = self.__receive__()
            if self.status_ == 2: return
            self.__create_file__(
                self.serv_dir_,__unmar__(self.req_file_),
                __unmar__(content))
            self.status_ = 1
    
    
    def __overwrite__(self):
        self.server_msg_ = "The file \"%s\" already exists in the server directory.\n\
    Do you want to overwrite it[Y/n]: " % (__unmar__(self.req_file_))
        self.__send__(self.server_msg_)
        answer = self.__receive__()
        if self.status_ == 2: return
        
        if __unmar__(answer) == ""\
        or __unmar__(answer).lower() == 'y'\
        or __unmar__(answer).lower() == 'yes':
            content = self.__receive__()
            if self.status_ == 2: return
            self.__create_file__(
                self.serv_dir_,__unmar__(self.req_file_),
                __unmar__(content))
            self.status_ = 1

        
    def __ERASE__(self):
        cache = self.__receive__()
        if self.status_ == 2: return
        if __unmar__(cache,int) == 0:
            self.req_file_ = self.__receive__()
            if self.status_ == 2: return
            print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                     __unmar__(self.req_file_)))
            offset = self.__receive__()
            if self.status_ == 2: return
            b2e = self.__receive__()
            if self.status_ == 2: return
            with open(
                    self.serv_dir_+__unmar__(self.req_file_)) as f:
                content = f.read()
                self.server_msg_ = content[:__unmar__(offset,int)] + \
                    content[__unmar__(b2e,int):]
                with open(
                        self.serv_dir_+__unmar__(self.req_file_), 'w') as ff:
                    ff.write(self.server_msg_)
                    ff.close()
                self.status_ = 1
                f.close()
            self.server_msg_ = "File \"%s\" in server_directory updated through client cache.\n" % (
                __unmar__(self.req_file_))
            self.__send__(self.server_msg_)
            self.status_ = 1
        else:
            self.req_file_ = self.__receive__()
            if self.status_ == 2: return
            print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                         __unmar__(self.req_file_)))
            if self.__check_server_directory__(self.req_file_):
                self.server_msg_ = "\nYou requested to:\n\n%s %s %s\n\tfile: %s" % (
                    WALL,
                    __unmar__(self.client_req_),
                    WALL,
                    __unmar__(self.req_file_))
                self.__send__(self.server_msg_)
                
                offset = self.__receive__()
                if self.status_ == 2: return
                b2e = self.__receive__()
                if self.status_ == 2: return
                
                self.server_msg_ = "\tOffset: {}".format(__unmar__(offset, int))
                self.__send__(self.server_msg_)
                
                self.server_msg_ = "\tSequence of bytes to erase: %s\n%s\n" % (
                    __unmar__(b2e),
                    END_OF_REQUEST)
                self.__send__(self.server_msg_)
                    
                with open(
                        self.serv_dir_+__unmar__(self.req_file_)) as f:
                    content = f.read()
                    if int(__unmar__(offset,int)) >= len(content):
                        self.server_msg_ = "Your \"offset\" exceeded the length of file content.\n"
                   
                    elif __unmar__(offset,int) + __unmar__(b2e,int) > len(content):
                        self.server_msg_ = "Your length of \"bytes to read\" exceeded the length of file content.\n"
                    
                    else:
                        if __unmar__(b2e,int) == -1:
                            b2e = __mar__(len(content))
                        self.server_msg_ = content[:__unmar__(offset,int)] + \
                            content[__unmar__(b2e,int):]
                        with open(
                                self.serv_dir_+__unmar__(self.req_file_), 'w') as ff:
                            ff.write(self.server_msg_)
                            ff.close()
                        self.status_ = 1
                    f.close()
                self.__send__(self.server_msg_)
                self.__send__(str(self.status_))
        if self.status_ == 1:
            self.__one_copy_semantics__(
                __unmar__(self.req_file_),
                __unmar__(offset,int),
                __unmar__(b2e))
        
    
    def __DELETE__(self):
        self.req_file_ = self.__receive__()
        if self.status_ == 2: return
        print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                     __unmar__(self.req_file_)))
        if self.__check_server_directory__(self.req_file_):
            self.server_msg_ = "\nYou requested to:\n\n%s %s %s\n\tfile: %s\n%s\n" % (
                WALL,
                __unmar__(self.client_req_),
                WALL,
                __unmar__(self.req_file_),
                END_OF_REQUEST)
            self.__send__(self.server_msg_)
            
            os.remove(
                self.serv_dir_+__unmar__(self.req_file_))
            self.status_ = 1


    def __LS__(self):
        self.server_msg_ = "List all files on Server Directory"
        print('\n\t' + self.server_msg_ + '\n')
        self.server_msg_ = "\nYou requested to " + self.server_msg_
        self.__send__(self.server_msg_)
        files = '\n' + "==========" + " Server Directory " + "==========" + '\n'
        for c in os.listdir(self.serv_dir_):
            files += '\t'+c+'\n'
        files += END_OF_REQUEST + '\n'
        self.__send__(files)
        self.req_file_ = __mar__("ALL")
        self.status_ = 1
    
    
    def __DISAPPEAR__(self):
        print("\n\t%s from clients list\n" % (__unmar__(self.client_req_)))
        self.req_file_ = __mar__("")
        self.clients_.remove(self.client_)
        self.status_ = 1










    
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
 
    def __send__(self,msg):
        if type(msg) != str:
            msg = str(msg)
        bufsize = self.__get_bufsize__(msg)
        self.socket_.sendto(__mar__(bufsize),self.client_)
        self.socket_.sendto(__mar__(msg),self.client_)
    
    
    def __get_bufsize__(self,msg):
        k = 1
        while k < len(msg):
            k = k * 2
        return k
    
    def __receive__(self):
        timeout = select.select([self.socket_],[],[],TIMEOUT)
        if timeout[0]:
            bufsize,self.client_ = self.socket_.recvfrom(12)
            msg,self.client_ = self.socket_.recvfrom(__unmar__(bufsize,int))
            return msg
        else:
            self.status_ = 2
            
    def __create_socket__(self, host, port):
        print("Creating UDP socket...")
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        print("Connecting socket to...\n - host: {} \n - port {}".format(host,port))
        sock.bind((host, port))
        print("Socket created")
        return sock
    
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
            
    def __check_server_directory__(self,filename):
        p = False
        if self.__file_exist__(self.serv_dir_,__unmar__(filename)):
            self.__send__(1)
            p = True
        else:
            self.__send__(0)
            self.server_msg_ = "\nThe file \"%s\" does not exist in the server directory.\n" % (
                __unmar__(filename))
            self.__send__(self.server_msg_)
        return p
            
    
    def __file_exist__(self,directory,filename):
        return os.path.isfile(directory+filename)
            
    
    def __record_client__(self,client):
        if self.__file_exist__(DATA_DIR,CLIENT_FILE):
            f = open(DATA_DIR+CLIENT_FILE,'r')
            if client+'\n' in f:
                f.close()
            else:
                self.client_file_ = open(DATA_DIR+CLIENT_FILE,'a')
                self.client_file_.write(client+'\n')
                self.client_file_.close()
        
    def __append_client__(self,client):
        try:
            self.clients_.remove(client)
            self.clients_.appendleft(client)
        except ValueError:
            self.clients_.appendleft(client)

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
        
    def __update_time__(self):
        global CUR
        while True:
            CUR = datetime.now()
            time.sleep(0.2)
        

if __name__ == "__main__":
    hostname = socket.gethostname()
    port = 9999
    serv_dir = "/home/csy/Documents/git/Remote_File_Server/Server_Directory/"
    serv = Server(hostname,port,serv_dir)
##    serv.start_server_.start()
    serv.__start__()
    

