# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 22:06:07 2020

@author: CSY
"""


import socket

BUF = 4096


class Client:
    
    def __init__(self, host, port):
        self.host_ = host
        self.port_ = port
        self.socket_ = self.__create_socket__()
        self.server_ = (self.host_, self.port_)
        self.server_addr_ = None
        self.client_req_ = ""
        self.pass_req_ = ""
        
    
    
    def __create_socket__(self):
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        return sock



    def __READ__(self, pathname, offset, b2r):
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
            serv_res = self.__receive__()
        elif self.__dec__(self.pass_req_, 'bool') == False:
            response = self.__receive__()



    def __WRITE__(self, pathname, offset, b2w):
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
            serv_res = self.__receive__()
        elif self.__dec__(self.pass_req_, 'bool') == False:
            response = self.__receive__()





    def __MONITOR__(self, pathname, length):
        self.client_req_ = "MONITOR"
        self.__send__(self.client_req_)
        pass
    def __IDEM__(self):
        pass
    def __NON_IDEM__(self):
        pass



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



def main():
    
    client = Client("DESKTOP-0J4QGEB",9999)
    client.__READ__("aaa.txt", 3, 5)
    client.__WRITE__("aaa.txt", 0, "bcskjl")


    
if __name__ == "__main__":
    main()



