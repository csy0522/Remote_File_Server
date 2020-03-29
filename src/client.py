#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 02:16:41 2020

@author: csy
"""


import socket
from datetime import datetime
from datetime import timedelta
from client_cache import Client_Cache
import argparse
from mar_unmar_shall import __marshall__ as __mar__
from mar_unmar_shall import __unmarshall__ as __unmar__

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
        self.cache_dir_ = cache_dir
    
    def __READ__(self, pathname, offset, b2r):
        self.client_req_ = "READ"
        if self.cache_.__data_exist__(pathname,offset,b2r) == True:
            self.__from_cache__(pathname,self.client_req_)
            cache_reading = self.cache_.__READ__(pathname,offset,b2r)
            if cache_reading == True:
                return
        self.__send__(self.client_req_)
        self.__send__(pathname)
        self.pass_req_ = self.__receive__(p=False)
        if __unmar__(self.pass_req_,int) == 1:
            self.__receive__()
            self.__send__(offset)
            self.__send__(b2r)
            self.__receive__()
            self.__receive__()
            response = self.__receive__()
            success = self.__receive__(p=False)
            if __unmar__(success) == "True":
                self.cache_.__add__(
                    pathname,__unmar__(response),
                    offset,offset+b2r)
        elif __unmar__(self.pass_req_,int) == 0:
            self.__receive__()
            
            
    def __WRITE__(self, pathname, offset, b2w):
        self.client_req_ = "WRITE"
        self.__send__(self.client_req_)
        if self.cache_.__data_exist__(pathname,offset) == True:
            self.__from_cache__(pathname,self.client_req_)
            self.cache_.__WRITE__(pathname,offset,b2w)
            self.__send__(0)
            self.__send__(pathname)
            self.__send__(offset)
            self.__send__(b2w)
            self.__receive__()
        else:
            self.__send__(1)
            self.__send__(pathname)
            self.pass_req_ = self.__receive__(p=False)
            if __unmar__(self.pass_req_,int) == 1:
                self.__receive__()
                self.__send__(offset)
                self.__send__(b2w)
                self.__receive__()
                self.__receive__()
                self.__receive__()
            elif __unmar__(self.pass_req_,int) == 0:
                self.__receive__()
                
    def __MONITOR__(self, pathname, length):
        self.client_req_ = "MONITOR"
        self.__send__(self.client_req_)
        self.__send__(pathname)
        self.pass_req_ = self.__receive__(p=False)
        if __unmar__(self.pass_req_,int) == 1:
            self.__receive__()
            self.__send__(length)
            self.__receive__()
            self.__receive__()
            self.__receive__()
            now = datetime.now()
            des = now + timedelta(seconds=int(length))
            while now < des:
                now = datetime.now()
                response = self.__receive__(p=False)
                if __unmar__(response,int) == 1:
                    self.__receive__()
                    self.__receive__()
                elif __unmar__(response,int) == 0:
                    self.__receive__()
                    break
        elif __unmar__(self.pass_req_,int) == 0:
            self.__receive__()
            
    def __RENAME__(self,pathname,name):
        self.client_req_ = "RENAME"
        self.__send__(self.client_req_)
        self.__send__(pathname)
        self.pass_req_ = self.__receive__(p=False)
        if __unmar__(self.pass_req_,int) == 1:
            self.__receive__()
            self.__send__(name)
            self.__receive__()
            self.__receive__()
        elif __unmar__(self.pass_req_,int) == 0:
            self.__receive__()
            
    def __REPLACE__(self,pathname,offset,b2w):
        self.client_req_ = "REPLACE"
        self.__send__(self.client_req_)
        self.__send__(pathname)
        self.pass_req_ = self.__receive__(p=False)
        if __unmar__(self.pass_req_,int) == 1:
            self.__receive__()
            self.__send__(offset)
            self.__send__(b2w)
            self.__receive__()
            self.__receive__()
            self.__receive__()
        elif __unmar__(self.pass_req_,int) == 0:
            self.__receive__()
            
    def __CREATE__(self,pathname,content):
        self.client_req_ = "CREATE"
        self.__send__(self.client_req_)
        self.__send__(pathname)
        self.pass_req_ = self.__receive__(p=False)
        if __unmar__(self.pass_req_,int) == 0:
            self.__receive__()
            self.__send__(content)
            self.__receive__()
        elif __unmar__(self.pass_req_,int) == 2:
            answer = input(
                __unmar__(self.__receive__(p=False)))
            self.__send__(answer)
            if answer == ""\
            or answer.lower() == 'y'\
            or answer.lower() == 'yes':
                self.__send__(content)
                self.__receive__()
            else:
                self.__receive__()
        elif __unmar__(self.pass_req_,int) == 1:
            self.__send__(content)
            self.__receive__()
            
    def __ERASE__(self,pathname,offset,b2e):
        self.client_req_ = "ERASE"
        self.__send__(self.client_req_)
        self.__send__(pathname)
        self.pass_req_ = self.__receive__(p=False)
        if __unmar__(self.pass_req_,int) == 1:
            self.__receive__()
            self.__send__(offset)
            self.__send__(b2e)
            self.__receive__()
            self.__receive__()
            self.__receive__()
        elif __unmar__(self.pass_req_,int) == 0:
            self.__receive__()
            
    def __DELETE__(self,pathname):
        self.client_req_ = "DELETE"
        self.__send__(self.client_req_)
        self.__send__(pathname)
        self.pass_req_ = self.__receive__(p=False)
        if __unmar__(self.pass_req_,int) == 1:
            self.__receive__()
            self.__receive__()
        elif __unmar__(self.pass_req_,int) == 0:
            self.__receive__()
            
    def __LS__(self):
        self.client_req_ = "LS"
        self.__send__(self.client_req_)
        self.__receive__()
        self.__receive__()
    
    def __create_socket__(self):
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        return sock
    
    def __create_cache__(self):
        cache = Client_Cache(socket.gethostbyname(socket.gethostname()),self.cache_dir_)
        return cache
    
    def __send__(self,msg):
        self.socket_.sendto(__mar__(msg), self.server_)
        
    def __receive__(self, p=True):
        msg, self.server_addr_ = self.socket_.recvfrom(BUF)
        if p == True:
            print(__unmar__(msg, 'str'))
        return msg
    
    def __check_cache__(self,data):
        return self.cache_.__data_exist__(data)
    
    def __from_cache__(self,filename,command):
        c1 = "The file \"%s\" exists in Cache!" % (
            filename)
        c2 = "%s \"%s\" from Cache..." % (
            command,filename)
        print('\n' + c1 + '\n' + c2 + '\n')
        
    def __get_args__(self):
        parser = argparse.ArgumentParser(
            description="Requesting from Server")
        parser.add_argument("request",nargs='?',
            help="request comment to the server")
        parser.add_argument("filename",nargs='?',
            help="Filename")
        parser.add_argument("add_arg1",nargs='?',help="additional argument")
        parser.add_argument("add_arg2",nargs='?',help="additional argument")
        args = parser.parse_args()
        return args
    
    def __check_args__(self,args,num):
        if args.filename == None:
            print("Need filename")
            return False
        if num == 2:
            if args.add_arg1 == None or args.add_arg2 == None:
                print("Need both arguments")
                return False
            return True
        elif num == 1:
            if args.add_arg1 == None:
                print("Need arg 1")
                return False
            elif args.add_arg2 != None:
                print("Don't need arg 2")
                return False
            return True
        elif num == 0:
            if args.add_arg1 != None:
                print("Do not need any other argument")
                return False
            return True
        
    def __process_args__(self,args):
        if args.request == None:
            print("Need Request")
        elif args.request == 'read':
            if self.__check_args__(args,2):
                client.__READ__(args.filename,
                int(args.add_arg1),int(args.add_arg2))
        elif args.request == 'write':
            if self.__check_args__(args,2):
                client.__WRITE__(args.filename,int(args.add_arg1),args.add_arg2)
        elif args.request == 'monitor':
            if self.__check_args__(args,1):
                client.__MONITOR__(args.filename,int(args.add_arg1))    
        elif args.request == 'rename':
            if self.__check_args__(args,1):
                client.__RENAME__(args.filename,args.add_arg1)
        elif args.request == 'replace':
            if self.__check_args__(args,2):
                client.__REPLACE__(args.filename,args.add_arg1,args.add_arg2)
        elif args.request == 'create':
            if self.__check_args__(args,1):
                client.__CREATE__(args.filename,args.add_arg1)
        elif args.request == 'delete':
            client.__DELETE__(args.filename)
        elif args.request == 'erase':
            if self.__check_args__(args,2):
                client.__ERASE__(args.filename,args.add_arg1,args.add_arg2)
                
    def __help__(self):
        print('\033[1m' + "read(r)" + '\033[0m' + " (\033[4mfilename\033[0m, \033[4moffset(int)\033[0m, \033[4mbytes-to-read(int)\033[0m")
        print(" : Read file \"filename\" from offset to the amount of bytes specified")
        print('\n')
        
        print('\033[1m' + "write(w)" + '\033[0m' + " (\033[4mfilename\033[0m, \033[4moffset(int)\033[0m, \033[4mContents\033[0m)")
        print(" : Write \"Contents\" on offset on file \"filename\"")
        print('\n')
        
        print('\033[1m' + "monitor(m)" + '\033[0m' + " (\033[4mfilename\033[0m, \033[4mDuration(int)\033[0m)")
        print(" : Monitor the change / update in file \"filename\" for \"Duration\" amount of time")
        print('\n')
        
        print('\033[1m' + "rename(f)" + '\033[0m' + " (\033[4mfilename\033[0m, \033[4mnew-file-name\033[0m)")
        print(" : Rename an existing file to \"new file name\"")
        print('\n')
        
        print('\033[1m' + "replace(p)" + '\033[0m' + " (\033[4mfilename\033[0m, \033[4moffset(int)\033[0m, \033[4mContents\033[0m)")
        print(" : Replace what is on file \"filename\" with \"Contents\" from offset")
        print('\n')
        
        print('\033[1m' + "create(n)" + '\033[0m' + " (\033[4mfilename\033[0m, \033[4mContents\033[0m)")
        print(" : Create a file with name \"filename\" with contents \"Contents\"")
        print(" : If creating empty file, leave \"Contents\" as blank")
        print('\n')
        
        print('\033[1m' + "erase(e)" + '\033[0m' + " (\033[4mfilename\033[0m, \033[4moffset(int)\033[0m, \033[4mbytes-to-erase(int)\033[0m)")
        print(" : Erase the contents on file \"filename\" from offset to \"bytes to erase\"")
        print('\n')
        
        print('\033[1m' + "delete(d)" + '\033[0m' + " (\033[4mfilename\033[0m)")
        print(" : Delete file \"filename\"")
        print('\n')
        
        print('\033[1m' + "cache(c)" + '\033[0m')
        print(" : List all files in Cache")
        print('\n')
        
        print('\033[1m' + "server(s)" + '\033[0m')
        print(" : List all files in Server Directory")
        print('\n')
        
        print('\033[1m' + "time(t)" + '\033[0m')
        print(" : Display current time")
        print('\n')
        
        print('\033[1m' + "help(h)" + '\033[0m')
        print(" : Display help table")
        print('\n')
        
        print('\033[1m' + "quit(q)" + '\033[0m')
        print(" : Terminate the client program")
        print('\n')
        
    def __start__(self):
        print('\n' + '\033[1m' + "================== Welcome to the Client Side ==================" + '\033[0m')
        print("\nThe client will be able to send request to: ")
        print("Server: " + '\033[1m' + self.host_ + '\033[0m' + "\t Port: " + '\033[1m' + str(self.port_) + '\033[0m' + "\n")
        print("The following are the available request from client to server: \n")
        self.__help__()
        request = ""
        while True:
            request = input("\nRequest: ")
            if request == None:
                print("Need Request")
            elif request == 'read' or request == 'r':
                filename = input("Filename: ")
                offset = self.__check_input_type__("Offset (int): ",int)
                b2r = self.__check_input_type__(
                    "Number of Bytes to read (int): ",int)
                client.__READ__(filename,offset,b2r)
            elif request == 'write' or request == 'w':
                filename = input("Filename: ")
                offset = self.__check_input_type__("Offset (int): ",int)
                b2w = input("Contents to insert: ")
                client.__WRITE__(filename,offset,b2w)
            elif request == 'monitor' or request == 'm':
                filename = input("Filename: ")
                time = self.__check_input_type__(
                    "Monitoring time (second) (int): ",int)
                client.__MONITOR__(filename,time)    
            elif request == 'rename' or request == 'f':
                filename = input("Filename: ")
                new_name = input("New Filename: ")
                client.__RENAME__(filename,new_name)
            elif request == 'replace' or request == 'p':
                filename = input("Filename: ")
                offset = self.__check_input_type__("Offset (int): ",int)
                text = input("Replace to: ")
                client.__REPLACE__(filename,offset,text)
            elif request == 'create' or request == 'n':
                filename = input("Filename: ")
                content = input("Content: ")
                client.__CREATE__(filename,content)
            elif request == "delete" or request == 'd':
                filename = input("Filename: ")
                client.__DELETE__(filename)
            elif request == "erase" or request == 'e':
                filename = input("Filename: ")
                offset = self.__check_input_type__("Offset (int): ",int)
                b2e = self.__check_input_type__(
                    "Number of Bytes to erase (int): ",int)
                client.__ERASE__(filename,offset,b2e)    
            elif request == "cache" or request == 'c':
                self.cache_.__LS__()
            elif request == "time" or request == "t":
                self.cache_.__get_time__()
            elif request == "server" or request == 's':
                client.__LS__()
            elif request == 'help' or request == 'h':
                self.__help__()
            elif request == "quit" or request == 'q':
                print("\n=============== Good bye ===============\n")
                break
            else:
                print("No such request")
                
    def __check_input_type__(self,text,input_type):
        inp = ""
        while True:
            inp = input(text)
            try:
                inp = int(inp)
                break
            except ValueError:
                print("The value must be %s" % (input_type))
                continue
        return inp
            

if __name__ == "__main__":
    server_name = 'e-csy'
    port = 9999
    cache_dir = "/home/csy/Documents/git/Remote_File_Server/cache/"
    client = Client(server_name,port,cache_dir)
    client.__start__()
    
    # args = client.__get_args__()
    # client.__process_args__(args)
    
