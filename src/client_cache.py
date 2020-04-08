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

CACHE_CLIENT_FILE = "Cache_Client_history.txt"
LOG_FILE = "Cache_log.txt"
DATA_DIR = "../data/"
CUR = datetime.now()
CACHE_TIME = 60

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
        self.time_thread_ = threading.Thread(target=self.__update_time__,daemon=True)
        self.time_thread_.start()
        
    '''
    The client reads the "filename" from cache
    if the file exists in the cache.
    '''
    def __READ__(self,filename,offset,b2r):
        offset_,content_,last_index_,_ = self.storage_[filename]
        if b2r == -1:
            b2r = last_index_ - offset
        print(self.storage_[filename][1][offset-offset_:offset-offset_+b2r])
        self.__update_history__("READ",filename,success=True)
    
    '''
    The client writes the "filename" from cache
    if the file exists in the cache.
    '''
    def __WRITE__(self,filename,offset,b2w):
        offset_,content,last_index_,_ = self.storage_[filename]
        new_content = self.storage_[filename][1][:offset-offset_]+\
            b2w+self.storage_[filename][1][offset-offset_:]
        self.storage_[filename] = [offset_,new_content,last_index_+len(b2w),_]
        self.__update_history__("WRITE",filename,success=True)
        self.__update_log__(filename,"Modified from Write Operation")
        print("Cache File:\n" + new_content)

    '''
    The client renames the "filename" from cache
    if the file exists in the cache.
    '''
    def __RENAME__(self,filename,name):
        offset_,content,last_index_,_ = self.storage_[filename]
        self.__del__(filename)
        self.__add__(name,content,offset_,last_index_)
        self.__update_history__("RENAME",filename,success=True)
        self.__update_log__(filename,"Modified from Rename Operation")

    '''
    The client replaces the "filename" from cache
    if the file exists in the cache.
    '''
    def __REPLACE__(self,filename,offset,b2w):
        offset_,content,last_index_,_ = self.storage_[filename]
        new_content = self.storage_[filename][1][:offset-offset_]+\
            b2w+self.storage_[filename][1][offset-offset_+len(b2w):]
        if offset-offset_+len(b2w) > last_index_:
            last_index_ = offset-offset_+len(b2w)
        self.storage_[filename] = [offset_,new_content,last_index_,_]
        self.__update_history__("REPLACE",filename,success=True)
        self.__update_log__(filename,"Modified from Replace Operation")
        print("Cache File:\n" + new_content)

    '''
    The client erases the "filename" from cache
    if the file exists in the cache.
    '''
    def __ERASE__(self,filename,offset,b2e):
        offset_,content,last_index_,_ = self.storage_[filename]
        new_content = self.storage_[filename][1][:offset-offset_]+\
            self.storage_[filename][1][offset-offset_+b2e:]
        last_index_ = last_index_ - b2e
        self.storage_[filename] = [offset_,new_content,last_index_,_]
        self.__update_history__("ERASE",filename,success=True)
        self.__update_log__(filename,"Modified from Erase Operation")
        print("Cache File:\n" + new_content)

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

    '''
    This function adds a data / file into the dictionary cache.
    '''
    def __add__(self,key,content,offset,last_index):
        self.storage_[key] = [offset,content,last_index,CUR+timedelta(seconds=CACHE_TIME)]
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
            offset_,content_,last_index_, _ = self.storage_[data]
            if offset >= offset_ and offset <= last_index_:
                if b2r != None:
                    if offset+b2r <= last_index_:
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
            time.sleep(0.5)
            
    
    '''
    This function sycs the cache directory.
    A file is removed from the cahce
    after a certain period of time.
    '''
    def __update_cache__(self):
        global CUR
        for k,v in list(self.storage_.items()):
            if v[3] < CUR:
                self.__del__(k)
    
    '''
    Thie function writes down a log
    for the cache.
    '''
    def __update_log__(self,key,what):
        global CUR
        self.logfile_ = open(DATA_DIR+LOG_FILE,'a')
        self.logfile_.write("File: " + key + 
                            # '\tContent: ' + self.storage_[key][1] + 
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
        
        
