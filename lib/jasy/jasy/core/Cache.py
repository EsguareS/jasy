#
# Jasy - JavaScript Tooling Framework
# Copyright 2010-2011 Sebastian Werner
#

import shelve, time, logging, os, os.path, sys, pickle

class Cache:
    """ 
    A cache class based on shelve feature of Python. 
    Supports transient only in-memory storage, too.
    """
    
    def __init__(self, path, clear=False):
        self.__transient = {}
        self.__file = os.path.join(path, "cache")
        
        logging.debug("Cache File: %s" % self.__file)
        
        try:
            logging.debug("Open cache file %s..." % self.__file)
            self.__db = shelve.open(self.__file)
        except:
            logging.warn("Detected faulty cache files. Rebuilding...")
            self.clear()
    
    
    def clear(self):
        if hasattr(self, "__db"):
            self.__db.close()

        logging.debug("Initialize cache file %s..." % self.__file)
        
        self.__db.close()
        self.__db = shelve.open(self.__file, flag="n")
        
        
    def read(self, key, timestamp=None):
        """ 
        Reads the given value from cache.
         
        Optional timestamp value checks wether the value was stored 
        after the given time to be valid.
        """
        
        if key in self.__transient:
            return self.__transient[key]
        
        timeKey = key + "-timestamp"
        if key in self.__db and timeKey in self.__db:
            if not timestamp or timestamp <= self.__db[timeKey]:
                value = self.__db[key]
                
                # Useful to debug serialized size. Often a performance
                # issue when data gets to big.
                # rePacked = pickle.dumps(value)
                # print("LEN: %s = %s" % (key, len(rePacked)))
                
                # Copy over value to in-memory cache
                self.__transient[key] = value
                return value
                
        return None
        
    
    def store(self, key, value, timestamp=None, transient=False):
        """
        Stores the given value.
        
        Default timestamp goes to the current time. Can be modified
        to the time of an other files modification date etc.
        """
        
        self.__transient[key] = value
        if transient:
            return
        
        if not timestamp:
            timestamp = time.time()
        
        try:
            self.__db[key+"-timestamp"] = timestamp
            self.__db[key] = value
        except pickle.PicklingError as err:
            logging.error("Failed to store enty: %s" % key)

        
    def sync(self):
        """ Syncs the internal storage database """
        self.__db.sync() 
      
      
    def close(self):
        """ Closes the internal storage database """
        self.__db.close()         
        
      