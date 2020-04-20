#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 23:15:40 2020
@author: csy
"""

import os
from datetime import datetime
from datetime import timedelta
import threading
import time
import copy

CACHE_CLIENT_FILE = "Cache_Client_History.txt"
LOG_FILE = "Cache_Log.txt"
DATA_DIR = "../data/"
CUR = datetime.now()

'''
This class creates a cache for the client.
It saves the file requested by the client in order to
increase the speed of reading and to opearte certain semantics.
The cache for each client is in a dictionary form.
'''
class Client_Cache:
    
    def __init__(self,client):
        self.storage_ = dict()
        self.history_ = self.__create_file__(DATA_DIR,CACHE_CLIENT_FILE)
        self.logfile_ = self.__create_file__(DATA_DIR,LOG_FILE)
        self.client_ = client
        self.time_out_ = 20
        self.client_req_ = None
        self.rename_ = None
        self.one_copy_semantics_ = None
        self.time_thread_ = threading.Thread(target=self.__update_time__,daemon=True)
        self.time_thread_.start()
        
    '''
    The client reads the "filename" from cache
    if the file exists in the cache.
    '''
    def __READ__(self,filename,offset,b2r):
        offset_,content_,b2r_,last_index_,_ = self.storage_[filename]
        if b2r == -1:
            b2r = last_index_
        print(self.storage_[filename][1][offset-offset_:b2r-offset])
        self.__update_history__("READ",filename,success=True)
    

    '''
    This operation allows the client to see
    all the existing files in cache.
    '''
    def __LS__(self):
        print("\nList all files in Cache")
        print('\n================= CACHE =================')
        for k,v in self.storage_.items():
            print("\t%s" % (k))
        print('================= END =================\n')

    def __LSL__(self):
        print("\nList all files in Cache")
        print('\n================= CACHE =================')
        for k,v in self.storage_.items():
            print("\t%s" % (k))
            print("\t- %s\n" % (v[1]))
        print('================= END =================\n')



    '''
    This function adds a data / file into the dictionary cache.
    '''
    def __add__(self,key,content,offset,b2r,last_index):
        self.storage_[key] = [offset,content,b2r,last_index,CUR+timedelta(seconds=self.time_out_)]
        self.__update_log__(key,"Created")



    '''
    This function removes a data / file from the dictionary cache.
    '''
    def __del__(self,key):
        self.__update_log__(key,"Deleted")
        del self.storage_[key]


    
    '''
    This function checks if a data / file exists in the cache directory.
    '''    
    def __data_exist__(self,data,offset=None,b2r=None):
        if data in self.storage_:
            if offset == None:
                return True
            offset_,content_,b2r_,last_index_,_ = self.storage_[data]
            if offset >= offset_ and offset <= b2r_:
                if b2r != None:
                    if b2r == -1:
                        b2r = last_index_
                    if b2r <= b2r_:
                        return True
                    else:
                        return False
                return True
        return False
    
    '''
    This function creates a file in the directory specified
    only if the file does not exist in the directory.
    '''
    def __create_file__(self,directory,filename,content=None):
        if self.__file_exist__(directory,filename):
            existing = open(directory+filename)
            existing.close()
            return existing
        else:
            new_file = open(directory+CACHE_CLIENT_FILE,'w')
            if content != None:
                new_file.write(content)
                new_file.close()
            else:
                new_file.close()
                return new_file

            
    '''
    This function checks if the 'filename' exists
    in the directory specified.
    '''
    def __file_exist__(self,directory,filename):
        return os.path.isfile(directory+filename)
            

    
    '''
    This function constantly updates the current time.
    '''
    def __update_time__(self):
        global CUR
        while True:
            CUR = datetime.now()
            self.__update_cache__()
            time.sleep(0.1)



    '''
    This function updates the content in the client_cache
    through one copy semantics.
    '''
    def __one_copy_semantics__(self):
        if self.client_req_ in ["WRITE","REPLACE","ERASE","RENAME"]:
            offset_,ori_content_,b2r_,last_index_,_ = self.storage_[self.one_copy_semantics_[0]]
            if self.client_req_ == "RENAME":
                if self.one_copy_semantics_[0] != self.one_copy_semantics_[1]:
                    print("File %s changed to %s in Cache through One_Copy_Semantics" % (
                        self.one_copy_semantics_[0],self.one_copy_semantics_[1]))
                    self.__del__(self.one_copy_semantics_[0])
                    self.__add__(self.one_copy_semantics_[1],ori_content_,offset_,b2r_,last_index_)
                    self.__update_history__(self.client_req_,self.one_copy_semantics_[0],success=True)
                    self.__update_log__(
                        self.one_copy_semantics_[0],"Modified from %s Operation" % (self.client_req_))
            else:
                last_index_ = len(self.one_copy_semantics_[1])
                if ori_content_ != self.one_copy_semantics_[1][offset_:b2r_]:
                    print("File %s updated in Cache through One_Copy_Semantics" % (
                        self.one_copy_semantics_[0]))
                    ori_content_ = self.one_copy_semantics_[1][offset_:b2r_]
                    self.__update_history__(self.client_req_,self.one_copy_semantics_[0],success=True)
                    self.__update_log__(
                        self.one_copy_semantics_[0],"Modified from %s Operation" % (self.client_req_))
                self.__add__(self.one_copy_semantics_[0],ori_content_,offset_,b2r_,last_index_)
        self.__one_copy_semantics_reset__()



    '''
    This function resets variables needed
    for one copy semantics procedure.
    '''
    def __one_copy_semantics_reset__(self):
        self.client_req_ = None
        self.one_copy_semantics_ = None

    
    '''
    This function sycs the cache directory.
    A file is removed from the cahce
    after a certain period of time.
    '''
    def __update_cache__(self):
        global CUR
        for k,v in list(self.storage_.items()):
            if v[4] < CUR:
                self.__del__(k)
            else:
                if self.one_copy_semantics_ != None:
                    self.__one_copy_semantics__()



    '''
    Thie function writes down a log
    for the cache.
    '''
    def __update_log__(self,key,what):
        global CUR
        self.logfile_ = open(DATA_DIR+LOG_FILE,'a')
        self.logfile_.write("File: " + key + 
                            '\t' + what + '\t' + 
                            CUR.strftime("%Y-%m-%d %H:%M:%S")+"\n")
        self.logfile_.close()

        
    '''
    This function gets the current time.
    '''
    def __get_time__(self):
        global CUR
        print("\n========== CURRENT TIME ==========\n")
        print('\t' + CUR.strftime("%Y-%m-%d %H:%M:%S"))
        print("\n=====================================")



    def __get_current_time__(self):
        global CUR
        return CUR


    '''
    This function records and updates the history
    from the operation the client requested
    '''
    def __update_history__(self,request,filename,success):
        succ = "Failed"
        if success == True:
            succ = "Succeed"
        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history_ = open(DATA_DIR+CACHE_CLIENT_FILE,'a')
        self.history_.write("Client: " + self.client_ +
                            "\tRequest: " + request + "\"" + 
                            filename + "\"\t" + succ + "\t" + curr_time + '\n')
        self.history_.close()
        
        
