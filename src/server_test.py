# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 21:35:32 2020

@author: CSY
"""


import socket
import os
from collections import deque
from datetime import datetime
from datetime import timedelta
import threading
import time

BUF = 4096
FILES = deque()
WALL = "==============="
END_OF_REQUEST = "================ END ================"
HIST_FILE = "Server_Client_History.txt"
CLIENT_FILE = "Clients.txt"
DATA_DIR = "../data/"
MON_FILE = ""



class Server():
    
    
    def __init__(self, host,port,serv_dir):
        self.host_ = host
        self.port_ = port
        self.serv_dir_ = serv_dir
        self.socket_ = self.__create_socket__(self.host_, self.port_)
        self.client_ = None
        self.client_req_ = ""
        self.server_msg_ = ""
        self.history_ = self.__create_file__(DATA_DIR,HIST_FILE)
        self.clients_ = self.__create_file__(DATA_DIR,CLIENT_FILE)
        # self.thread_ = threading.Thread(target=self.run)





    def __start__(self):
        while True:
            print("\nWaiting to receive message...\n")
            self.client_req_ = self.__receive__()
            self.__add_client__(self.client_[0])
            print("Client \"%s\" requested to:" % (self.client_[0]))
            if self.__unmarshall__(self.client_req_) == "READ":
                self.__READ__()
            elif self.__unmarshall__(self.client_req_) == "WRITE":
                self.__WRITE__()
            elif self.__unmarshall__(self.client_req_) == "MONITOR":
                self.__MONITOR__()
            elif self.__unmarshall__(self.client_req_) == "RENAME":
                self.__RENAME__()
            elif self.__unmarshall__(self.client_req_) == "REPLACE":
                self.__REPLACE__()
            elif self.__unmarshall__(self.client_req_) == "CREATE":
                self.__CREATE__()
            elif self.__unmarshall__(self.client_req_) == "ERASE":
                self.__ERASE__()
            elif self.__unmarshall__(self.client_req_) == "DELETE":
                self.__DELETE__()
        
            
            





    def __READ__(self):
        filename = self.__receive__()
        print("\n\t%s file: %s\n" % (self.__unmarshall__(self.client_req_),
                                     self.__unmarshall__(filename)))
        if self.__file_exist__(
                self.serv_dir_,self.__unmarshall__(filename)):
            self.__send__(1)

            self.server_msg_ = "You requested to:\n\n%s %s %s\n\tfile: %s" % (
                WALL,
                self.__unmarshall__(self.client_req_),
                WALL,
                self.__unmarshall__(filename))
            self.__send__(self.server_msg_)
            
            offset = self.__receive__()
            b2r = self.__receive__()
            
            self.server_msg_ = "\tOffset: {}".format(self.__unmarshall__(offset))
            self.__send__(self.server_msg_)
            
            self.server_msg_ = "\tTotal bytes to read: {}\n{}\n".format(
                self.__unmarshall__(b2r,int),
                END_OF_REQUEST)
            self.__send__(self.server_msg_)
            
            with open(
                    self.serv_dir_+self.__unmarshall__(filename)) as f:
                content = f.read()
                succ = False
                if int(self.__unmarshall__(offset,int)) >= len(content):
                    self.server_msg_ = "Your \"offset\" exceeded the length of file content"
               
                elif self.__unmarshall__(offset,int) + self.__unmarshall__(b2r,int) > len(content):
                    self.server_msg_ = "Your length of \"bytes to read\" exceeded the length of file content"
                
                else:
                    self.server_msg_ = content[self.__unmarshall__(offset,int):
                                  self.__unmarshall__(offset,int) + 
                                  self.__unmarshall__(b2r,int)]
                    # self.server_msg_ = content
                    succ = True
                    
            self.__record__(self.client_[0],str(self.port_),
                self.__unmarshall__(self.client_req_),
                self.__unmarshall__(filename),success=succ)
            
            self.__send__(self.server_msg_)
            self.__send__(str(succ))
                
        else:
            self.__send__(0)
            self.server_msg_ = "The file \"%s\" does not exist in the server directory" % (
                self.__unmarshall__(filename))
            self.__send__(self.server_msg_)
            self.__record__(self.client_[0],str(self.port_),
                self.__unmarshall__(self.client_req_),
                self.__unmarshall__(filename,str),success=False)
        print("----------------------- END -----------------------")





    def __WRITE__(self):
        filename = self.__receive__()
        print("\n\t%s file: %s\n" % (self.__unmarshall__(self.client_req_),
                                     self.__unmarshall__(filename)))
        if self.__file_exist__(
                self.serv_dir_,self.__unmarshall__(filename)):
            self.__send__(1)

            self.server_msg_ = "You requested to:\n\n%s %s %s\n\tfile: %s" % (
                WALL,
                self.__unmarshall__(self.client_req_),
                WALL,
                self.__unmarshall__(filename))
            self.__send__(self.server_msg_)
            
            offset = self.__receive__()
            b2w = self.__receive__()
            
            self.server_msg_ = "\tOffset: {}".format(self.__unmarshall__(offset, int))
            self.__send__(self.server_msg_)
            
            self.server_msg_ = "\tSequence of bytes to write: %s\n%s\n" % (
                self.__unmarshall__(b2w),
                END_OF_REQUEST)
            self.__send__(self.server_msg_)

            with open(
                    self.serv_dir_+self.__unmarshall__(filename)) as f:
                content = f.read()
                succ = False
                if self.__unmarshall__(offset,int) >= len(content):
                    self.server_msg_ = "Your \"offset\" exceeded the length of file content"
                else:
                    self.server_msg_ = "%s%s%s" % (
                        content[:self.__unmarshall__(offset, int)],
                        self.__unmarshall__(b2w),
                        content[self.__unmarshall__(offset, int):])
                    with open(
                            self.serv_dir_+self.__unmarshall__(filename), 'w') as f:
                        f.write(self.server_msg_)
                        f.close()
                        succ = True
            self.__record__(self.client_[0],str(self.port_),
                self.__unmarshall__(self.client_req_),
                self.__unmarshall__(filename),success=succ)
            
            self.__send__(self.server_msg_)
            # self.__send__(int(succ))
        else:
            self.__send__(0)
            self.server_msg_ = "The file \"%s\" does not exist in the server directory" % (
                self.__unmarshall__(filename))
            self.__record__(self.client_[0],str(self.port_),
                self.__unmarshall__(self.client_req_),
                self.__unmarshall__(filename),success=False)
            self.__send__(self.server_msg_)
        print("----------------------- END -----------------------")








    def __MONITOR__(self):
        global MON_FILE
        filename = self.__receive__()
        print("\n\t%s file: %s\n" % (self.__unmarshall__(self.client_req_),
                                     self.__unmarshall__(filename)))
        if self.__file_exist__(
                self.serv_dir_,self.__unmarshall__(filename)):
            self.__send__(1)

            self.server_msg_ = "You requested to:\n\n%s %s %s\n\tfile: %s" % (
                WALL,
                self.__unmarshall__(self.client_req_),
                WALL,
                self.__unmarshall__(filename))
            self.__send__(self.server_msg_)

            length = self.__receive__()

            self.server_msg_ = "\tMonitoring Length: {}".format(
                self.__unmarshall__(length, int))
            self.__send__(self.server_msg_)

            now = datetime.now()
            des = now + timedelta(seconds=self.__unmarshall__(length, int))
            self.server_msg_ = "\tMonitoring Start Time: %s" % (
                str(now.time()))
            self.__send__(self.server_msg_)
            self.server_msg_ = "\tMonitoring End Time: %s\n%s\n" % (
                str(des.time()),
                END_OF_REQUEST)
            self.__send__(self.server_msg_)

#########################################################
            
            ori_file = open(self.serv_dir_+self.__unmarshall__(filename))
            ori_content = ori_file.read()
            ori_file.close()

            self.__monitoring__(filename,ori_content,now,des)
            
#########################################################
        else:
            self.__send__(0)
            self.server_msg_ = "The file \"%s\" does not exist in the server directory" % (
                self.__unmarshall__(filename))
            self.__send__(self.server_msg_)
        print("----------------------- END -----------------------")
        
        
        
    def __monitoring__(self,filename,ori_content,now,des):
        while now < des:
            now = datetime.now()
            new_file = open(
                self.serv_dir_+self.__unmarshall__(filename))
            new_content = new_file.read()
            self.__send__(0)
            if ori_content != new_content:
                self.__send__(1)
                print("updated")
                self.server_msg_ = "File \"%s\" Updated" % (
                    self.__unmarshall__(filename))
                self.__send__(self.server_msg_)
                self.server_msg_ = "Content: \n%s" % (
                    new_content)
                self.__send__(self.server_msg_)
                ori_content = new_content
        self.__send__(2)
        self.server_msg_ = "%s End of Monitoring %s" % (
            WALL,WALL)
        self.__send__(self.server_msg_)




    
            


    # Non-Idempotent
    def __RENAME__(self):
        filename = self.__receive__()
        print("\n\t%s file: %s\n" % (self.__unmarshall__(self.client_req_),
                                     self.__unmarshall__(filename)))
        if self.__file_exist__(
                self.serv_dir_,self.__unmarshall__(filename)):
            self.__send__(1)

            self.server_msg_ = "You requested to:\n\n%s %s %s\n\tfile: %s" % (
                WALL,
                self.__unmarshall__(self.client_req_),
                WALL,
                self.__unmarshall__(filename))
            self.__send__(self.server_msg_)
            
            name = self.__receive__()
            
            self.server_msg_ = "\tChange the file name to: %s\n%s\n" % (
                self.__unmarshall__(name),
                END_OF_REQUEST)
            self.__send__(self.server_msg_)

            file_type_idx = self.__unmarshall__(filename).rfind('.')
            file_type = self.__unmarshall__(filename)[file_type_idx:]

            print(self.__unmarshall__(name)[-len(file_type):])

            if self.__unmarshall__(name)[-len(file_type):] != file_type:
                self.server_msg_ = "The file must be the same type."

            else:
                os.rename(
                    self.serv_dir_+self.__unmarshall__(filename),
                    self.serv_dir_+self.__unmarshall__(name))

                self.server_msg_ = "%s Rename Successful %s" % (
                    WALL, WALL)
            self.__send__(self.server_msg_)

        else:
            self.__send__(0)
            self.server_msg_ = "The file \"%s\" does not exist in the server directory" % (
                self.__unmarshall__(filename))
            self.__send__(self.server_msg_)
        print("----------------------- END -----------------------")





    # Idempotent
    def __REPLACE__(self):
        filename = self.__receive__()
        print("\n\t%s file: %s\n" % (self.__unmarshall__(self.client_req_),
                                     self.__unmarshall__(filename)))
        if self.__file_exist__(
                self.serv_dir_,self.__unmarshall__(filename)):
            self.__send__(1)

            self.server_msg_ = "You requested to:\n\n%s %s %s\n\tfile: %s" % (
                WALL,
                self.__unmarshall__(self.client_req_),
                WALL,
                self.__unmarshall__(filename))
            self.__send__(self.server_msg_)
            
            offset = self.__receive__()
            b2w = self.__receive__()
            
            self.server_msg_ = "\tOffset: {}".format(self.__unmarshall__(offset, int))
            self.__send__(self.server_msg_)
            
            self.server_msg_ = "\tSequence of bytes to write: %s\n%s\n" % (
                self.__unmarshall__(b2w),
                END_OF_REQUEST)
            self.__send__(self.server_msg_)

            with open(
                    self.serv_dir_+self.__unmarshall__(filename)) as f:
                content = f.read()
                if self.__unmarshall__(offset, int) >= len(content):
                    self.server_msg_ = "Your \"offset\" exceeded the length of file content"
                else:
                    last_idx = self.__unmarshall__(offset,int)+len(
                        self.__unmarshall__(b2w))
                    self.server_msg_ = "%s%s%s" % (
                        content[:self.__unmarshall__(offset, int)],
                        self.__unmarshall__(b2w),
                        content[last_idx:])
                    with open(
                            self.serv_dir_+self.__unmarshall__(filename), 'w') as f:
                        f.write(self.server_msg_)
                        f.close()
                    
            self.__send__(self.server_msg_)

        else:
            self.__send__(0)
            self.server_msg_ = "The file \"%s\" does not exist in the server directory" % (
                self.__unmarshall__(filename))
            self.__send__(self.server_msg_)
        print("----------------------- END -----------------------")





    # Idempotent
    def __CREATE__(self):
        filename = self.__receive__()
        print("\n\t%s file: %s\n" % (self.__unmarshall__(self.client_req_),
                                     self.__unmarshall__(filename)))
        file_type_idx = self.__unmarshall__(filename).rfind('.')
        file_type = self.__unmarshall__(filename)[file_type_idx:]
        if file_type != ".txt":
            self.__send__(0)
            self.server_msg_ = "The file type needs to be \".txt\".\n\
Convertig file to \".txt\"...\n"
            self.__send__(self.server_msg_)
            filename = self.__unmarshall__(filename)+".txt"
            content = self.__receive__()
            self.__create_file__(
                    self.serv_dir_,filename,self.__unmarshall__(content))
            self.server_msg_ = "%s Created Successfully %s" % (
                    WALL, WALL)
            self.__send__(self.server_msg_)

        elif self.__file_exist__(
            self.serv_dir_,self.__unmarshall__(filename)):
            self.__send__(2)
            
            self.server_msg_ = "The file \"%s\" already exists in the server directory.\n\
Do you want to overwrite it[Y/n]: " % (self.__unmarshall__(filename))
            self.__send__(self.server_msg_)
            answer = self.__receive__()
            if self.__unmarshall__(answer) == ""\
            or self.__unmarshall__(answer).lower() == 'y'\
            or self.__unmarshall__(answer).lower() == 'yes':
                content = self.__receive__()
                self.__create_file__(
                    self.serv_dir_,self.__unmarshall__(filename),
                    self.__unmarshall__(content))
                self.server_msg_ = "%s Created Successfully %s" % (
                    WALL, WALL)
                self.__send__(self.server_msg_)
            else:
                self.server_msg_ = "\n%s File NOT Created %s" % (
                    WALL,WALL)
                self.__send__(self.server_msg_)
        else:
            self.__send__(1)
            content = self.__receive__()
            self.__create_file__(
                self.serv_dir_,self.__unmarshall__(filename),
                self.__unmarshall__(content))
            self.server_msg_ = "%s Created Successfully %s" % (
                    WALL, WALL)
            self.__send__(self.server_msg_)
        print("----------------------- END -----------------------")
           




     # =============================================================== #       
        
    # non-idempotent    
    def __ERASE__(self):
        pass

    # idempotent
    def __DELETE__(self):
        pass
    
    # =============================================================== #





    def __create_socket__(self, host, port):
        print("Creating UDP socket...")
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        print("Connecting socket to...\n - host: {} \n - port {}".format(host,port))
        sock.bind((host, port))
        print("Socket created")
        return sock





    def __file_exist__(self,directory,filename):
        return os.path.isfile(directory+filename)





    def __create_file__(self,directory,filename,content=None):
        if self.__file_exist__(directory,filename):
            pass
        else:
            new_file = open(directory+filename, 'w')
            if content != None:
                new_file.write(content)
                new_file.close()
            else:
                new_file.close()
                return new_file





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





    def __send__(self,msg):
        self.socket_.sendto(self.__marshall__(msg), self.client_)
    def __receive__(self):
        msg, self.client_ = self.socket_.recvfrom(BUF)
        return msg
    
        
        
        
    def __marshall__(self,s):
        if type(s) == int:
            s = str(s)
        hex_list = []
        for c in s:
            num = ord(c)
            dec = str(int(num/16))
            rem = str(self.get_remain(num,16))
            d = ''.join([dec,rem])
            h = bytearray.fromhex(d)
            hex_list.append(h)
        return b''.join(hex_list)
    def __unmarshall__(self,b,d_t=str):
        hex_list = b.hex()
        char_list = []
        for i in range(int(len(hex_list)/2)):
            h = hex_list[i*2:i*2+2]
            o = int(h[0]) * 16
            t = self.to_num(h[1])
            num = o + t
            char_list.append(chr(num))
        if d_t == int:
            return int(''.join(char_list))
        elif d_t == bool:
            return bool(''.join(char_list))
        return ''.join(char_list)
    def get_remain(self,a,b):
        r = a % b
        dic = {
            10:'A',
            11:'B',
            12:'C',
            13:'D',
            14:'E',
            15:'F'}
        if r in dic.keys():
            r = dic[r]
        return r
    def to_num(self,h):
        dic = {
            10:'a',
            11:'b',
            12:'c',
            13:'d',
            14:'e',
            15:'f'}
        if h in dic.values():
            k_list = list(dic.keys())
            v_list = list(dic.values())
            return int(k_list[v_list.index(h)])
        return int(h)
        
        
        
        
        
        




    def __ls__(self, filetype=""):
        for c in os.listdir('.'):
            if filetype == "text":
                if ".txt" in str(c):
                    print(c)
            elif filetype == "dir":
                if os.path.isdir(c):
                    print(c)
            elif filetype == "others":
                # if os.path.isfile(c):
                if self.__check_server_dir__(c):
                    if ".txt" not in str(c):
                        print(c)
            else:
                print(c)
    




if __name__ == "__main__":

    serv_dir = "/home/csy/Documents/git/Remote_File_Server/Server_Directory/"
    serv = Server(socket.gethostname(),9999,serv_dir)
    serv.__start__()
    
    
    
    # def __enc__(self, data):
    #     if type(data) == str:
    #         return data.encode('utf-8')
    #     elif type(data) == int:
    #         return data.to_bytes(2, "little")
    #     elif type(data) == bool:
    #         return str(data).encode('utf-8')
    # def __dec__(self, data, t):
    #     if t == "int":
    #         return int.from_bytes(data, "little")
    #     elif t == "str":
    #         return data.decode('utf-8')
    #     elif t == "bool":
    #         return bool(data.decode('utf-8'))
    
    
