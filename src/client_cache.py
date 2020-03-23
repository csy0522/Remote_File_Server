from fcache.cache import FileCache


class Client_Cache:

	def __init__(self,dir_name,path):
		self.dir_name_ = dir_name
		self.dir_path_ = path
		self.cache_ = self.__create_cache__()


	def __create_cache__(self):
		cache = FileCache(appname=self.dir_name_,app_cache_dir=self.dir_path_)
		return cache


	def __add__(self,filename,content):
		self.cache_[filename] = content
		self.__sync__()


#	def __del__(self,filename):
#		try:
#			del self.cache_[filename]
#			self.__sync__()
#		except KeyError:
#			return "The file does not exist in Cache"






	def __exist__(self,filename):
		return filename in self.cache_


	def __READ__(self,filename,offset,b2r):
		value =self.cache_.get(filename)
		if value == None:
			return "The filename does not exist in Cache"
		elif offset > len(self.cache_.get(filename)):
			return "The \"offset\" exceeded the length of content."
		elif offset+b2r > len(self.cache_.get(filename)):
			return "The length of bytes to read from the offset \
exceeded the length of content"
		return self.cache_.get(filename)[offset:offset+b2r]



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


	
	
	
	
	



