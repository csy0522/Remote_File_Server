# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 22:06:07 2020

@author: CSY
"""


import socket
from datetime import datetime
from datetime import timedelta
import os
from client_cache import Client_Cache
BUF = 4096



class Client:
    
    def __init__(self, host, port, cache_dir):
        self.host_ = host
        self.port_ = port
        self.cache_dir_ = cache_dir
        self.socket_ = self.__create_socket__()
        self.server_ = (self.host_, self.port_)
        self.server_addr_ = None
        self.client_req_ = ""
        self.pass_req_ = ""
        self.cache_ = self.__create_cache__()
        



            
    def __create_socket__(self):
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        return sock
    
    
    def __create_cache__(self):
        cache = Client_Cache("c",self.cache_dir_)
        return cache



    


            
    def __READ__(self, pathname, offset, b2r):
        if self.__check_cache__(self.cache_dir_+pathname) == True:
            content = self.cache_.__READ__(
                self.cache_dir_+pathname,offset,b2r)
            print(content)
            return content
        self.client_req_ = "READ"
        self.__send__(self.client_req_)
        self.__send__(pathname)
        self.pass_req_ = self.__receive__()
        if self.__dec__(self.pass_req_, 'bool') == True:
            response = self.__receive__()
            self.__send__(offset)
            self.__send__(b2r)
            response = self.__receive__()
            response = self.__receive__()
            response = self.__receive__()
            self.cache_.__add__(
                self.cache_dir_+pathname,self.__dec__(response,'str'))
        elif self.__dec__(self.pass_req_, 'bool') == False:
            response = self.__receive__()
        
            



            
    def __WRITE__(self, pathname, offset, b2w):
        if self.__check_cache__(self.cache_dir_+pathname) == True:
            written_content = self.cache_.__WRITE__(
                self.cache_dir_+pathname,offset,b2w)
            return written_content
        self.client_req_ = "WRITE"
        self.__send__(self.client_req_)
        self.__send__(pathname)
        self.pass_req_ = self.__receive__()
        if self.__dec__(self.pass_req_, 'bool') == True:
            response = self.__receive__()
            self.__send__(offset)
            self.__send__(b2w)
            response = self.__receive__()
            response = self.__receive__()
            response = self.__receive__()
        elif self.__dec__(self.pass_req_, 'bool') == False:
            response = self.__receive__()
        self.cache_.__add__(self.cache_dir_+pathname)




            
    def __MONITOR__(self, pathname, length):
        self.client_req_ = "MONITOR"
        self.__send__(self.client_req_)
        self.__send__(pathname)
        self.pass_req_ = self.__receive__()
        if self.__dec__(self.pass_req_,'bool') == True:
            response = self.__receive__()
            self.__send__(length)
            response = self.__receive__()
            response = self.__receive__()
            response = self.__receive__()



        ################################################
            
            now = datetime.now()
            des = now + timedelta(seconds=length)
       
            while now < des:
                now = datetime.now()
                self.pass_req_ = self.__receive__(p=False)
                if self.__dec__(self.pass_req_,'int') == 1:
                    response = self.__receive__()
                    response = self.__receive__()         
                elif self.__dec__(self.pass_req_,'int') == 2:
                    break
            response = self.__receive__()

        ################################################
            
        elif self.__dec__(self.pass_req_, 'bool') == False:
            response = self.__receive__()
            



            
    def __RENAME__(self,pathname,name):
        self.client_req_ = "RENAME"
        self.__send__(self.client_req_)
        self.__send__(pathname)
        self.pass_req_ = self.__receive__()
        if self.__dec__(self.pass_req_, 'bool') == True:
            response = self.__receive__()
            self.__send__(name)
            response = self.__receive__()
            response = self.__receive__()
        elif self.__dec__(self.pass_req_, 'bool') == False:
            response = self.__receive__()




            
    def __REPLACE__(self,pathname,offset,b2w):
        self.client_req_ = "REPLACE"
        self.__send__(self.client_req_)
        self.__send__(pathname)
        self.pass_req_ = self.__receive__()
        if self.__dec__(self.pass_req_, 'bool') == True:
            response = self.__receive__()
            self.__send__(offset)
            self.__send__(b2w)
            response = self.__receive__()
            response = self.__receive__()
            response = self.__receive__()
        elif self.__dec__(self.pass_req_, 'bool') == False:
            response = self.__receive__()





    def __CREATE__(self,pathname,content):
        self.client_req_ = "CREATE"
        self.__send__(self.client_req_)
        self.__send__(pathname)
        self.pass_req_ = self.__receive__()
        if self.__dec__(self.pass_req_,'int') == 0:
            response = self.__receive__()
            self.__send__(content)
            response = self.__receive__()
        elif self.__dec__(self.pass_req_,'int') == 2:
            answer = input(
                self.__dec__(self.__receive__(p=False),'str'))
            self.__send__(answer)
            if answer == ""\
            or answer.lower() == 'y'\
            or answer.lower() == 'yes':
                self.__send__(content)
                response = self.__receive__()
            else:
                response = self.__receive__()
        elif self.__dec__(self.pass_req_,'int') == 1:
            self.__send__(content)
            response = self.__receive__()
            


    # =============================================================== #
    # def __ERASE__(self):
    #     self.client_req_ = "ERASE"
    #     self.__send__(self.client_req_)
    #     self.__send__(pathname)
    #     self.pass_req_ = self.__receive__()
    #     if self.__dec__(self.pass_req_, 'bool') == True:
    #         response = self.__receive__()
    #         self.__send__(offset)
    #         self.__send__(b2r)
    #         response = self.__receive__()
    #         response = self.__receive__()
    #         serv_res = self.__receive__()
    #     elif self.__dec__(self.pass_req_, 'bool') == False:
    #         response = self.__receive__()
    


    # def __DELETE__(self):
    #     self.client_req_ = "RENAME"
    #     self.__send__(self.client_req_)
    #     self.__send__(pathname)
    #     self.pass_req_ = self.__receive__()
    #     if self.__dec__(self.pass_req_, 'bool') == True:
    #         response = self.__receive__()
    #         self.__send__(name)
    #         response = self.__receive__()
    #         response = self.__receive__()
    #     elif self.__dec__(self.pass_req_, 'bool') == False:
    #         response = self.__receive__()
    # =============================================================== #




    def __check_cache__(self,file):
        return self.cache_.__exist__(file)



            
    def __send__(self,msg):
        self.socket_.sendto(self.__enc__(msg), self.server_)
    def __receive__(self, p=True):
        msg, self.server_addr_ = self.socket_.recvfrom(BUF)
        if p == True:
            print(self.__dec__(msg, 'str'))
        return msg
    def __enc__(self, data):
        if type(data) == str:
            return data.encode('utf-8')
        elif type(data) == int:
            return data.to_bytes(2, "little")
    def __dec__(self, data, t):
        if t == "int":
            return int.from_bytes(data, "little")
        elif t == "str":
            return data.decode('utf-8')
        elif t == "bool":
            return bool(int.from_bytes(data, "little"))



    
if __name__ == "__main__":
    
    cache_d = r"C:\Users\CSY\Desktop\Spring 2020\git\Remote_File_Server"

    cli = Client("DESKTOP-0J4QGEB",9999,cache_d)

    cli.__READ__("HELLO.txt",0,1)
















    
    
    
    
    
