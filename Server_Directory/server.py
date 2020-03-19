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

BUF = 4096
FILES = deque()
WALL = "==============="
END_OF_REQUEST = "================ END ================"

SERV_DIR = "..\\Server_Directory\\"


class Server:
    
    def __init__(self, host, port):
        self.host_ = host
        self.port_ = port
        self.socket_ = self.__create_socket__(self.host_, self.port_)
        self.client_ = None
        self.client_req_ = ""
        self.server_msg_ = ""
        self.clients_ = []




            
    def __create_socket__(self, host, port):
        print("Creating UDP socket...")
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        print("Connecting socket to...\n - host: {} \n - port {}".format(host,port))
        sock.bind((host, port))
        print("Socket created")
        return sock




            
    def __start__(self):
        while True:
            print("\nWaiting to receive message...\n")
            self.client_req_ = self.__receive__()
            print("Client \"%s\" requested to:" % (self.client_[0]))
            if self.__dec__(self.client_req_, 'str') == "READ":
                self.__READ__()
            elif self.__dec__(self.client_req_, 'str') == "WRITE":
                self.__WRITE__()
            elif self.__dec__(self.client_req_, 'str') == "MONITOR":
                self.__MONITOR__()
            elif self.__dec__(self.client_req_, 'str') == "RENAME":
                self.__RENAME__()
            elif self.__dec__(self.client_req_, 'str') == "REPLACE":
                self.__REPLACE__()




            
    def __READ__(self):
        filename = self.__receive__()
        print("\n\t%s file: %s\n" % (self.__dec__(self.client_req_, 'str'),
                                     self.__dec__(filename, 'str')))
        if os.path.isfile(self.__dec__(filename, 'str')):
            self.__send__(1)

            self.server_msg_ = "You requested to:\n\n%s %s %s\n\tfile: %s" % (
                WALL,
                self.__dec__(self.client_req_, 'str'),
                WALL,
                self.__dec__(filename, 'str'))
            self.__send__(self.server_msg_)
            
            offset = self.__receive__()
            b2r = self.__receive__()
            
            self.server_msg_ = "\tOffset: {}".format(self.__dec__(offset, 'int'))
            self.__send__(self.server_msg_)
            
            self.server_msg_ = "\tTotal bytes to read: {}\n{}\n".format(
                self.__dec__(b2r, 'int'),
                END_OF_REQUEST)
            self.__send__(self.server_msg_)
            
            with open(self.__dec__(filename, 'str')) as f:
                content = f.read()
                if self.__dec__(offset, 'int') >= len(content):
                    self.server_msg_ = "Your \"offset\" exceeded the length of file content"
                elif self.__dec__(offset, 'int') + self.__dec__(b2r, 'int') > len(content):
                    self.server_msg_ = "Your length of \"bytes to read\" exceeded the length of file content"
                else:
                    self.server_msg_ = content[self.__dec__(offset, 'int'):
                                  self.__dec__(offset, 'int') + self.__dec__(b2r, 'int')]
                    
            self.__send__(self.server_msg_)
                
        else:
            self.__send__(0)
            self.server_msg_ = "The file \"%s\" does not exist in the server directory" % (
                self.__dec__(filename, 'str'))
            self.__send__(self.server_msg_)
        print("----------------------- END -----------------------")




            
    def __WRITE__(self):
        filename = self.__receive__()
        print("\n\t%s file: %s\n" % (self.__dec__(self.client_req_, 'str'),
                                     self.__dec__(filename, 'str')))
        if os.path.isfile(self.__dec__(filename, 'str')):
            self.__send__(1)

            self.server_msg_ = "You requested to:\n\n%s %s %s\n\tfile: %s" % (
                WALL,
                self.__dec__(self.client_req_, 'str'),
                WALL,
                self.__dec__(filename, 'str'))
            self.__send__(self.server_msg_)
            
            offset = self.__receive__()
            b2w = self.__receive__()
            
            self.server_msg_ = "\tOffset: {}".format(self.__dec__(offset, 'int'))
            self.__send__(self.server_msg_)
            
            self.server_msg_ = "\tSequence of bytes to write: %s\n%s\n" % (
                self.__dec__(b2w, 'str'),
                END_OF_REQUEST)
            self.__send__(self.server_msg_)

            with open(self.__dec__(filename, 'str')) as f:
                content = f.read()
                if self.__dec__(offset, 'int') >= len(content):
                    self.server_msg_ = "Your \"offset\" exceeded the length of file content"
                else:
                    self.server_msg_ = "%s%s%s" % (
                        content[:self.__dec__(offset, 'int')],
                        self.__dec__(b2w,'str'),
                        content[self.__dec__(offset, 'int'):])
                    with open(self.__dec__(filename, 'str'), 'w') as f:
                        file = f.write(self.server_msg_)
                        f.close()
                    
            self.__send__(self.server_msg_)

        else:
            self.__send__(0)
            self.server_msg_ = "The file \"%s\" does not exist in the server directory" % (
                self.__dec__(filename, 'str'))
            self.__send__(self.server_msg_)
        print("----------------------- END -----------------------")




            
    def __MONITOR__(self):
        filename = self.__receive__()
        print("\n\t%s file: %s\n" % (self.__dec__(self.client_req_, 'str'),
                                     self.__dec__(filename, 'str')))
        if os.path.isfile(self.__dec__(filename, 'str')):
            self.__send__(1)

            self.server_msg_ = "You requested to:\n\n%s %s %s\n\tfile: %s" % (
                WALL,
                self.__dec__(self.client_req_, 'str'),
                WALL,
                self.__dec__(filename, 'str'))
            self.__send__(self.server_msg_)

            length = self.__receive__()

            self.server_msg_ = "\tMonitoring Length: {}".format(
                self.__dec__(length, 'int'))
            self.__send__(self.server_msg_)

            now = datetime.now()
            des = now + timedelta(seconds=self.__dec__(length, 'int'))
            self.server_msg_ = "\tMonitoring Start Time: %s" % (
                str(now.time()))
            self.__send__(self.server_msg_)
            self.server_msg_ = "\tMonitoring End Time: %s\n%s\n" % (
                str(des.time()),
                END_OF_REQUEST)
            self.__send__(self.server_msg_)




            ################################################
            
            ori_file = open(self.__dec__(filename, 'str'))
            ori_content = ori_file.read()

            while now < des:
                now = datetime.now()
                new_file = open(self.__dec__(filename, 'str'))
                new_content = new_file.read()
                self.__send__(0)
                if ori_content != new_content:
                    self.__send__(1)
                    self.server_msg_ = "File \"%s\" Updated" % (
                        self.__dec__(filename, 'str'))
                    self.__send__(self.server_msg_)
                    self.server_msg_ = "Content: \n - %s" % (
                        new_content)
                    self.__send__(self.server_msg_)
            self.__send__(2)
            self.server_msg_ = "%s End of Monitoring %s" % (
                WALL,WALL)
            self.__send__(self.server_msg_)

            ################################################
                    
        else:
            self.__send__(0)
            self.server_msg_ = "The file \"%s\" does not exist in the server directory" % (
                self.__dec__(filename, 'str'))
            self.__send__(self.server_msg_)
        print("----------------------- END -----------------------")




    # =============================================================== #


    def __RENAME__(self):
        filename = self.__receive__()
        print("\n\t%s file: %s\n" % (self.__dec__(self.client_req_, 'str'),
                                     self.__dec__(filename, 'str')))
        if os.path.isfile(self.__dec__(filename, 'str')):
            self.__send__(1)

            self.server_msg_ = "You requested to:\n\n%s %s %s\n\tfile: %s" % (
                WALL,
                self.__dec__(self.client_req_, 'str'),
                WALL,
                self.__dec__(filename, 'str'))
            self.__send__(self.server_msg_)
            
            name = self.__receive__()
            
            self.server_msg_ = "\tChange the file name to: %s\n%s\n" % (
                self.__dec__(name, 'str'),
                END_OF_REQUEST)
            self.__send__(self.server_msg_)

            file_type_idx = self.__dec__(filename, 'str').rfind('.')
            file_type = self.__dec__(filename,'str')[file_type_idx:]

            print(self.__dec__(name,'str')[-len(file_type):])

            if self.__dec__(name, 'str')[-len(file_type):] != file_type:
                self.server_msg_ = "The file must be the same type."

            else:
                os.rename(self.__dec__(filename, 'str'),self.__dec__(name, 'str'))

                self.server_msg_ = "%s Rename Successful %s" % (
                    WALL, WALL)
            self.__send__(self.server_msg_)

        else:
            self.__send__(0)
            self.server_msg_ = "The file \"%s\" does not exist in the server directory" % (
                self.__dec__(filename, 'str'))
            self.__send__(self.server_msg_)
        print("----------------------- END -----------------------")




        
    def __REPLACE__(self):
        filename = self.__receive__()
        print("\n\t%s file: %s\n" % (self.__dec__(self.client_req_, 'str'),
                                     self.__dec__(filename, 'str')))
        if os.path.isfile(self.__dec__(filename, 'str')):
            self.__send__(1)

            self.server_msg_ = "You requested to:\n\n%s %s %s\n\tfile: %s" % (
                WALL,
                self.__dec__(self.client_req_, 'str'),
                WALL,
                self.__dec__(filename, 'str'))
            self.__send__(self.server_msg_)
            
            offset = self.__receive__()
            b2w = self.__receive__()
            
            self.server_msg_ = "\tOffset: {}".format(self.__dec__(offset, 'int'))
            self.__send__(self.server_msg_)
            
            self.server_msg_ = "\tSequence of bytes to write: %s\n%s\n" % (
                self.__dec__(b2w, 'str'),
                END_OF_REQUEST)
            self.__send__(self.server_msg_)

            with open(self.__dec__(filename, 'str')) as f:
                content = f.read()
                if self.__dec__(offset, 'int') >= len(content):
                    self.server_msg_ = "Your \"offset\" exceeded the length of file content"
                else:
                    last_idx = self.__dec__(offset,'int')+len(
                        self.__dec__(b2w,'str'))
                    self.server_msg_ = "%s%s%s" % (
                        content[:self.__dec__(offset, 'int')],
                        self.__dec__(b2w,'str'),
                        content[last_idx:])
                    with open(self.__dec__(filename, 'str'), 'w') as f:
                        file = f.write(self.server_msg_)
                        f.close()
                    
            self.__send__(self.server_msg_)

        else:
            self.__send__(0)
            self.server_msg_ = "The file \"%s\" does not exist in the server directory" % (
                self.__dec__(filename, 'str'))
            self.__send__(self.server_msg_)
        print("----------------------- END -----------------------")


    
    def __CREATE__(self):
        pass
    def __ERASE__(self):
        pass
    
 
    # =============================================================== #


            
    def __ls__(self, filetype=""):
        for c in os.listdir('.'):
            if filetype == "text":
                if ".txt" in str(c):
                    print(c)
            elif filetype == "dir":
                if os.path.isdir(c):
                    print(c)
            elif filetype == "others":
                if os.path.isfile(c):
                    if ".txt" not in str(c):
                        print(c)
            else:
                print(c)




            
    def __send__(self,msg):
        self.socket_.sendto(self.__enc__(msg), self.client_)
    def __receive__(self):
        msg, self.client_ = self.socket_.recvfrom(BUF)
        return msg
    def __enc__(self, data):
        if type(data) == str:
            return data.encode('utf-8')
        elif type(data) == int:
            return data.to_bytes(2, "little")
        elif type(data) == bool:
            return str(data).encode('utf-8')
    def __dec__(self, data, t):
        if t == "int":
            return int.from_bytes(data, "little")
        elif t == "str":
            return data.decode('utf-8')
        elif t == "bool":
            return bool(data.decode('utf-8'))




            
def main():
    server = Server(socket.gethostname(), 9999)
    server.__start__()




            
if __name__ == "__main__":
    main()
        
        
        
