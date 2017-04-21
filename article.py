from listOfConsepts import ListOfConsepts
from textSlice import TextSlice
import logging
import hashlib
logger = logging.getLogger('Article')
hdlr = logging.FileHandler('/tmp/myapp.log')
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)


class Article:

    def __init__(self, title="", page=0, author="", link="", event_type="", texts=None, consepts=None, keywords=None, anno_texts=None):
        self._title = title
        self._page = int(page)
        self._author = author
        self._link = link
        self._query_result = []
        self._event=event_type
        self._texts = None
        self._text_length = 0

        self.set_texts(texts)
        #self.set_annotated_texts(anno_texts)
        self.set_keywords(keywords)
        self.set_consepts(consepts)

    def get_len(self):
        return self._text_length


    def get_id(self):
        return self._link


    def set_len(self, value):
        self._text_length = value


    def set_id(self, value):
        self._link = value


    def get_event(self):
        return self._event


    def set_event(self, value):
        self._event = value


    def del_event(self):
        del self._event


    def get_query_result(self):
        return self._query_result


    def set_query_result(self, value):
        self._query_result = value


    def get_title(self):
        return self._title


    def get_page(self):
        return self._page


    def get_author(self):
        return self._author


    def get_texts(self):
        return self._texts


    def get_keywords(self):
        return self.__keywords


    def get_ranked_consepts(self):
        return self.__consepts

    def get_consepts(self):
        return self.__consepts


    def set_title(self, value):
        self._title = value


    def set_page(self, value):
        self._page = value


    def set_author(self, value):
        self._author = value

    def del_title(self):
        del self._title


    def del_page(self):
        del self._page


    def del_author(self):
        del self._author


    def del_texts(self):
        del self._texts


    def del_keywords(self):
        del self.__keywords


    def del_consepts(self):
        del self.__consepts

    def addText(self, strText, page):
        textSlice = TextSlice(strText, page)
        self._texts.append(textSlice)
        
    def addTerm(self, label, link, type, source, newForm):
        if label != "" and link!= "":
            h = hashlib.md5(self._title.encode())
            article_id = h.hexdigest()
            self.__consepts.addOrUpdateTerm(label, link, type, source, newForm, article_id)
        logger.info("Added consept: "+label+" ("+str(newForm)+") : "+link)
        
    def get_text_by_page(self, page):
        for text in self._texts:
            if text.get_page() == page:
                return text
    
    def get_last_page(self):
        page = self._page
        for text in self._texts:
            if text.get_page() > page:
                page = text.get_page()
        return page
    
    def is_part_of_article(self, page):
        lastPage = self.get_last_page()
        firstPage = self._page
        if page >= firstPage and page <= lastPage:
            return True
        return False
    
    def get_article_postfix(self):
        return "page"+self._page
    
    def __str__(self):
        s ="Title: "+self._title+ " by "+self._author+" on page "+str(self._page)+ " based on events of " +self.get_event()
        return s
    
    def __repr__(self):
        s= ""+self._title+ " by "+self._author+" (p. "+str(self._page)+")"+" based on events of " +self.get_event()
        return s
    
    def __eq__(self, other):
        if isinstance(other, Article):
            return False
        if other == None:
            return False
        if self._author == other.get_author():
            if self._title == other.get_title():
                if self._page == other.get_page():
                    return True
        return False        
    
    def __cmp__(self, other):
        if hasattr(other, 'page'):
            return self._page.__cmp__(other.get_page())

    def set_texts(self, texts):
        if texts == None:
            self._texts = list()
        else:
            self._texts = texts
        
    def set_keywords(self, keywords):
        if keywords == None:
            self.__keywords = list()
            #self.__keywords = Keywords()
        else:
            self.__keywords = keywords
            
    def get_all_consepts(self):
        if self.__consepts != None:
            return self.__consepts.get_consepts()
            
    def set_consepts(self, consepts):
        if consepts == None:
            #self.__consepts = list()
            self.__consepts = ListOfConsepts()
        else:
            self.__consepts = consepts
            
    def log_top10(self):
        self.log_article_names(True, True, 0)
    
    def log_terms(self):
        logger.debug(self)
        for consept in self.__consepts.get_consepts():
            if consept != None:
                consept.logTerm()

    def log_article_names(self, topTermsOnly=False, topLinkOnly=False, limit=0):
        logger.debug(self)
        #print(self.__consepts.get_consepts())
        for consept in self.__consepts.get_consepts():
            if consept != None:
                consept.logConsept(topTermsOnly,topLinkOnly, limit)
            else:
                logger.info(consept)

    def log_article(self, topConseptOnly=False, topConseptLinkOnly=False, limit=0):
        if len(self._texts)>0:
            self.log_article_names(topConseptOnly, topConseptLinkOnly, limit)
            
    def log_article_content(self):
        if len(self._texts)>0:
            logger.debug(str(self))
            for text in self._texts:
                logger.debug(str(text))
                
    def log_results(self):
        for r in self._query_result:
            logger.debug(r)
            
    def get_annotated_full_text(self, pretty=0):
        full_texts=""
        for text in self._texts:
            t = ""
            if pretty == 0:
                #print("Get annotated text")
                t = text.get_annotated_text()
            else:
                t = text.get_annotated_text_pretty_print()
            full_texts = full_texts+" "+t
        return full_texts
    
    def get_article_full_text(self):
        full_texts=""
        for text in self._texts:
            t = text.get_text()
            full_texts = full_texts+" "+t
        return full_texts
    
    def get_full_text_in_xmlformat(self):
        full_texts="<text> "
        for text in self._texts:
            t = text.get_xml_text()
            full_texts = full_texts+" "+t
        full_texts = full_texts+" </text>"
        return full_texts
            
#     def find_text(self, t):
#         for text in self.get_texts():
#             if text == t:
#                 return text
#                 
#     #get result and original text to match them up
#     def fit_annotations_to_text(self):
#         for query_result in self._query_result:
#             for triple in query_result:
#                 arpafied = query_result['arpafied']
#                 original = query_result['original']
#                 simple = simplify_arpa_results(arpafied)
#                 annotated_text = match_arpa_results(simple, original)
#                 text = self.find_text(original)
#                 text.set_annotated_text(annotated_text)
                

    # {"locale":"fi",
    # "results":
    ##[{"id":"http://ldf.fi/warsa/actors/person_1","label":"Carl Gustaf Emil Mannerheim","matches":["Emil Mannerheim"],"properties":{"sukunimi":["\"MANNERHEIM\""],"label":["\"Carl Gustaf Emil Mannerheim\""],"ngram":["\"Emil Mannerheim\""],"id":["<http://ldf.fi/warsa/actors/person_1>"],"etunimet":["\"Carl Gustaf Emil\""]}}]}    
    #def simplify_arpa_results(self, arpafied):
     #   simplified = dict()
     #   if arpafied == None:
     #       return None
     #   if 'results' in arpafied:
     #       results = arpafied['results']
     #       for result in results:
     #           if 'label' in result:
     #               label = result['label']
     #               if 'properties' in result and 'ngram' in result['properties']:
     #                   original_string = result['properties']['ngram']
     #                   if original_string not in simplified:
     #                       simplified[original_string] = label
     #   else:
     #       print("Results do not exist in arpafied, "+str(arpafied))
     #   return simplified
        
    
        
            
    title = property(get_title, set_title, del_title, "title's docstring")
    page = property(get_page, set_page, del_page, "page's docstring")
    author = property(get_author, set_author, del_author, "author's docstring")
    texts = property(get_texts, set_texts, del_texts, "texts's docstring")
    keywords = property(get_keywords, set_keywords, del_keywords, "keywords's docstring")
    consepts = property(get_consepts, set_consepts, del_consepts, "consepts's docstring")
    query_result = property(get_query_result, set_query_result, None, None)
    event = property(get_event, set_event, del_event, "event's docstring")
