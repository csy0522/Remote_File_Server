#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 02:16:41 2020

@author: csy
"""


import sys
import socket
from client_cache import Client_Cache
import select
import argparse
import threading
import time
from datetime import datetime
from datetime import timedelta
from mar_unmar_shall import __marshall__ as __mar__
from mar_unmar_shall import __unmarshall__ as __unmar__

TIMEOUT = 60
STATUS = {
    1:"-------------------- \033[1;32;40mSUCCEEDED\033[0m --------------------",
    0: "-------------------- \033[1;31;40mFAILED\033[0m --------------------",
    2: "-------------------- \033[1;33;40mTIMEOUT\033[0m --------------------",
    3: "-------------------- \033[1;36;40mCOMPLETE\033[0m --------------------",
    None: "-------------------- \033[1;31;40mReturned None\033[0m --------------------",
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


SD = "/home/csy/Documents/git/Remote_File_Server/Server_Directory/"


'''
This class creates a client for the user to gain the access of the local server directory
specified with the hostname and the port number later in the main functino.
It allows the user to access and modify files in the local server directory with
operations provided by the server.
'''
class Client:

    def __init__(self):
        self.host_ = None
        self.port_ = None
        self.server_ = None
        self.server_addr_ = None
        self.socket_ = self.__create_socket__()
        self.cache_ = self.__create_cache__()
        self.inputs_ = []
        self.request_ = ""
        self.semantics_ = ''
        self.one_copy_semantics_ = ""
        self.status_ = 0



    '''
    This function updates the file that exists
    in cache of all the clients.
    It is executed when one file is updated through any client.
    '''
    def __one_copy_semantics__(self):
        if self.cache_.__data_exist__(pathname,offset) == True:
            self.__from_cache__(pathname,self.client_req_)
            self.cache_.__WRITE__(pathname,offset,b2w)
            self.status_ = 1
        else:
            print("file does not exist")
            


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
            response = self.__receive__()
            if self.status_ == 2 or self.status_ == None: return
            self.status_ = self.__receive__(int,False)
            if self.status_ == 2 or self.status_ == None: return
            if self.status_ == 1:
                self.cache_.__add__(
                    self.inputs_[0],response,
                    self.inputs_[1],self.inputs_[1]+len(response))
                self.cache_.server_dir_ = self.__receive__(p=False)
            



    '''
    This operation allows the users to insert 
    a string starting from the offset.
    If the file is available in cache,
    the client will modify the file in cache,
    and request an update to the server.
    '''
    def __WRITE__(self):
        self.__send__(SERV_OP[self.request_])
        for i in self.inputs_:
            self.__send__(i)
            
        self.__receive__()
        if self.status_ == 2 or self.status_ == None: return
        self.status_ = self.__receive__(int,False)
        if self.status_ == 2 or self.status_ == None: return





    '''
    This operation allows the users to "observe" the updates / changes
    made to a specific file during a period of time.
    '''
    def __MONITOR__(self):
        self.__send__(SERV_OP[self.request_])
        for i in self.inputs_:
            self.__send__(i)
        if self.__receive__(int,False) == 1:
            if self.__receive__(int,False) == 1:

                serv_dir = self.__receive__(p=False)
                
                ori_file = open(serv_dir+self.inputs_[0])
                ori_content = ori_file.read()
                ori_file.close()

                self.__monitoring__(serv_dir,self.inputs_[0],self.inputs_[1],ori_content)
                self.status_ = 1
            else:
                self.__receive__()
                if self.status_ == 2 or self.status_ == None: return
        else:
            self.__receive__()
            if self.status_ == 2 or self.status_ == None: return



    '''
    This is an assistnant function for MONITOR operation.
    It constantly receives the updates / changes of the file specified.
    '''
    def __monitoring__(self,serv_dir,filename,mon_time,ori_content):
        des = datetime.now() + timedelta(seconds=mon_time)
        print("\nMonitoring...\n")
        while self.cache_.__get_current_time__() < des:
            try:
                new_file = open(serv_dir+filename)
                new_content = new_file.read()
            except FileNotFoundError:
                print("\nFile \"%s\" is removed...\n" % (filename))
                break
            time.sleep(0.1)
            if ori_content != new_content:
                print("==================================")
                print("File \"%s\" Updated.\n" % (filename))
                print("Updated Content: \n%s" % (new_content))
                print("==================================")
                ori_content = new_content
            new_file.close()
        print("...End of Monitoring.\n")




    '''
    This operation allows the users to rename
    a file specified.
    If the file is available in cache,
    the client will update the name of the file in cache,
    and request an update to the server.
    '''
    def __RENAME__(self):
        self.__send__(SERV_OP[self.request_])
        for i in self.inputs_:
            self.__send__(i)

        self.__receive__()
        if self.status_ == 2 or self.status_ == None: return
        self.status_ = self.__receive__(int,False)
        if self.status_ == 2 or self.status_ == None: return
        if self.status_ == 1:
            self.cache_.rename_ = self.__receive__(p=False)
            if self.status_ == 2 or self.status_ == None: return
    


    '''
    This operation allows the users to replace
    a part of content with another string specified from the offset.
    If the file is available in cache,
    the client will update the file in cache,
    and request and update to the server.
    '''
    def __REPLACE__(self):
        self.__send__(SERV_OP[self.request_])
        for i in self.inputs_:
            self.__send__(i)

        self.__receive__()
        if self.status_ == 2 or self.status_ == None: return
        self.status_ = self.__receive__(int,False)
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

        if self.__receive__(int,False) == 1:
            self.__overwrite__(self.inputs_[1])
            
        self.__receive__()
        if self.status_ == 2 or self.status_ == None: return
        self.status_ = self.__receive__(int,False)
        if self.status_ == 2 or self.status_ == None: return




    '''
    This is an assistant function for the CREATE operation.
    It asks the users if they want to overwrite a file.
    '''
    def __overwrite__(self,content):
        yes = ["","y","yes"]
        answer = input(self.__receive__(p=False))
        if self.status_ == 2 or self.status_ == None: return        
        self.__send__(answer)
        if answer.lower() in yes:
            self.__send__(content)
            


    '''
    This operation allows the users to erase
    a chunk of string starting from the offset to the number of bytes specified.
    If the file is available in cache,
    the client will modify the file in cache,
    and request an update to the server.
    '''
    def __ERASE__(self):
        self.__send__(SERV_OP[self.request_])
        for i in self.inputs_:
            self.__send__(i)
            
        self.__receive__()
        if self.status_ == 2 or self.status_ == None: return
        self.status_ = self.__receive__(int,False)
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
        self.status_ = self.__receive__(int,False)
        if self.status_ == 2 or self.status_ == None: return



    '''
    This operation allows the users to see
    every available files in the local server directory.
    '''
    def __LS__(self):
        self.__send__(SERV_OP[self.request_])
        self.__receive__()
        if self.status_ == 2 or self.status_ == None: return
        self.status_ = self.__receive__(int,False)
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
                '\033[1m' + "GOODBYE" + '\033[0m' + 
                " =======================" + 
                "\n")
        self.status_ = self.__receive__(int,False)
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
    def __receive__(self,d_type=str,p=True):
        timeout = select.select([self.socket_],[],[],TIMEOUT)
        if timeout[0]:
            bufsize,self.server_addr_ = self.socket_.recvfrom(12)
            msg, self.server_addr_ = self.socket_.recvfrom(__unmar__(bufsize,int))
            msg = __unmar__(msg,d_type)
            if p == True and msg != None:
                print("\n%s" % str(msg))
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
    This function asks the user the inputs based on the request
    '''
    def __get_inputs__(self):
        inputs = []
        for i in FUNC_INPUT[SERV_OP[self.request_]]:
            ip = ''
            if i[1] == int:
                ip = self.__check_int_input__(i[0])
            else:
                ip = input(i[0])
            inputs.append(ip)
        return inputs



    def __check_int_input__(self,text):
        q = ['q','quit']
        inp = ''
        while True:
            inp = input(text)
            try:
                inp = int(inp)
                break
            except ValueError:
                if inp.lower() in q:
                    print("\n" + 
                        "======================= " + 
                        '\033[1m' + "GOOD BYE" + '\033[0m' + 
                        " =======================" + 
                        "\n")
                    exit()
                print("The value must be %s" % (int))
                continue
        return inp




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
            description="Specifying the invocation semantics")
        parser.add_argument("Semantics",nargs='?',
            help="The invocation semantics - type 'amo' for At-Most-Once, 'alo' for At-Least-Once.")
        args = parser.parse_args()
        return args






    '''
    This function processes arguments.
    Since this was designed for a back-up plan,
    it will not be used for this project.
    '''
    def __process_args__(self,args):
##        if args.Semantics == "alo":
##            self.semantics_ = "alo"
##            self.__start__()
##        elif args.Semantics == "amo":
##            self.semantics_ = "amo"
##            self.__start__()
        semantics = ['alo','amo']
        if args.Semantics not in semantics:
            if args.Semantics == None:
                print("You need to specify the invocation semantics.")
                print("Type '--help' for help")
            else:
                print("Invalid invocation semantics")
                print("Please type either At-Most-Once or At-Least-Once ('amo'/'alo')")
        else:
            self.semantics_ = args.Semantics
            self.__start__()


    
            

    '''
    This function starts the client.
    Since the client is in a while loop,
    it will continuously ask for input from the user.
    '''
    def __start__(self):
        print('\n' + '\033[1m' + "================== Welcome to the Client Side ==================" + '\033[0m')
        print("\nThis program provides the tool for the user to access the local server directory\n\n")
        self.host_ = input("Enter the address of the host ('q' to quit): ")
        if self.host_.lower() in ['q','quit']:exit()
        self.port_ = self.__check_int_input__("Enter the port number of the host ('q' to quit): ")
##        self.host_ = '192.168.0.103'
##        self.host_ = '192.168.0.104'
##        self.port_ = 9090
        self.server_ = (self.host_, self.port_)
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
                self.cache_.client_req_ = SERV_OP[self.request_]
                if self.semantics_ == "alo":
                    while self.status_ == 2:
                        print(STATUS[self.status_])
                        print("\nRequesting Again...")
                        eval("self.__" + SERV_OP[self.request_] + "__")()
                time.sleep(0.1)
                print(STATUS[self.status_])




'''
Before running, please specify:
    1. Server name
    2. Port Number
    3. Cache_Directory
'''    
if __name__ == "__main__":
    
    client = Client()
    
    args = client.__get_args__()
    client.__process_args__(args)

    

    

  
