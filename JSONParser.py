import json
import logging
import utils
from listOfConsepts import ListOfConsepts
from consept import Term 

logger = logging.getLogger('JSONParser')
hdlr = logging.FileHandler('/tmp/myapp.log')
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)

class JSONParser(object):
    """A customer of ABC Bank with a checking account. Customers have the
    following properties:

    Attributes:
        name: A string representing the customer's name.
        balance: A float tracking the current balance of the customer's account.
    """

    def __init__(self):
        """Return a Customer object whose name is *name* and starting
        balance is *balance*."""
                 #logging detup

    def is_empty(self, document):
        """Return the balance remaining after withdrawing *amount*
        dollars."""
        if document == None:
            return True
        return False


    def retrieveField(self, document, field):
        res = None
        if field in document:
            res = document[field]
        return res

    def appendMatchesC(self, data, id, label, type, freqs):
        if data == None:
            data = ListOfConsepts()
        dataValue = None
        
        consept = data.getConseptByName(label)
        if consept != None:
            pass #update consept frequency and add new links
        else:
            consept = Term(label, type)
            consept._addNewLink(id, source, sourceLabel)
            data._addTerm(consept)
        
        if label in data:
            if id==data[label]:
                freqs[label]+=1
                return data, freqs
            else:
                freqs[label]=1
            dataValue = list(data[label])
        elif not (label in data):
            dataValue = list()
            #data[label] = list()
        dataValue.append(id)
        #data[label].append(id)
        data[label] = dataValue
        return data, freqs    

    def appendMatches(self, data, id, label, freqs):
        dataValue = None
        if label in data:
            if id==data[label]:
                return data #, freqs
            dataValue = data[label]
        else:
            dataValue = []
            
        dataValue.append(id)
        if label in data:
            logger.info("addition target "+label+":"+str(data[label]))
        data[label] = dataValue
        return data
    
    def appendMatchArrays(self, dictionary, key, matches):
        if dictionary == None:
            dictionary = dict()
        if not(key in dictionary):
            data = dict()
        else:
            data = dictionary[key]
        
        for match in matches:
            for matchKey in match:
                dataValue = None
                if matchKey in data:
                    if match[matchKey]==data[matchKey]:
                        continue
                    dataValue = data[matchKey]
                elif not (matchKey in data):
                    dataValue = []
                dataValue.append(match[matchKey])
                data[matchKey] = dataValue
            
        dictionary[key]=data
        return dictionary[key]

    def parse_article(self, results, article, type, source, stopwords):
        articleMap = []
        freqs = dict()
        
        try:
            for result in results:
                try:
                    decoded = json.loads(result)
                except TypeError:
                    decoded = result
                
                if not(self.is_empty(decoded)):         
                        id = self.retrieveField(decoded, 'id')
                        label = self.retrieveField(decoded, 'label')
                        matchingForm = self.retrieveField(decoded, 'matches')
                        if label == "Laki":
                            print("Printing stopwords:")
                            print(stopwords)
                        if id != None and label !=None and (label not in stopwords and label.lower() not in stopwords):
                            article.addTerm(label, id,type, source, matchingForm)
                                                            
                        else:
                            logger.debug("No data exists, empty result")
                 
                else:
                    logger.debug("empty results")  
        except (ValueError, KeyError, TypeError) as err:
            logger.debug("JSON format error")
            logger.debug(err)
            err.print_stack()
        except Exception as e:
            logger.debug("Unknown error")
            logger.debug(e)
            err.print_stack()
            
        combinedData = None#utils.combineDataToFreqs(data, freqs)
        return article, combinedData

    def retrieveData(self, document):
        data = None
        res = self.retrieveField(document, 'arpafied')
        if self.is_empty(res) == False:
            logger.info(str(res))
            data = self.retrieveField(res, 'results')
        return data

    def parse(self, input_magazines, all_magazines, arpaName, arpaURL, stopwordlist, keyWords=None, keyWordFreqs=None):
        """Return the balance remaining after depositing *amount*
        dollars."""
        #input_magazines = '{ "one": 1, "two": { "list": [ {"item":"A"},{"item":"B"} ] } }' 
        
        if keyWordFreqs==None:
            keyWordFreqs = dict()
        
        if keyWords==None:
            keyWords = dict()
            
        try:
            for mId, magazine in enumerate(input_magazines):
                articles = magazine.get_articles()
                articleAmount = len(articles)
                logger.info("Processing "+str(articleAmount)+ " articles")
                for aId,article in enumerate(articles):
                    counter = 0
                    queryresults = article.get_query_result()
                    for entity in queryresults:
                        counter+=1
                        results = self.retrieveData(entity)
                        if results == None:
                            logger.debug("nothing to process, processing failed for article "+article.get_title()+"! ")
                            logger.debug(entity)
                            res = self.retrieveField(entity, 'arpafied')
                            logger.debug(res)
                        else:
                            article, combined = self.parse_article(results, article, arpaName, arpaURL, stopwordlist)
                            articles[aId]=article
                input_magazines[mId]=magazine
        except (ValueError, KeyError, TypeError) as err:
            logger.debug("JSON format error")
            logger.debug(err)
            err.print_stack()
        
        return input_magazines, keyWordFreqs
