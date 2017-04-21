

class Consept(object):
    def __init__(self, link="", frequency=1, source=None, sourceName=""):
        """Return a Customer object whose name is *name* and starting
        balance is *balance*."""
        self.__link=link
        self.__frequency=int(frequency)
        self.__source=source
        self.__sourceName=sourceName

    def get_link(self):
        return self.__link


    def get_frequency(self):
        return self.__frequency


    def set_link(self, value):
        self.__link = value


    def set_frequency(self, value):
        self.__frequency = value


    def del_link(self):
        del self.__link


    def del_frequency(self):
        del self.__frequency

        
    def incrementFrequency(self, increment=1):
        self.__frequency+=increment
        
    def _getFrequency(self):
        return int(self.__frequency)
        
    def __str__(self):
        s = self.__link + " ("+str(self.__frequency)+") "
        return s
    
    def __cmp__(self, other):
        if hasattr(other, 'frequency'):
            return self.__frequency.__cmp__(other.get_frequency())
    
    def __repr__(self):
        return ""+self.__link+ " ( "+str(self.__frequency)+" )"
    
    def __eq__(self, other):
        if not(isinstance(other, Consept)):
            return False
        if other == None:
            return False
        if self.__link == other.get_link():
            return True
        return False     
    
    def __gt__(self, other):
        if hasattr(other, 'frequency'):
            return self.__frequency.__gt__(other.get_frequency())
        return False
    
    def __lt__(self, other):
        if hasattr(other, 'frequency'):
            return self.__frequency.__lt__(other.get_frequency())
        return False    
    link = property(get_link, set_link, del_link, "link's docstring")
    frequency = property(get_frequency, set_frequency, del_frequency, "frequency's docstring")
