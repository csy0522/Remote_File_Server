#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 02:16:41 2020

@author: csy
"""


import socket
from client_cache import Client_Cache
import select
import argparse
from mar_unmar_shall import __marshall__ as __mar__
from mar_unmar_shall import __unmarshall__ as __unmar__

TIMEOUT = 10
STATUS = {
    1:"-------------------- \033[1;32;40mSUCCEEDED\033[0m --------------------",
    0: "-------------------- \033[1;31;40mFAILED\033[0m --------------------",
    2: "-------------------- \033[1;33;40mTIMEOUT\033[0m --------------------",
    3: "-------------------- \033[1;36;40mCOMPLETE\033[0m --------------------"
    }
SERV_OP = {
    'read': "READ",'r':"READ",
    'write': "WRITE",'w':"WRITE",
    'monitor': "MONITOR", 'm': "MONITOR",
    'rename': "RENAME", 'x': "RENAME",
    'replace': "REPLACE", 'p': "REPLACE",
    'create': "CREATE", 'n': "CREATE",
    'delete': "DELETE", 'd': "DELETE",
    'erase': "ERASE", 'e': "ERASE",
    'server': "LS", 's': "LS",
    'quit': "DISAPPEAR", 'q': "DISAPPEAR"
    }
CLI_OP = {
    'cache': "CACHE", 'c': "CACHE",
    'time': "TIME", 't': "TIME",
    'help': "HELP", 'h': "HELP"    
    }
FUNC_INPUT = {
    "READ": [["Filename: ",str],["Offset (int): ", int],
             ["Number of Bytes to read (\'-1\' to read till the end) (int): ",int]],
    "WRITE": [["Filename: ",str],["Offset (int): ", int],
             ["Contents to insert: ",str]],
    "MONITOR": [["Filename: ",str],["Monitoring time (second) (int): ", int]],
    "RENAME": [["Filename: ",str],["New Filename: ", str]],
    "REPLACE": [["Filename: ",str],["Offset (int): ", int],["Replace to: ",str]],
    "CREATE": [["Filename: ",str],["Content(default: empty-file): ", str]],
    "DELETE": [["Filename: ",str]],
    "ERASE": [["Filename: ",str],["Offset (int): ", int],
             ["Number of Bytes to erase (\'-1\' to read till the end) (int): ",int]],
    "LS": [],
    "DISAPPEAR": [],
    "CACHE": [],
    "TIME": [],
    "HELP": []
    }


'''
This class creates a client for the user to gain the access of the local server directory
specified with the hostname and the port number later in the main functino.
It allows the user to access and modify files in the local server directory with
operations provided by the server.
'''
class Client:

    def __init__(self,host,port):
        self.host_ = host
        self.port_ = port
        self.socket_ = self.__create_socket__()
        self.cache_ = self.__create_cache__()
        self.server_ = (self.host_, self.port_)
        self.server_addr_ = None
        self.request_ = ""
        self.inputs_ = []
        self.status_ = 0
        self.one_copy_semantics_ = ""


    '''
    This operation allows the users to print 
    a file from offset till the number of bytes specified.
    If the file is available in the cache, the client will
    read it off directly from cache.
    '''
    def __READ__(self):
        if self.cache_.__data_exist__(
            self.inputs_[0],self.inputs_[1],self.inputs_[2]) == True:
            self.__from_cache__(
                self.inputs_[0],SERV_OP[self.request_])
            self.cache_.__READ__(
                self.inputs_[0],self.inputs_[1],self.inputs_[2])
            self.status_ = 1
        else:
            self.__send__(SERV_OP[self.request_])
            for i in self.inputs_:
                self.__send__(i)
            response = self.__receive__(p=False)
            print("\n%s" % (__unmar__(response)))
            if self.status_ == 2 or self.status_ == None: return
            self.status_ = __unmar__(self.__receive__(p=False),int)
            if self.status_ == 2 or self.status_ == None: return
            if self.status_ == 1:
                self.cache_.__add__(
                    self.inputs_[0],__unmar__(response),
                    self.inputs_[1],self.inputs_[1]+len(__unmar__(response)))
            



    '''
    This operation allows the users to insert 
    a string starting from the offset.
    If the file is available in cache,
    the client will modify the file in cache,
    and request an update to the server.
    '''
    def __WRITE__(self):
        if self.cache_.__data_exist__(
            self.inputs_[0],self.inputs_[1]) == True:
            self.__from_cache__(
                self.inputs_[0],SERV_OP[self.request_])
            self.cache_.__WRITE__(
                self.inputs_[0],self.inputs_[1],self.inputs_[2])
        
        self.__send__(SERV_OP[self.request_])
        for i in self.inputs_:
            self.__send__(i)
            
        self.__receive__()
        if self.status_ == 2 or self.status_ == None: return
        self.status_ = __unmar__(self.__receive__(p=False),int)
        if self.status_ == 2 or self.status_ == None: return




    '''
    This operation allows the users to "observe" the updates / changes
    made to a specific file during a period of time.
    '''
    def __MONITOR__(self):
        self.__send__(SERV_OP[self.request_])
        for i in self.inputs_:
            self.__send__(i)
        self.__monitoring__()
        self.status_ = __unmar__(self.__receive__(p=False),int)
        if self.status_ == 2 or self.status_ == None: return

    '''
    This is an assistnant function for MONITOR operation.
    It constantly receives the updates / changes of the file specified.
    '''
    def __monitoring__(self):
        self.__receive__()
        if self.status_ == 2 or self.status_ == None: return
        while True:
            if __unmar__(self.__receive__(p=False),int) == 1:
                self.__receive__()
                if self.status_ == 2 or self.status_ == None: return
                self.__receive__()
                if self.status_ == 2 or self.status_ == None: return
            else:
                self.__receive__()
                if self.status_ == 2 or self.status_ == None: return
                break





    '''
    This operation allows the users to rename
    a file specified.
    If the file is available in cache,
    the client will update the name of the file in cache,
    and request an update to the server.
    '''
    def __RENAME__(self):
        if self.cache_.__data_exist__(self.inputs_[0]) == True:
            self.__from_cache__(
                self.inputs_[0],SERV_OP[self.request_])
            self.cache_.__RENAME__(
                self.inputs_[0],self.inputs_[1])

        self.__send__(SERV_OP[self.request_])
        for i in self.inputs_:
            self.__send__(i)

        self.__receive__()
        if self.status_ == 2 or self.status_ == None: return
        self.status_ = __unmar__(self.__receive__(p=False),int)
        if self.status_ == 2 or self.status_ == None: return








    '''
    This operation allows the users to replace
    a part of content with another string specified from the offset.
    If the file is available in cache,
    the client will update the file in cache,
    and request and update to the server.
    '''
    def __REPLACE__(self):
        if self.cache_.__data_exist__(
            self.inputs_[0],self.inputs_[1]) == True:
            self.__from_cache__(
                self.inputs_[0],SERV_OP[self.request_])
            self.cache_.__REPLACE__(
                self.inputs_[0],self.inputs_[1],self.inputs_[2])
            
        self.__send__(SERV_OP[self.request_])
        for i in self.inputs_:
            self.__send__(i)

        self.__receive__()
        if self.status_ == 2 or self.status_ == None: return
        self.status_ = __unmar__(self.__receive__(p=False),int)
        if self.status_ == 2 or self.status_ == None: return



    '''
    This operation allows the users to create
    new files in the local server directory.
    If the file the user tries to creates already
    exists in the directory, the client will ask
    the user if the user wants to replace it.
    '''
    def __CREATE__(self):
        self.__send__(SERV_OP[self.request_])
        for i in self.inputs_:
            self.__send__(i)

        if __unmar__(self.__receive__(p=False),int) == 1:
            self.__overwrite__(self.inputs_[1])
            
        self.__receive__()
        if self.status_ == 2 or self.status_ == None: return
        self.status_ = __unmar__(self.__receive__(p=False),int)
        if self.status_ == 2 or self.status_ == None: return




    '''
    This is an assistant function for the CREATE operation.
    It asks the users if they want to overwrite a file.
    '''
    def __overwrite__(self,content):
        answer = input(
            __unmar__(self.__receive__(p=False)))
        if self.status_ == 2 or self.status_ == None: return
        self.__send__(answer)
        if answer == ""\
        or answer.lower() == 'y'\
        or answer.lower() == 'yes':
            self.__send__(content)
            



    '''
    This operation allows the users to erase
    a chunk of string starting from the offset to the number of bytes specified.
    If the file is available in cache,
    the client will modify the file in cache,
    and request an update to the server.
    '''
    def __ERASE__(self):
        if self.cache_.__data_exist__(
            self.inputs_[0],self.inputs_[1]) == True:
            self.__from_cache__(
                self.inputs_[0],SERV_OP[self.request_])
            self.cache_.__ERASE__(
                self.inputs_[0],self.inputs_[1],self.inputs_[2])

        self.__send__(SERV_OP[self.request_])
        for i in self.inputs_:
            self.__send__(i)
            
        self.__receive__()
        if self.status_ == 2 or self.status_ == None: return
        self.status_ = __unmar__(self.__receive__(p=False),int)
        if self.status_ == 2 or self.status_ == None: return


    '''
    This operation allows the users to remove
    a file from the local server directory.
    '''
    def __DELETE__(self):
        self.__send__(SERV_OP[self.request_])
        for i in self.inputs_:
            self.__send__(i)

        self.__receive__()
        if self.status_ == 2 or self.status_ == None: return
        self.status_ = __unmar__(self.__receive__(p=False),int)
        if self.status_ == 2 or self.status_ == None: return



    '''
    This operation allows the users to see
    every available files in the local server directory.
    '''
    def __LS__(self):
        self.__send__(SERV_OP[self.request_])
        self.__receive__()
        if self.status_ == 2 or self.status_ == None: return
        self.status_ = __unmar__(self.__receive__(p=False),int)
        if self.status_ == 2 or self.status_ == None: return


    '''
    This operation allows the users to remove
    the clients from the "clients list",
    and exit the program.
    '''
    def __DISAPPEAR__(self):
        self.__send__(SERV_OP[self.request_])
        print("\n" + 
                "======================= " + 
                '\033[1m' + "GOOD BYE" + '\033[0m' + 
                " =======================" + 
                "\n")
        self.status_ = __unmar__(self.__receive__(p=False),int)
        if self.status_ == 2 or self.status_ == None: return
        exit()



    def __CACHE__(self):
        self.cache_.__LS__()
        self.status_ = 1

    def __TIME__(self):
        self.cache_.__get_time__()
        self.status_ = 1

    def __HELP__(self):
        self.__help__()
        self.status_ = 1

    


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
        cache = Client_Cache(socket.gethostbyname(socket.gethostname()))
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
    This function calculates a optimal bufsize for a message
    to be sent to the clients.
    '''   
    def __get_bufsize__(self,msg):
        k = 1
        while k < len(msg):
            k = k * 2
        return k



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
    This function asks the user the inputs based on the request
    '''
    def __get_inputs__(self):

        inputs = []
        for i in FUNC_INPUT[SERV_OP[self.request_]]:
            ip = ''
            if i[1] == int:
                while True:
                    ip = input(i[0])
                    try:
                        ip = int(ip)
                        break
                    except ValueError:
                        print("The value must be %s" % (i[1]))
                        continue
            else:
                ip = input(i[0])

            inputs.append(ip)
        return inputs





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
    This function gets arguments.
    Since this was designed for a back-up plan,
    it will not be used for this project.
    '''
    def __get_args__(self):
        parser = argparse.ArgumentParser(
            description="The Invocation Semantics for Server/Client System.")
        parser.add_argument("Semantics",nargs='?',
            help="request comment to the server")
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
        if args.Semantics == None:
            print("You need to specify the invocation semantics.")
            print("Type '--help' for help")
        elif args.Semantics == "alo":
            self.__alo__()
        elif args.Semantics == "amo":
            self.__amo__()






    '''
    This function starts the client.
    Since the client is in a while loop,
    it will continuously ask user for inputs.
    '''
    def __alo__(self):
        print('\n' + '\033[1m' + "================== Welcome to the Client Side ==================" + '\033[0m')
        print("\nThe client will be able to send request to: ")
        print("Server: " + '\033[1m' + self.host_ + '\033[0m' + "\t Port: " + '\033[1m' + str(self.port_) + '\033[0m' + "\n")
        print("The following are the available request from client to server: \n")
        self.__help__()
        while True:
            self.status_ = 0
            self.request_ = input("\nEnter your request: ")
            if self.request_ not in SERV_OP:
                if self.request_ not in CLI_OP:
                    print("\nNo Such Operation.\nPlease Enter Again.")
                    continue
                else:
                    eval("self.__" + CLI_OP[self.request_] + "__")()
                    print(STATUS[self.status_])
            else:
                self.inputs_ = self.__get_inputs__()
                eval("self.__" + SERV_OP[self.request_] + "__")()
                while self.status_ == 2:
                    print(STATUS[self.status_])
                    print("\nRequesting Again...")
                    eval("self.__" + SERV_OP[self.request_] + "__")()
                    
                print(STATUS[self.status_])





    '''
    This function starts the client.
    Since the client is in a while loop,
    it will continuously ask user for inputs.
    '''
    def __amo__(self):
        print('\n' + '\033[1m' + "================== Welcome to the Client Side ==================" + '\033[0m')
        print("\nThe client will be able to send request to: ")
        print("Server: " + '\033[1m' + self.host_ + '\033[0m' + "\t Port: " + '\033[1m' + str(self.port_) + '\033[0m' + "\n")
        print("The following are the available request from client to server: \n")
        self.__help__()
        while True:
            self.status_ = 0
            self.request_ = input("\nEnter your request: ")
            if self.request_ not in SERV_OP:
                if self.request_ not in CLI_OP:
                    print("\nNo Such Operation.\nPlease Enter Again.")
                    continue
                else:
                    eval("self.__" + CLI_OP[self.request_] + "__")()
                    print(STATUS[self.status_])
            else:
                self.inputs_ = self.__get_inputs__()
                eval("self.__" + SERV_OP[self.request_] + "__")()
                print(STATUS[self.status_])



                



'''
Before running, please specify:
    1. Server name
    2. Port Number
    3. Cache_Directory
'''    
if __name__ == "__main__":
    server_name = 'e-csy'
    port = 9999
    
    client = Client(server_name,port)

    args = client.__get_args__()
    client.__process_args__(args)
    


















