import logging
from conseptLink import Consept

logger = logging.getLogger('Term')
hdlr = logging.FileHandler('/tmp/terms.log')
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)

class Term(object):

    def __init__(self, label="", type="", frequency=1, links=None, w=0, index=0, forms=None):
        self._id = index
        self._label = label
        self._type = type
        self._frequency=frequency
        self._weight=w
        self._links=links
        self._forms=forms
        self.setForms(forms)
        self.setLinks(links)
        #print(self)
    
    def getLabel(self):
        return self._label
    
    def setIndex(self, index):
        if len(index) > 0:
            logger.info("Changing index ("+str(index)+") for "+str(self)+".")
            self._id=index
        else:
            logger.info("Trying to add an index ("+str(index)+") with lenght less than zero for "+str(self)+".")

    def getIndex(self):
        return self._id

    def getWeight(self):
        return self._weight
    
    def setWeight(self, w):
        self._weight=w        
            
    def setForms(self, form):
        logger.info("setting form to index "+str(form))
        if form == None:
            self._forms = list()
        else:
            if type(form) is list:
                self._forms == form
            else:
                self._forms.append(form)
        
    def setLinks(self, links):
        if links == None:
            self._links = list()
        else:
            self._links = links
            
    def getLinks(self):
        return sorted(self._links)
    
    def retrieve_link_uris(self):
        links = self.getLinks()
        
        if len(links) > 0:
            
            uris = list()
            for link in links:
                l = link.get_link()
                uris.append(l)
            return uris
        else:
            return None
    
    def getType(self):
        return self._type
    
    def getForms(self):
        return self._forms
        
    def _getLabel(self):
        return self._label
    
    def _compareLabels(self, label):
        if (self._label.lower().strip()) == (label.lower().strip()):
            return True
        return False
    def getConnectingForm(self, label):
        for f in self._forms:
            if (f.lower().strip()) == (label.lower().strip()):
                return f
        return None
    def compareForms(self, label):
        logger.info("Searching for "+label)
        logger.info("From "+str(self._forms))
        if self._forms == None or label not in self._forms:
            return False
        for f in self._forms:
            logger.info("Compare: "+str(f)+ " == "+str(label))
            if (f.lower().strip()) == (label.lower().strip()):
                logger.info("Found: "+f+ " == "+label)
                return True
        return False
 
    def _combineConsepts(self, parConsept):
        self._incrementFrequency(parConsept.get_frequency())
        self._addLinks(parConsept.get_links())


    def insertOrUpdateLink(self, link):
        if link not in self._links:
            self._links.append(link)
        else:
            self._updateLink(link)

    def _addLinks(self, links):
        for link in links:
            self.insertOrUpdateLink(link)
        
    def _addLink(self, link):
        self._links.append(link)
        
    def _addForm(self, newForm):
        if self._forms == None:
            self.setForms(newForm)
        else:
            for form in newForm:
                if form not in self._forms:
                    self._forms.append(form)
        
    def _addNewLink(self, linkLabel, source, sourceName):
        link = Consept(linkLabel,1, source, sourceName)
        self._addLink(link)
        
        
    def _incrementFrequency(self, increment=1):
        self._frequency=int(self._frequency)+int(increment)
        
    def _updateLink(self, pLink):
        for cLink in self._links:
            if isinstance(pLink, Consept):
                if cLink == pLink:
                    cLink.incrementFrequency(1)
                    return
            else:
                if cLink.get_link() == pLink:
                    cLink.incrementFrequency(1)
                    return
            
    def get_frequency(self):
        return self._frequency
    
    def get_links(self):
        return self._links
        
    def __cmp__(self, other):
        if hasattr(other, 'frequency'):
            return self._frequency.__cmp__(other.get_frequency())
    
    def __repr__(self):
        return self._id+" "+self._label.upper()+ " ("+str(self._frequency)+","+str(self._weight)+") " + self._type
    
    def __str__(self):
        return self._id+" "+self._label.upper()+ " ( "+str(self._frequency)+" )" + str(self._forms)
    
    def __eq__(self, other):
        if not(isinstance(other, Term)):
            return False
        if other == None:
            return False
        if self._label == other.getLabel():
            if self._frequency == other.get_frequency():
                if self.get_links() == other.get_links():
                    return True
        return False     
    
    def __gt__(self, other):
        if hasattr(other, 'frequency'):
            return self._frequency.__gt__(other.get_frequency())
        return False
    
    def __lt__(self, other):
        if hasattr(other, 'frequency'):
            return self._frequency.__lt__(other.get_frequency())
        return False
    
    def list_of_consepts(self, onlyTop=False, limit=0):
        str1=""
        if onlyTop == False:
            for link in self.get_links():
                if link != None:
                    logger.debug(link)
        else:
            for link in self.get_links():
                if link != None:
                    if link.get_frequency()>limit:
                        logger.debug(link)
        return str1
    
    def logConsept(self, topTermOnly=False, topOnly=False, limit=0):
        if topTermOnly == False:
            logger.debug(self)
            self.list_of_consepts(topOnly, limit)
        else:
            if self._frequency>limit:
                logger.debug(self)
                self.list_of_consepts(topOnly, limit)
                
    def logTerm(self):
        logger.debug(self)
