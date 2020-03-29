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
from mar_unmar_shall import __marshall__ as __mar__
from mar_unmar_shall import __unmarshall__ as __unmar__

BUF = 4096
WALL = "==============="
END_OF_REQUEST = "================ END ================"
HIST_FILE = "Server_Client_History.txt"
CLIENT_FILE = "Clients.txt"
DATA_DIR = "../data/"
CUR = datetime.now()

class Server():
    
    def __init__(self, host,port,serv_dir):
        self.host_ = host
        self.port_ = port
        self.serv_dir_ = serv_dir
        self.socket_ = self.__create_socket__(self.host_, self.port_)
        self.client_ = ""
        self.client_req_ = ""
        self.server_msg_ = ""
        self.history_ = self.__create_file__(DATA_DIR,HIST_FILE)
        self.clients_ = self.__create_file__(DATA_DIR,CLIENT_FILE)
        self.time_thread_ = threading.Thread(target=self.__update_time__,daemon=True)
        self.time_thread_.start()

    def __start__(self):
        while True:
            print("\nWaiting to receive message...\n")
            self.client_req_ = self.__receive__()
            self.__add_client__(self.client_[0])
            print("Client \"%s\" requested to:" % (self.client_[0]))
            if __unmar__(self.client_req_) == "READ":
                self.__READ__()
            elif __unmar__(self.client_req_) == "WRITE":
                self.__WRITE__()
            elif __unmar__(self.client_req_) == "MONITOR":
                self.__MONITOR__()
            elif __unmar__(self.client_req_) == "RENAME":
                self.__RENAME__()
            elif __unmar__(self.client_req_) == "REPLACE":
                self.__REPLACE__()
            elif __unmar__(self.client_req_) == "CREATE":
                self.__CREATE__()
            elif __unmar__(self.client_req_) == "ERASE":
                self.__ERASE__()
            elif __unmar__(self.client_req_) == "DELETE":
                self.__DELETE__()
            elif __unmar__(self.client_req_) == "LS":
                self.__LS__()
                
                
    def __READ__(self):
        filename = self.__receive__()
        print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                     __unmar__(filename)))
        if self.__file_exist__(
                self.serv_dir_,__unmar__(filename)):
            self.__send__(1)
    
            self.server_msg_ = "\nYou requested to:\n\n%s %s %s\n\tfile: %s" % (
                WALL,
                __unmar__(self.client_req_),
                WALL,
                __unmar__(filename))
            self.__send__(self.server_msg_)
            
            offset = self.__receive__()
            b2r = self.__receive__()
            
            self.server_msg_ = "\tOffset: {}".format(__unmar__(offset))
            self.__send__(self.server_msg_)
            
            self.server_msg_ = "\tTotal bytes to read: {}\n{}\n".format(
                __unmar__(b2r,int),
                END_OF_REQUEST)
            self.__send__(self.server_msg_)
            
            with open(
                    self.serv_dir_+__unmar__(filename)) as f:
                content = f.read()
                succ = False
                if int(__unmar__(offset,int)) >= len(content):
                    self.server_msg_ = "Your \"offset\" exceeded the length of file content.\n"
               
                elif __unmar__(offset,int) + __unmar__(b2r,int) > len(content):
                    self.server_msg_ = "Your length of \"bytes to read\" exceeded the length of file content.\n"
                
                else:
                    self.server_msg_ = content[__unmar__(offset,int):
                                  __unmar__(offset,int) + 
                                  __unmar__(b2r,int)]
                    succ = True
                f.close()
            self.__record__(self.client_[0],str(self.port_),
                __unmar__(self.client_req_),
                __unmar__(filename),success=succ)
            
            self.__send__(self.server_msg_)
            self.__send__(str(succ))
        else:
            self.__send__(0)
            self.server_msg_ = "\nThe file \"%s\" does not exist in the server directory.\n" % (
                __unmar__(filename))
            self.__send__(self.server_msg_)
            self.__record__(self.client_[0],str(self.port_),
                __unmar__(self.client_req_),
                __unmar__(filename,str),success=False)
        print("----------------------- END -----------------------")
        
    def __WRITE__(self):
        cache = self.__receive__()
        if __unmar__(cache,int) == 0:
            filename = self.__receive__()
            print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                     __unmar__(filename)))
            offset = self.__receive__()
            b2w = self.__receive__()
            with open(
                self.serv_dir_+__unmar__(filename)) as f:
                content = f.read()
                f.close()
            self.server_msg_ = "%s%s%s" % (
                content[:__unmar__(offset, int)],
                __unmar__(b2w),
                content[__unmar__(offset, int):])
            with open(
                self.serv_dir_+__unmar__(filename), 'w') as ff:
                ff.write(self.server_msg_)
                ff.close()
            self.server_msg_ = "File \"%s\" in server_directory updated through client cache.\n" % (__unmar__(filename))
            self.__send__(self.server_msg_)
        else:
            filename = self.__receive__()
            print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                         __unmar__(filename)))
            if self.__file_exist__(
                    self.serv_dir_,__unmar__(filename)):
                self.__send__(1)
    
                self.server_msg_ = "\nYou requested to:\n\n%s %s %s\n\tfile: %s" % (
                    WALL,
                    __unmar__(self.client_req_),
                    WALL,
                    __unmar__(filename))
                self.__send__(self.server_msg_)
                
                offset = self.__receive__()
                b2w = self.__receive__()
                
                self.server_msg_ = "\tOffset: {}".format(__unmar__(offset, int))
                self.__send__(self.server_msg_)
                
                self.server_msg_ = "\tSequence of bytes to write: %s\n%s\n" % (
                    __unmar__(b2w),
                    END_OF_REQUEST)
                self.__send__(self.server_msg_)
    
                with open(
                        self.serv_dir_+__unmar__(filename)) as f:
                    content = f.read()
                    succ = False
                    if __unmar__(offset,int) >= len(content):
                        self.server_msg_ = "Your \"offset\" exceeded the length of file content\n"
                    else:
                        self.server_msg_ = "%s%s%s" % (
                            content[:__unmar__(offset, int)],
                            __unmar__(b2w),
                            content[__unmar__(offset, int):])
                        with open(
                                self.serv_dir_+__unmar__(filename), 'w') as ff:
                            ff.write(self.server_msg_)
                            ff.close()
                            succ = True
                    f.close()
                self.__record__(self.client_[0],str(self.port_),
                    __unmar__(self.client_req_),
                    __unmar__(filename),success=succ)
                
                self.__send__(self.server_msg_)
            else:
                self.__send__(0)
                self.server_msg_ = "\nThe file \"%s\" does not exist in the server directory\n" % (
                    __unmar__(filename))
                self.__record__(self.client_[0],str(self.port_),
                    __unmar__(self.client_req_),
                    __unmar__(filename),success=False)
                self.__send__(self.server_msg_)
        print("----------------------- END -----------------------")
            
    def __MONITOR__(self):
        filename = self.__receive__()
        print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                     __unmar__(filename)))
        if self.__file_exist__(
                self.serv_dir_,__unmar__(filename)):
            self.__send__(1)
    
            self.server_msg_ = "\nYou requested to:\n\n%s %s %s\n\tfile: %s" % (
                WALL,
                __unmar__(self.client_req_),
                WALL,
                __unmar__(filename))
            self.__send__(self.server_msg_)
    
            length = self.__receive__()
    
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
    
            ori_file = open(self.serv_dir_+__unmar__(filename))
            ori_content = ori_file.read()
            ori_file.close()
            
            monitor_thread_ = threading.Thread(target=self.__monitoring__,
                                           args=(filename,ori_content,des))
            monitor_thread_.start()
            
            self.__record__(self.client_[0],str(self.port_),
                __unmar__(self.client_req_),
                __unmar__(filename),success=True)
            
        else:
            self.__send__(0)
            self.server_msg_ = "\nThe file \"%s\" does not exist in the server directory\n" % (
                __unmar__(filename))
            self.__record__(self.client_[0],str(self.port_),
                __unmar__(self.client_req_),
                __unmar__(filename),success=False)
            self.__send__(self.server_msg_)
        print("----------------------- END -----------------------")
    def __monitoring__(self,filename,ori_content,des):
        global CUR
        while CUR < des:
            new_file = open(
                self.serv_dir_+__unmar__(filename))
            new_content = new_file.read()
            if ori_content != new_content:
                self.__send__(1)
                self.server_msg_ = "File \"%s\" Updated" % (
                    __unmar__(filename))
                self.__send__(self.server_msg_)
                self.server_msg_ = "Content: \n%s" % (
                    new_content)
                self.__send__(self.server_msg_)
                ori_content = new_content
        self.__send__(0)
        self.server_msg_ = "%s End of Monitoring %s" % (
            WALL,WALL)
        self.__send__(self.server_msg_)
        
    def __RENAME__(self):
        filename = self.__receive__()
        print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                     __unmar__(filename)))
        if self.__file_exist__(
                self.serv_dir_,__unmar__(filename)):
            self.__send__(1)
    
            self.server_msg_ = "\nYou requested to:\n\n%s %s %s\n\tfile: %s" % (
                WALL,
                __unmar__(self.client_req_),
                WALL,
                __unmar__(filename))
            self.__send__(self.server_msg_)
            
            name = self.__receive__()
            
            self.server_msg_ = "\tChange the file name to: %s\n%s\n" % (
                __unmar__(name),
                END_OF_REQUEST)
            self.__send__(self.server_msg_)
    
            file_type_idx = __unmar__(filename).rfind('.')
            file_type = __unmar__(filename)[file_type_idx:]
    
            print(__unmar__(name)[-len(file_type):])
            
            succ = False
            
            if __unmar__(name)[-len(file_type):] != file_type:
                self.server_msg_ = "The file must be the same type."
    
            else:
                os.rename(
                    self.serv_dir_+__unmar__(filename),
                    self.serv_dir_+__unmar__(name))
                succ = True
                self.server_msg_ = "%s Rename Successful %s" % (
                    WALL, WALL)
                
            self.__record__(self.client_[0],str(self.port_),
                __unmar__(self.client_req_),
                __unmar__(filename),success=succ)
            self.__send__(self.server_msg_)
    
        else:
            self.__send__(0)
            self.server_msg_ = "The file \"%s\" does not exist in the server directory" % (
                __unmar__(filename))
            self.__record__(self.client_[0],str(self.port_),
                __unmar__(self.client_req_),
                __unmar__(filename),success=False)
            self.__send__(self.server_msg_)
        print("----------------------- END -----------------------")
        
    def __REPLACE__(self):
        filename = self.__receive__()
        print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                     __unmar__(filename)))
        if self.__file_exist__(
                self.serv_dir_,__unmar__(filename)):
            self.__send__(1)
    
            self.server_msg_ = "\nYou requested to:\n\n%s %s %s\n\tfile: %s" % (
                WALL,
                __unmar__(self.client_req_),
                WALL,
                __unmar__(filename))
            self.__send__(self.server_msg_)
            
            offset = self.__receive__()
            b2w = self.__receive__()
            
            self.server_msg_ = "\tOffset: {}".format(__unmar__(offset, int))
            self.__send__(self.server_msg_)
            
            self.server_msg_ = "\tSequence of bytes to write: %s\n%s\n" % (
                __unmar__(b2w),
                END_OF_REQUEST)
            self.__send__(self.server_msg_)
    
            with open(
                    self.serv_dir_+__unmar__(filename)) as f:
                content = f.read()
                succ = False
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
                            self.serv_dir_+__unmar__(filename), 'w') as ff:
                        ff.write(self.server_msg_)
                        ff.close()
                    succ = True
                f.close()
            self.__record__(self.client_[0],str(self.port_),
                __unmar__(self.client_req_),
                __unmar__(filename),success=succ)
            self.__send__(self.server_msg_)
    
        else:
            self.__send__(0)
            self.server_msg_ = "The file \"%s\" does not exist in the server directory" % (
                __unmar__(filename))
            self.__record__(self.client_[0],str(self.port_),
                __unmar__(self.client_req_),
                __unmar__(filename),success=False)
            self.__send__(self.server_msg_)
        print("----------------------- END -----------------------")
        
    def __CREATE__(self):
        filename = self.__receive__()
        print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                     __unmar__(filename)))
        file_type_idx = __unmar__(filename).rfind('.')
        file_type = __unmar__(filename)[file_type_idx:]
        if file_type != ".txt":
            self.__send__(0)
            self.server_msg_ = "The file type needs to be \".txt\".\n\
    Convertig file to \".txt\"...\n"
            self.__send__(self.server_msg_)
            filename = __unmar__(filename)+".txt"
            content = self.__receive__()
            self.__create_file__(
                    self.serv_dir_,filename,__unmar__(content))
            self.server_msg_ = "%s Created Successfully %s" % (
                    WALL, WALL)
            self.__record__(self.client_[0],str(self.port_),
                __unmar__(self.client_req_),
                __unmar__(filename),success=True)
            self.__send__(self.server_msg_)
    
        elif self.__file_exist__(
            self.serv_dir_,__unmar__(filename)):
            self.__send__(2)
            
            self.server_msg_ = "The file \"%s\" already exists in the server directory.\n\
    Do you want to overwrite it[Y/n]: " % (__unmar__(filename))
            self.__send__(self.server_msg_)
            answer = self.__receive__()
            succ = False
            
            if __unmar__(answer) == ""\
            or __unmar__(answer).lower() == 'y'\
            or __unmar__(answer).lower() == 'yes':
                content = self.__receive__()
                self.__create_file__(
                    self.serv_dir_,__unmar__(filename),
                    __unmar__(content))
                self.server_msg_ = "%s Created Successfully %s" % (
                    WALL, WALL)
                succ = True
                self.__send__(self.server_msg_)
            else:
                self.server_msg_ = "\n%s File NOT Created %s" % (
                    WALL,WALL)
                self.__send__(self.server_msg_)
            self.__record__(self.client_[0],str(self.port_),
                    __unmar__(self.client_req_),
                    __unmar__(filename),success=succ)
        else:
            self.__send__(1)
            content = self.__receive__()
            self.__create_file__(
                self.serv_dir_,__unmar__(filename),
                __unmar__(content))
            self.server_msg_ = "%s Created Successfully %s" % (
                    WALL, WALL)
            self.__record__(self.client_[0],str(self.port_),
                __unmar__(self.client_req_),
                __unmar__(filename),success=True)
            self.__send__(self.server_msg_)
        print("----------------------- END -----------------------")
        
    def __ERASE__(self):
        filename = self.__receive__()
        print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                     __unmar__(filename)))
        if self.__file_exist__(
                self.serv_dir_,__unmar__(filename)):
            self.__send__(1)
            self.server_msg_ = "\nYou requested to:\n\n%s %s %s\n\tfile: %s" % (
                WALL,
                __unmar__(self.client_req_),
                WALL,
                __unmar__(filename))
            self.__send__(self.server_msg_)
            
            offset = self.__receive__()
            b2e = self.__receive__()
            
            self.server_msg_ = "\tOffset: {}".format(__unmar__(offset, int))
            self.__send__(self.server_msg_)
            
            self.server_msg_ = "\tSequence of bytes to erase: %s\n%s\n" % (
                __unmar__(b2e),
                END_OF_REQUEST)
            self.__send__(self.server_msg_)
                
            with open(
                    self.serv_dir_+__unmar__(filename)) as f:
                content = f.read()
                succ = False
                if int(__unmar__(offset,int)) >= len(content):
                    self.server_msg_ = "Your \"offset\" exceeded the length of file content.\n"
               
                elif __unmar__(offset,int) + __unmar__(b2e,int) > len(content):
                    self.server_msg_ = "Your length of \"bytes to read\" exceeded the length of file content.\n"
                
                else:
                    self.server_msg_ = content[:__unmar__(offset,int)] + \
                        content[__unmar__(b2e,int):]
                    with open(
                            self.serv_dir_+__unmar__(filename), 'w') as ff:
                        ff.write(self.server_msg_)
                        ff.close()
                    succ = True
                f.close()
            self.__record__(self.client_[0],str(self.port_),
                __unmar__(self.client_req_),
                __unmar__(filename),success=succ)
            
            self.__send__(self.server_msg_)
        else:
            self.__send__(0)
            self.server_msg_ = "\nThe file \"%s\" does not exist in the server directory.\n" % (
                __unmar__(filename))
            self.__send__(self.server_msg_)
            self.__record__(self.client_[0],str(self.port_),
                __unmar__(self.client_req_),
                __unmar__(filename,str),success=False)
        print("----------------------- END -----------------------")
        
    def __DELETE__(self):
        filename = self.__receive__()
        print("\n\t%s file: %s\n" % (__unmar__(self.client_req_),
                                     __unmar__(filename)))
        if self.__file_exist__(
                self.serv_dir_,__unmar__(filename)):
            self.__send__(1)
            self.server_msg_ = "\nYou requested to:\n\n%s %s %s\n\tfile: %s" % (
                WALL,
                __unmar__(self.client_req_),
                WALL,
                __unmar__(filename))
            self.__send__(self.server_msg_)
            
            os.remove(
                self.serv_dir_+__unmar__(filename))
            self.__record__(self.client_[0],str(self.port_),
                __unmar__(self.client_req_),
                __unmar__(filename),success=True)
            self.server_msg_ = "%s Removed Successfully %s" % (
                WALL,WALL)
            self.__send__(self.server_msg_)
        else:
            self.__send__(0)
            self.server_msg_ = "The file \"%s\" does not exist in the server directory"
            self.__record__(self.client_[0],str(self.port_),
                __unmar__(self.client_req_),
                __unmar__(filename),success=False)
            self.__send__(self.server_msg_)
        print("----------------------- END -----------------------")
        
    def __LS__(self):
        self.server_msg_ = "List all files on Server Directory"
        print('\n' + WALL + self.server_msg_ + WALL + '\n')
        self.server_msg_ = "\nYou requested to " + self.server_msg_
        self.__send__(self.server_msg_)
        files = '\n' + WALL + " Server Directory " + WALL + '\n'
        for c in os.listdir(self.serv_dir_):
            files += '\t'+c+'\n'
        files += END_OF_REQUEST + '\n'
        self.__send__(files)
        print("----------------------- END -----------------------")
                
                
        
        
        
        
        
    def __send__(self,msg):
        self.socket_.sendto(__mar__(msg), self.client_)
        
    def __receive__(self):
        msg, self.client_ = self.socket_.recvfrom(BUF)
        return msg

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
            
    def __file_exist__(self,directory,filename):
        return os.path.isfile(directory+filename)
            
    def __add_client__(self,client):
        if self.__file_exist__(DATA_DIR,CLIENT_FILE):
            f = open(DATA_DIR+CLIENT_FILE,'r')
            if client+'\n' in f:
                f.close()
            else:
                self.clients_ = open(DATA_DIR+CLIENT_FILE,'a')
                self.clients_.write(client+'\n')
                self.clients_.close()
                
    def __record__(self,client,port,request,filename,success):
        self.history_ = open(DATA_DIR+HIST_FILE,'a')
        succ = "Succeed"
        if success == False:
            succ = "Failed"
        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history_.write("Client: " + 
            client + "\tPort: " + port + "\tRequest: " + 
            request + " file \"" + filename + "\" " + 
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
    serv.__start__()
    
