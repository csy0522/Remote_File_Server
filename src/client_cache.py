from fcache.cache import FileCache
import os
from datetime import datetime

CACHE_CLIENT_FILE = "Cache_Client_history.txt"
DATA_DIR = '../data/'



class Client_Cache:

    def __init__(self,dir_name,path):
        self.dir_name_ = dir_name
        self.dir_path_ = path
        self.cache_ = self.__create_cache__()
        self.history_ = self.__create_file__(DATA_DIR,CACHE_CLIENT_FILE)





    def __create_cache__(self):
        cache = FileCache(appname=self.dir_name_,app_cache_dir=self.dir_path_)
        return cache





    def __add__(self,filename,content):
        self.cache_[filename] = content
        self.__sync__()





#    def __del__(self,filename):
#        try:
#            del self.cache_[filename]
#            self.__sync__()
#        except KeyError:
#            return "The file does not exist in Cache"
        




    def __create_file__(self,directory,filename,content=None):
        if self.__file_exist__(directory,filename):
            pass
        else:
            new_file = open(directory+CACHE_CLIENT_FILE,'w')
            if content != None:
                new_file.write(content)
                new_file.close()
            else:
                new_file.close()
                return new_file
            




    def __update_history__(self,request,filename,success):
        self.history_ = open(DATA_DIR+CACHE_CLIENT_FILE,'a')
        succ = "Succeed"
        if success == False:
            succ = "Failed"
        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history_.write("Request: " + 
            request + " file \"" + filename + "\" " + 
            succ + "\tTime: " + curr_time + "\n")
        self.history_.close()





    def __file_exist__(self,directory,filename):
        return os.path.isfile(directory+filename)





    def __exist__(self,filename):
        return filename in self.cache_





    def __READ__(self,filename,offset,b2r):
        value =self.cache_.get(self.dir_path_+filename)
        if value == None:
            self.__update_history__("READ",filename,success=False)
            return "The filename does not exist in Cache"
        elif offset > len(self.cache_.get(self.dir_path_+filename)):
            self.__update_history__("READ",filename,success=False)
            return "The \"offset\" exceeded the length of content."
        elif offset+b2r > len(self.cache_.get(self.dir_path_+filename)):
            self.__update_history__("READ",filename,success=False)
            return "The length of bytes to read from the offset \
exceeded the length of content"
        self.__update_history__("READ",filename,success=True)
        return self.cache_.get(self.dir_path_+filename)[offset:offset+b2r]





    def __WRITE__(self,filename,offset,b2w):
        value =self.cache_.get(filename)
        if value == None:
            return "The filename does not exist in Cache"
        elif offset > len(self.cache_.get(filename)):
            return "The \"offset\" exceeded the length of content."
        new_content = self.cache_.get(filename)[:offset] + \
            b2w + self.cache_.get(filename)[offset:]
        self.cache_[filename] = new_content
        self.__sync__()
        return self.cache_.get(filename)
     




    def __cwd__(self):
        return self.cache_.cache_dir+"\\"





    def __sync__(self):
        self.cache_.sync()




