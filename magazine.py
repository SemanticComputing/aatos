from listOfConsepts import ListOfConsepts
from consept import Consept 
from conseptLink import Consept
from article import Article
import logging

logger = logging.getLogger('Magazine')
hdlr = logging.FileHandler('/tmp/myapp.log')
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)

class Magazine:
    def __init__(self, name, volume, issue, articles=None):
        self.__volume = volume
        self.__issue = issue
        self.__name = name
        if articles == None:
            self.__articles=list()
        else:
            self.__articles = articles

    def get_name(self):
        return self.__name


    def set_name(self, value):
        self.__name = value


    def del_name(self):
        del self.__name


    def get_volume(self):
        return self.__volume


    def get_issue(self):
        return self.__issue


    def get_articles(self):
        return self.__articles


    def set_volume(self, value):
        self.__volume = value


    def set_issue(self, value):
        self.__issue = value


    def set_articles(self, value):
        self.__articles = value


    def del_volume(self):
        del self.__volume


    def del_issue(self):
        del self.__issue


    def del_articles(self):
        del self.__articles
        
    def add_article(self, article):
        self.__articles.append(article)
        
    def get_article_id(self, article=None):
        str=""
        if article != None:
            postfix = article.get_article_postfix()
            str = self.__volume+"_"+self.__issue+"_"+postfix
        return str
        
    def print_articles(self):
        for article in self.__articles:
            str = self.get_article_id(article)

    def get_article(self, searchedArticle):
        for article in self.__articles:
            if article == searchedArticle:
                return article
        return None
    
    def is_article_in_magazine(self, searchedArticle):
        article = self.get_article(searchedArticle)
        if article != None:
            return True
        return False
    
    def find_article_by_page(self, page):
        close = 0
        closest=0
        item = None
        nearestMatchItem=0
        for article in self.__articles:
            retPage = article.get_page()
            close = int(page) - int(retPage)
            if close >= 0:
                if closest > close or nearestMatchItem == 0:
                    item = article
                    nearestMatchItem=page
                    closest=close
        return item

    def get_article_by_param(self, title="", page=0):
        for article in self.__articles:
            if page > 0 and article.page == page:
                return article
            if len(title)>0 and article.title() == title:
                return article
        return None
    
    def log_articles(self, topConspetsOnly=False, topConspetLinksOnly=False, limit=0):
        logger.debug(self)
        for article in self.__articles:
            article.log_article(topConspetsOnly, topConspetLinksOnly, limit)
            
    def log_article_terms(self):
        logger.debug(self)
        for article in self.__articles:
            article.log_terms()
            
    def log_articles_and_contents(self):
        logger.debug(self)
        for article in self.__articles:
            article.log_article_content()
    
    def __str__(self):
        return self.__name+" Volume : "+self.__volume+" Issue : "+self.__issue
    #def __cmp__(self, other):
    #    if hasattr(other, 'frequency'):
    #        return self._frequency.__cmp__(other.get_frequency())

    def __repr__(self):
        return self.__name+" Volume : "+self.__volume+" Issue : "+self.__issue + " Articles: "+str(len(self.__articles))

    def __eq__(self, other):
        if not(isinstance(other, Magazine)):
            return False
        if other == None:
            return False
        if self.__name == other.get_name():
            if self.__volume == other.get_volume():
                if self.__issue == other.get_issue():
                    return True
        return False

    def __gt__(self, other):
        if self.__volume > other.get_volume():
            return True
        elif self.__issue > other.get_issue() and self.__volume == other.get_volume():
            return True
        return False

    def __lt__(self, other):
        if self.__volume < other.get_volume():
            return True
        elif self.__issue < other.get_issue() and self.__volume == other.get_volume():
            return True
        return False

