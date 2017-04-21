
import traceback
import logging, sys
from consept import Term 
from conseptLink import Consept
from decorator import append

logger = logging.getLogger('ListofConsepts')
hdlr = logging.FileHandler('/tmp/terms.log')
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)

class ListOfConsepts(object):
    def __init__(self):
        self._consepts = list()
        self._ranked_consepts = list()
        self._consept_map = dict()

    def get_ranked_consepts(self):
        return sorted(self._ranked_consepts)

    def get_consepts(self):
        return sorted(self._consepts)
    def set_consept_map(m):
        self._consept_map =m

    def get_consept_map():
        return self._consept_map

    def set_ranked_consepts(self, value):
        self._ranked_consepts = value
    def set_consepts(self, value):
        self._consepts = value

    def del_consepts(self):
        del self._consepts

    def updateConseptMap(self, label, index):
        for c in self._consept_map:
            if label in self._consept_map[c]:
                map_value = self._consept_map[c]
                for value in map_value.split(','):
                    if value == label:
                        value = index
                    values=values+','+value
                self._consept_map[c] = values

    def addOrUpdateTerm(self, label, link, type, source, newForm, article_id):
        logger.debug("Recieved this consept "+label+" ("+str(newForm)+") : "+link)
        consept, id = self.getConseptByName(label)
        if consept == None:
            logger.debug("NOT FOUND, ADD NEW TERM "+label+" : "+link)
            index = ""
            #check if there is a related consept, if not create new id 
            related = self.getRelatedConsept(newForm)
            problem = list()
            if related != None:
                for node in related:
                    if len(index) > 0 and node.getIndex() != index:
                        logger.warn("Problematic issue with index. This term "+str(index)+" related to more than one term.")
                        problem.append(node)
                    elif len(index) == 0 and node.getIndex() != index:
                        problem.append(node)
                    index = node.getIndex()
                if len(problem) > 1:
                    logger.warn("Problems listed: "+str(problem))
                    for p in problem:
                        logger.warn(p)
            if related == None or len(index)<1:
                index = article_id+"_"+str(len(self._consepts)+1)

            #self.updateConseptMap(label, index)
            self._addNewTerm(label, link, type, source, index, newForm)
            #self._consepts.append(consept)
        else:
            cLink = Consept(link.strip())
            consept.insertOrUpdateLink(cLink)
            consept._incrementFrequency(1)
            self._consepts[id]=consept
            forms=consept.getForms()
            if forms != None:
                if newForm not in forms:
                    consept._addForm(newForm)
            else:
                forms = list()
                forms.append(newForm)
                consept._addForm(forms)
            
    def _addTerm(self, label, links, type, index, newForm):
        c = Term(label=label, type=type, index=index, forms=newForm)
        c._addLinks(links)
        self._consepts.append(c)
        
    def _addNewTerm(self, label, link, type, source, index, newForm):
        c = Term(label=label, type=type, index=index, forms=newForm)
        c._addNewLink(link, source, type)
        if c != None:
            self._consepts.append(c)
        else:
            logger.debug("PRODUCED NONE for "+label + " : "+link)

    #creates a map that uses the index as a key. for each key there is a list of consepts.
    def getAllConseptsByIndex(self):
        allConsepts = dict()
        try:
            if self._consepts == None:
                return None
            for id,consept in enumerate(self._consepts):
                index= consept.getIndex()
                if index in allConsepts:
                    if consept not in allConsepts[index]:
                        allConsepts[index].append(consept)
                else:
                    allConsepts[index] = list()
                    allConsepts[index].append(consept)
        except Exception as e:
            logger.error(e, exc_info=True)
            return None
        return allConsepts

    def getAllIndexesByForm(self):
        allConsepts = dict()
        try:
            if self._consepts == None:
                return None
            for id,consept in enumerate(self._consepts):
                index= consept.getIndex()
                original_forms = consept.getForms()
                for original_form in original_forms:
                    if original_form in allConsepts:
                        if index not in allConsepts[original_form]:
                            allConsepts[original_form].append(index)
                    else:
                        allConsepts[original_form] = list()
                        allConsepts[original_form].append(index)
        except Exception as e:
            logger.error(e, exc_info=True)
            return None
        return allConsepts


    #creates a list of consepts for a index.
    def searchConseptsByIndex(self, index):
        consepts=list()
        try:
            if self._consepts == None:
                return None
            for id,consept in enumerate(self.get_consepts()):
                if consept.getIndex() == index:
                    consepts.append(consept)
        except Exception as e:
            logger.error(e, exc_info=True)
            #logger.error(sys.exc_traceback.tb_lineno)
            return None
        return consepts

    def findIndexForForm(self, form):
        c = self.getRelatedConsept(form)
        return c.getIndex()

    #get related consept by comparing their forms.
    #label - term from text that is being linked to a consept
    #return - returns a consept that has been linked to similar term in the text. These text terms are listed in term's forms.
    def getRelatedConsept(self, labelList):
        try:
            if self._consepts == None:
                logger.info("empty list of consepts. index failed")
                return None
            consepts=list()
            for label in labelList:
                for id,consept in enumerate(self._consepts):
                    if consept not in consepts and consept.compareForms(label) == True:
                        consepts.append(consept)
            return consepts
        except Exception as e:
            logger.error(e, exc_info=True)
            #logger.error(sys.exc_traceback.tb_lineno)
        return None
    def getConseptByName(self, label):
        try:
            if self._consepts == None:
                return None, 0
            for id,consept in enumerate(self.get_consepts()):
                if consept._compareLabels(label):
                    return consept,id
        except Exception as e:
            logger.error(e,exc_info=True)
            #logger.error(sys.exc_traceback.tb_lineno)
        return None, 0
    def getConseptByForm(self, form):
        try:
            c = list()
            if self._consepts == None:
                return None, 0
            for id,consept in enumerate(self.get_consepts()):
                if consept.compareForms(form):
                    c.append(consept)
            return c
        except Exception as e:
            logger.error(e, exc_info=True)
            #logger.error(sys.exc_traceback.tb_lineno)
        return None
    def getTerm(self, searchedConsept):
        for consept in self._consepts:
            if consept == searchedConsept:
                return consept
        return None
    
    def __sizeof__(self):
        return len(self._consepts)
    
    def __repr__(self):
        return "Consepts [ "+len(self._consepts)+" ]"
    
    def __str__(self):
        return "Containing "+len(self._consepts)+" consepts"
    
    def logConseptsByIndex(self):
        allConsepts = self.getAllConseptsByIndex()
        for index in allConsepts:
            logger.info(index)
            for i in allConsepts[index]:
                logger.info(" -- "+str(i))


    def logListOfConsepts(self):
        for consept in self.get_consepts():
            logger.debug(consept)    
