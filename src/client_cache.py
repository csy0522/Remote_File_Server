from fcache.cache import FileCache


class Client_Cache:

    def __init__(self,dir_name,path):
        self.dir_name_ = dir_name
        self.dir_path_ = path
        self.cache_ = self.__create_cache__()


    def __create_cache__(self):
        cache = FileCache(appname=self.dir_name_,app_cache_dir=self.dir_path_)
        return cache


    def __add__(self,file,content):
        self.cache_[file] = content
        self.__sync__()


    def __del__(self,file):
        if not self.__exist__():
            return "The file does not exist in Cache"
        del self.cache_[file]
        self.cache
        self.__sync__()



    def __exist__(self,file):
        return file in self.cache_


    def __READ__(self,file,offset,b2r):
        value =self.cache_.get(file)
        if value == None:
            return "The file does not exist in Cache"
        elif offset > len(self.cache_.get(file)):
            return "The \"offset\" exceeded the length of content."
        elif offset+b2r > len(self.cache_.get(file)):
            return "The length of bytes to read from the offset \
exceeded the length of content"
        return self.cache_.get(file)[offset:offset+b2r]



    def __WRITE__(self,file,offset,b2w):
        value =self.cache_.get(file)
        if value == None:
            return "The file does not exist in Cache"
        elif offset > len(self.cache_.get(file)):
            return "The \"offset\" exceeded the length of content."
        new_content = self.cache_.get(file)[:offset] + \
            b2w + self.cache_.get(file)[offset:]
        self.cache_[file] = new_content
        self.__sync__()
        return self.cache_.get(file)
        
    

    def __cwd__(self):
        return self.cache_.cache_dir+"\\"



    
    def __sync__(self):
        self.cache_.sync()


    
    
    
    
    



