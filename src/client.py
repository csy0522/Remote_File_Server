#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 02:16:41 2020

@author: csy
"""


import socket
from client_cache import Client_Cache
import argparse
import select
from mar_unmar_shall import __marshall__ as __mar__
from mar_unmar_shall import __unmarshall__ as __unmar__

STATUS = {1:"\033[1;32;40mSUCCEEDED\033[0m",
          0: "\033[1;31;40mFAILED\033[0m",
          2: "\033[1;33;40mTIMEOUT\033[0m"}
TIMEOUT = 60

'''
This class creates a client for the user to gain the access of the local server directory
specified with the hostname and the port number later in the main functino.
It allows the user to access and modify files in the local server directory with
operations provided by the server.
'''
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
        self.status_ = 0
        self.request___ = ""
        self.one_copy_semantics_ = ""
    
    '''
    This operation allows the users to print 
    a file from offset till the number of bytes specified.
    If the file is available in the cache, the client will
    read it off directly from cache.
    '''
    def __READ__(self, pathname, offset, b2r):
        self.client_req_ = "READ"
        if self.cache_.__data_exist__(pathname,offset,b2r) == True:
            self.__from_cache__(pathname,self.client_req_)
            self.cache_.__READ__(pathname,offset,b2r)
            self.status_ = 1
        else:
            self.__send__(self.client_req_)
            self.__send__(pathname)
            self.pass_req_ = self.__receive__(p=False)
            if self.status_ == 2: return
            if __unmar__(self.pass_req_,int) == 1:
                self.__receive__()
                if self.status_ == 2: return
                self.__send__(offset)
                self.__send__(b2r)
                self.__receive__()
                if self.status_ == 2: return
                self.__receive__()
                if self.status_ == 2: return
                response = self.__receive__()
                if self.status_ == 2: return
                success = self.__receive__(p=False)
                if self.status_ == 2: return
                if __unmar__(success,int) == 1:
                    b2r = len(__unmar__(response)) - offset
                    self.cache_.__add__(
                        pathname,__unmar__(response),
                        offset,offset+b2r)
                    self.status_ = 1
            elif __unmar__(self.pass_req_,int) == 0:
                self.__receive__()
                if self.status_ == 2: return


    '''
    This operation allows the users to insert 
    a string starting from the offset.
    If the file is available in cache,
    the client will modify the file in cache,
    and request an update to the server.
    '''
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
            if self.status_ == 2: return
            self.status_ = 1
        else:
            self.__send__(1)
            self.__send__(pathname)
            self.pass_req_ = self.__receive__(p=False)
            if self.status_ == 2: return
            if __unmar__(self.pass_req_,int) == 1:
                self.__receive__()
                if self.status_ == 2: return
                self.__send__(offset)
                self.__send__(b2w)
                self.__receive__()
                if self.status_ == 2: return
                self.__receive__()
                if self.status_ == 2: return
                self.__receive__()
                if self.status_ == 2: return
                success = self.__receive__(p=False)
                if self.status_ == 2: return
                self.status_ = __unmar__(success,int)
            elif __unmar__(self.pass_req_,int) == 0:
                self.__receive__()
                if self.status_ == 2: return
    
    
    '''
    This operation allows the users to "observe" the updates / changes
    made to a specific file during a period of time.
    '''
    def __MONITOR__(self, pathname, length):
        self.client_req_ = "MONITOR"
        self.__send__(self.client_req_)
        self.__send__(pathname)
        self.pass_req_ = self.__receive__(p=False)
        if self.status_ == 2: return
        if __unmar__(self.pass_req_,int) == 1:
            self.__receive__()
            if self.status_ == 2: return
            self.__send__(length)
            self.__receive__()
            if self.status_ == 2: return
            self.__receive__()
            if self.status_ == 2: return
            self.__receive__()
            if self.status_ == 2: return
            self.__receive__()
            if self.status_ == 2: return
            while True:
                response = self.__receive__(p=False)
                if self.status_ == 2: return
                if __unmar__(response,int) == 1:
                    self.__receive__()
                    if self.status_ == 2: return
                    self.__receive__()
                    if self.status_ == 2: return
                elif __unmar__(response,int) == 0:
                    self.__receive__()
                    if self.status_ == 2: return
                    break
            self.status_ = 1
        elif __unmar__(self.pass_req_,int) == 0:
            self.__receive__()
            if self.status_ == 2: return


    '''
    This operation allows the users to rename
    a file specified.
    If the file is available in cache,
    the client will update the name of the file in cache,
    and request an update to the server.
    '''
    def __RENAME__(self,pathname,name):
        self.client_req_ = "RENAME"
        self.__send__(self.client_req_)
        if self.cache_.__data_exist__(pathname) == True:
            self.__from_cache__(pathname,self.client_req_)
            self.cache_.__RENAME__(pathname,name)
            self.__send__(0)
            self.__send__(pathname)
            self.__send__(name)
            self.__receive__()
            if self.status_ == 2: return
            self.status_ = 1
        else:
            self.__send__(1)
            self.__send__(pathname)
            self.pass_req_ = self.__receive__(p=False)
            if self.status_ == 2: return
            if __unmar__(self.pass_req_,int) == 1:
                self.__receive__()
                if self.status_ == 2: return
                self.__send__(name)
                self.__receive__()
                if self.status_ == 2: return
                self.__receive__()
                if self.status_ == 2: return
                success = self.__receive__(p=False)
                if self.status_ == 2: return
                self.status_ = __unmar__(success,int)
            elif __unmar__(self.pass_req_,int) == 0:
                self.__receive__()
                if self.status_ == 2: return
            
            
    '''
    This operation allows the users to replace
    a part of content with another string specified from the offset.
    If the file is available in cache,
    the client will update the file in cache,
    and request and update to the server.
    '''
    def __REPLACE__(self,pathname,offset,b2w):
        self.client_req_ = "REPLACE"
        self.__send__(self.client_req_)
        if self.cache_.__data_exist__(pathname,offset) == True:
            self.__from_cache__(pathname,self.client_req_)
            self.cache_.__REPLACE__(pathname,offset,b2w)
            self.__send__(0)
            self.__send__(pathname)
            self.__send__(offset)
            self.__send__(b2w)
            self.__receive__()
            if self.status_ == 2: return
            self.status_ = 1
        else:
            self.__send__(1)
            self.__send__(pathname)
            self.pass_req_ = self.__receive__(p=False)
            if self.status_ == 2: return
            if __unmar__(self.pass_req_,int) == 1:
                self.__receive__()
                if self.status_ == 2: return
                self.__send__(offset)
                self.__send__(b2w)
                self.__receive__()
                if self.status_ == 2: return
                self.__receive__()
                if self.status_ == 2: return
                self.__receive__()
                if self.status_ == 2: return
                success = self.__receive__(p=False)
                if self.status_ == 2: return
                self.status_ = __unmar__(success,int)
            elif __unmar__(self.pass_req_,int) == 0:
                self.__receive__()
                if self.status_ == 2: return


    '''
    This operation allows the users to create
    new files in the local server directory.
    If the file the user tries to creates already
    exists in the directory, the client will ask
    the user if the user wants to replace it.
    '''
    def __CREATE__(self,pathname,content):
        self.client_req_ = "CREATE"
        self.__send__(self.client_req_)
        self.__send__(pathname)
        self.__receive__()
        if self.status_ == 2: return
        self.pass_req_ = self.__receive__(p=False)
        if self.status_ == 2: return
        
        if __unmar__(self.pass_req_,int) == 0:
            self.__receive__()
            if self.status_ == 2: return
            e = self.__receive__(p=False)
            if self.status_ == 2: return
            if __unmar__(e,int) == 1:
                self.__overwrite__(content)
            else:
                self.__send__(content)
                self.status_ = 1
        elif __unmar__(self.pass_req_,int) == 2:
            self.__overwrite__(content)
        elif __unmar__(self.pass_req_,int) == 1:
            self.__send__(content)
            self.status_ = 1
            
    '''
    This is an assistant function for the CREATE operation.
    It asks the users if they want to overwrite a file.
    '''
    def __overwrite__(self,content):
        answer = input(
            __unmar__(self.__receive__(p=False)))
        if self.status_ == 2: return
        self.__send__(answer)
        if answer == ""\
        or answer.lower() == 'y'\
        or answer.lower() == 'yes':
            self.__send__(content)
            self.status_ = 1


    '''
    This operation allows the users to erase
    a chunk of string starting from the offset to the number of bytes specified.
    If the file is available in cache,
    the client will modify the file in cache,
    and request an update to the server.
    '''
    def __ERASE__(self,pathname,offset,b2e):
        self.client_req_ = "ERASE"
        self.__send__(self.client_req_)
        if self.cache_.__data_exist__(pathname,offset) == True:
            self.__from_cache__(pathname,self.client_req_)
            self.cache_.__ERASE__(pathname,offset,b2e)
            self.__send__(0)
            self.__send__(pathname)
            self.__send__(offset)
            self.__send__(b2e)
            self.__receive__()
            if self.status_ == 2: return
            self.status_ = 1
        else:
            self.__send__(1)
            self.__send__(pathname)
            self.pass_req_ = self.__receive__(p=False)
            if self.status_ == 2: return
            if __unmar__(self.pass_req_,int) == 1:
                self.__receive__()
                if self.status_ == 2: return
                self.__send__(offset)
                self.__send__(b2e)
                self.__receive__()
                if self.status_ == 2: return
                self.__receive__()
                if self.status_ == 2: return
                self.__receive__()
                if self.status_ == 2: return
                success = self.__receive__(p=False)
                if self.status_ == 2: return
                self.status_ = __unmar__(success,int)
            elif __unmar__(self.pass_req_,int) == 0:
                self.__receive__()
                if self.status_ == 2: return


    '''
    This operation allows the users to remove
    a file from the local server directory.
    '''
    def __DELETE__(self,pathname):
        self.client_req_ = "DELETE"
        self.__send__(self.client_req_)
        self.__send__(pathname)
        self.pass_req_ = self.__receive__(p=False)
        if self.status_ == 2: return
        if __unmar__(self.pass_req_,int) == 1:
            self.__receive__()
            if self.status_ == 2: return
            self.status_ = 1
        elif __unmar__(self.pass_req_,int) == 0:
            self.__receive__()
            if self.status_ == 2: return

    '''
    This operation allows the users to see
    every available files in the local server directory.
    '''
    def __LS__(self):
        self.client_req_ = "LS"
        self.__send__(self.client_req_)
        self.__receive__()
        if self.status_ == 2: return
        self.__receive__()
        if self.status_ == 2: return
        self.status_ = 1
        
        
    '''
    This operation allows the users to remove
    the clients from the "clients list",
    and exit the program.
    '''
    def __DISAPPEAR__(self):
        self.client_req_ = "DISAPPEAR"
        self.__send__(self.client_req_)
        
        print("\n" + 
                "======================= " + 
                '\033[1m' + "GOOD BYE" + '\033[0m' + 
                " =======================" + 
                "\n")
        

    '''
    This function updates the file that exists
    in cache of all the clients.
    It is executed when one file is updated through any client.
    '''
    def __one_copy_semantics__(self):        
        pathname = __unmar__(self.__receive__())
        offset = __unmar__(self.__receive__(),int)
        b2w = __unmar__(self.__receive__())
        
        if self.cache_.__data_exist__(pathname,offset) == True:
            self.__from_cache__(pathname,self.client_req_)
            self.cache_.__WRITE__(pathname,offset,b2w)
            self.status_ = 1
        else:
            print("file does not exist")
        
        
    '''
    This function creates a new UDP socket for the client.
    '''
    def __create_socket__(self):
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        return sock
    
    '''
    This function creates client-side cache for the client.
    '''
    def __create_cache__(self):
        cache = Client_Cache(socket.gethostbyname(socket.gethostname()),self.cache_dir_)
        return cache
    
    '''
    This function sends the message / request to the server.
    '''
    def __send__(self,msg):
        if type(msg) == int:
            msg = str(msg)
        bufsize = self.__get_bufsize__(msg)
        self.socket_.sendto(__mar__(bufsize),self.server_)
        self.socket_.sendto(__mar__(msg),self.server_)
        
       
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
    This function receives a message sent by the client.
    An optimal bufsize is received first, and the message is received
    based on the optimal bufsize.
    if timeout, return a specific value for status update.
    '''
    def __receive__(self,p=True):
        timeout = select.select([self.socket_],[],[],TIMEOUT)
        if timeout[0]:
            bufsize,self.server_addr_ = self.socket_.recvfrom(12)
            msg, self.server_addr_ = self.socket_.recvfrom(__unmar__(bufsize,int))
            if p == True:
                print(__unmar__(msg))
            return msg
        else:
            self.status_ = 2
    
    '''
    This function checks if a file / data
    exists in the cache.
    '''
    def __check_cache__(self,data):
        return self.cache_.__data_exist__(data)
    
    '''
    This function simply prints the status of the cache
    '''
    def __from_cache__(self,filename,command):
        c1 = "The file \"%s\" exists in Cache!" % (
            filename)
        c2 = "%s \"%s\" from Cache..." % (
            command,filename)
        print('\n' + c1 + '\n' + c2 + '\n')
        
        
    '''
    This function checks the input type.
    It checks whether the input is an integer.
    '''
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
        
        
    '''
    This function gets arguments.
    Since this was designed for a back-up plan,
    it will not be used for this project.
    '''
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
    
    '''
    This function checks arguments.
    Since this was designed for a back-up plan,
    it will not be used for this project.
    '''
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
        
        
    '''
    This function processes arguments.
    Since this was designed for a back-up plan,
    it will not be used for this project.
    '''
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
                
                
    '''
    This function prints the guidance for the users
    '''
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
        
        print('\033[1m' + "rename(x)" + '\033[0m' + " (\033[4mfilename\033[0m, \033[4mnew-file-name\033[0m)")
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
        
        
    '''
    This function starts the client and asks the user to input the operation.
    This function will continue until the user types 'quit' or 'q' to quit the program.
    '''
    def __start__(self):
        print('\n' + '\033[1m' + "================== Welcome to the Client Side ==================" + '\033[0m')
        print("\nThe client will be able to send request to: ")
        print("Server: " + '\033[1m' + self.host_ + '\033[0m' + "\t Port: " + '\033[1m' + str(self.port_) + '\033[0m' + "\n")
        print("The following are the available request from client to server: \n")
        self.__help__()
        while True:
            self.status_ = 0
            try:
                self.request_ = input("\nEnter your request: ")
            except:
                self.__one_copy_semantics__()
            if self.request_ == None:
                print("Need Request")
            elif self.request_ == 'read' or self.request_ == 'r':
                filename = input("Filename: ")
                offset = self.__check_input_type__("Offset (int): ",int)
                b2r = self.__check_input_type__(
                    "Number of Bytes to read (\'-1\' to read till the end) (int): ",int)
                # client.__READ__(filename,offset,b2r)
                self.__READ__(filename,offset,b2r)
            elif self.request_ == 'write' or self.request_ == 'w':
                filename = input("Filename: ")
                offset = self.__check_input_type__("Offset (int): ",int)
                b2w = input("Contents to insert: ")
                self.__WRITE__(filename,offset,b2w)
                
            elif self.request_ == 'monitor' or self.request_ == 'm':
                filename = input("Filename: ")
                time = self.__check_input_type__(
                    "Monitoring time (second) (int): ",int)
                while time >= TIMEOUT:
                    print("\nMonitoring Time cannot be longer than \"Timeout\" - Currently set to \"%d\"." % (
                        TIMEOUT))
                    print("Please Enter a smaller number.\n")
                    time = self.__check_input_type__(
                        "Monitoring time (second) (int): ",int)
                self.__MONITOR__(filename,time)  
                
            elif self.request_ == 'rename' or self.request_ == 'x':
                filename = input("Filename: ")
                new_name = input("New Filename: ")
                self.__RENAME__(filename,new_name)

            elif self.request_ == 'replace' or self.request_ == 'p':
                filename = input("Filename: ")
                offset = self.__check_input_type__("Offset (int): ",int)
                text = input("Replace to: ")
                self.__REPLACE__(filename,offset,text)

            elif self.request_ == 'create' or self.request_ == 'n':
                filename = input("Filename: ")
                content = input("Content(default: empty-file): ")
                self.__CREATE__(filename,content)

            elif self.request_ == "delete" or self.request_ == 'd':
                filename = input("Filename: ")
                self.__DELETE__(filename)

            elif self.request_ == "erase" or self.request_ == 'e':
                filename = input("Filename: ")
                offset = self.__check_input_type__("Offset (int): ",int)
                b2e = self.__check_input_type__(
                    "Number of Bytes to erase (\'-1\' to read till the end) (int): ",int)
                self.__ERASE__(filename,offset,b2e)

            elif self.request_ == "server" or self.request_ == 's':
                self.__LS__()
                self.status_ = 1
                
            elif self.request_ == "quit" or self.request_ == 'q':
                self.__DISAPPEAR__()
                self.status_ = 1
                break
            
            elif self.request_ == "cache" or self.request_ == 'c':
                self.cache_.__LS__()
                self.status_ = 1
                
            elif self.request_ == "time" or self.request_ == "t":
                self.cache_.__get_time__()
                self.status_ = 1
                
            elif self.request_ == 'help' or self.request_ == 'h':
                self.__help__()
                self.status_ = 1
                
            elif self.request_ == "allc":
                self.__ALLC__()
                
            else:
                print("\nNo Such Operation.\nPlease Enter Again.")
                
            print("-------------------- %s --------------------" % (
                STATUS[self.status_]))

    
'''
Before running, please specify:
    1. Server name
    2. Port Number
    3. Cache_Directory
'''    
if __name__ == "__main__":
    server_name = 'e-csy'
    port = 9999
    cache_directory = "/home/csy/Documents/git/Remote_File_Server/cache/"
    
    client = Client(server_name,port,cache_directory)
    
    client.__start__()

    
