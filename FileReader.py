import glob
import os, sys, re
import utils
import logging
from fileinput import filename
from article import Article
from magazine import Magazine
from bs4 import BeautifulSoup
from htmlParser import htmlParser
#from debian.debfile import PART_EXTS
#http://stackoverflow.com/questions/2212643/python-recursive-folder-read

            #logging detup
logger = logging.getLogger('FileReader')
hdlr = logging.FileHandler('/tmp/file_reader.log')
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)

class FileReader(object):
    def __init__(self, file_name_pattern="", path="", full_path="", min_len=0, max_len=0):
        self.__file_name_pattern = file_name_pattern
        self.__path = path
        self._min_len = min_len
        self._max_len = max_len
        
        if full_path != "" and full_path!=None:
            self.__document=full_path
    def getMinLength(self):
        #return minimum length of a doc from the read document set
        return self._min_len
    def getMaxLength(self):
        #return maximum length of a doc from the read document set
        return self._max_len
    
    def setLengths(self, length):
        if length > self._max_len:
            if int(self._min_len) <= 0 and int(self._max_len) > 0:
                self._min_len = self._max_len
            self._max_len = int(length)
        elif (length < self._min_len or self._min_len == 0) and length > 0:
            self._min_len = int(length)     
        
    def getArticles(self, articles, filename):
        item=None
        for articleKey in articles:
            id = articles[articleKey]
            if articleKey in filename:
                return id
        
        return item

    def extractVolumeIssueFromFilename(self, filename):
        name=volume=issue=""
        if utils.contains_digits(filename) == False:
            return 0
        filenameArr = filename.split(".")
        filePrefix = filenameArr[0]
        file = filePrefix.split("_")
        
        leng = len(file)
        if leng>=4:
            name = file[1]+" "+file[2]
            volume = file[(leng-2)]
            if volume != file[4]:
                issue = ""+file[3] +"_"+ file[4]
            else: 
                issue = ""+file[3]
        else:
            return 0
        
        issue = issue.replace("-", "")
        
        return name, volume, issue   

    def extractPageNumberFromFilename(self, filename):
        if utils.contains_digits(filename) == False:
            return 0
        
        filePrefix = filename.split(".")[0]
        pageString = filePrefix.split("_")[-1]
        if not ('page' in pageString):
            for part in filePrefix:
                if 'page' in part:
                    pageString = part
        
        pageStr = ''.join(x for x in pageString if x.isdigit())
        filePage = int(pageStr)
        return filePage

    def getArticlea(self, magazines, filename):
        item=None
        articles = self.getArticles(articles, filename)
        name= volume= issue=""
        filePage=0
        closest=0
        close=0
        nearestMatchItem=0
        try:
            if "." in filename:
                filePage = self.extractPageNumberFromFilename(filename)
            if "_" in filename:
                name, volume, issue = self.extractVolumeIssueFromFilename(filename)
            
            #in case of a problem
            if filePage == 0:
                return item
            
            for magazine in magazines:
                if magazine.get_volume()==volume:
                    if magazine.get_issue()==issue:
                        item= magazine

        except Exception as e:
            print("Error happened!!!!!!!!!!!!!!! "+filename)
            print(e)
        
        return item

    def getArticle(self, articles, filename):
        item=None
        articles = self.getArticles(articles, filename)
        filePage=0
        closest=0
        close=0
        nearestMatchItem=0
        try:
            if "." in filename:
                filePage = self.extractPageNumberFromFilename(filename)
            
            #in case of a problem
            if filePage == 0:
                return item
            
            for a in articles:
                page=utils.convertToInt(utils.getDictValue(a, 'page'))
                close = filePage - int(page)
                if close >= 0:
                    if closest > close or nearestMatchItem == 0:
                            item = a
                            nearestMatchItem=page
                            closest=close
        except Exception as e:
            print("Error happened!!!!!!!!!!!!!!! "+filename)
            print(e)
        
        return item
    

    def isEndOfArticle(self,article,articles):
        p = utils.convertToInt(utils.getDictValue(article, 'page'))
        nextPage=p+1
        for a in articles:
            page=utils.getDictValue(a, 'page')
            page = utils.convertToInt(page)
            if page == nextPage:
                return True
        return False
        
    def getMagazine(self, filename):
        name, volume, issue = self.extractVolumeIssueFromFilename(filename)
        fileId=issue+"_"+volume
        return fileId

    def saveValuesForNewIdentifier(self, container, identifier, doc):
        values = []
        values.append(doc)
        container[identifier] = values
        return container


    def readDocument(self, path, folder, filename, document):
        document = ""
        if not folder in path:
            document = folder + "/" + filename
        else:
            document = path + filename
        doc = self.read(document)
        return doc, document

    def execute_with_params(self, file_pattern="", path="", magazines=None,articles=None):
        listOfMagazines=[]
        container = dict()
        for folder, subs, files in os.walk(path):
            with open(os.path.join(folder, file_pattern), 'w') as dest:
                docValue=""
                prevId=""
                identifier=""
                page_count=0
                for filename in files:
                    #print("Filename "+filename)
                    if filename == file_pattern:
                        pass                    
                    elif filename.endswith(file_pattern):
                        document=""
                        if not folder in path:
                            document = folder+"/"+filename
                        else:
                            document = path+filename
                        doc = self.read(document)
                        if magazines==None:
                            pass
                            #container = self.saveValuesForNewIdentifier(container, identifier, doc)
                        elif len(doc)<1:
                            pass
                        else:
                            fileId = self.getMagazine(filename)
                            mag=magazines[fileId]
                            if fileId not in listOfMagazines:
                                listOfMagazines.append(fileId)
                            page = self.extractPageNumberFromFilename(filename)
                            if page > 0:
                                article = mag.find_article_by_page(page)
                                logger.debug(article)
                                logger.debug(filename)
                                
                                #get filename
                                name=""
                                str_name = filename.split("page")
                                try:
                                    name = str_name[0]
                                except:
                                    name = filename
                                mag.set_name(name)
                                if article != None: #If article exists
                                    if len(doc)<5 and len(values[-1:])<3900:
                                        logger.info("SMALL "+str(len(doc)) + " = "+doc)
                                        pass
                                    if len(doc)>0:
                                        self.setLengths(len(doc))
                                        #split value in case too long to process
                                        if len(doc)>3000:
                                            sentences=""
                                            splitted = doc.split(' ')
                                            for split in splitted:
                                                lenn = len(sentences) + len(split) + 1 #+1 for the space
                                                if lenn > 3000:
                                                    article.addText(sentences, page)
                                                    sentences = ""
                                                sentences += split+" "
                                            if len(sentences) > 0:
                                                article.addText(sentences, page)
                                        else:
                                            article.addText(doc, page)
                                            article.set_len(len(doc))
                                else:
                                    #in case we cannot find article
                                    article = Article(filename, page, "")
                                    article.addText(doc, page)
                                    article.set_len(len(doc))
                                    self.setLengths(len(doc))
                                    mag.add_article(article)    
                            else:
                                    #if article not found for the document, store pages page by page
                                print("stored file "+filename+" as article was not found")
                                article = Article(filename, page, "")
                                article.addText(doc, page)
                                article.set_len(len(doc))
                                mag.add_article(article) 
                                self.setLengths(len(doc))
                                
                            magazines[fileId] = mag 
                            #mag.log_articles_and_contents()
                            
                    elif filename.endswith(".xml"):
                        page_count = 1+page_count
                        article = Article(filename, page, "")
                        doc, document = self.readDocument(path, folder, filename, document)
                        if len(doc)>0:
                            xml = xmlParser(input_file=doc)
                            if bool(BeautifulSoup(html, "html.parser").find()) == True:
                                self.setLengths(len(doc))
                                article.set_len(len(doc))
                                html = htmlParser(doc)
                                article = self.split_document(html.get_text(), article, page_count)
                                result.append(article)
                        else:
                            #process
                            pass
                    elif filename.endswith(".html"):
                        page_count = 1+page_count
                        article = Article(filename, page, "")
                         
                        doc, document = self.readDocument(path, folder, filename, document)
                        if len(doc)>0:
                            self.setLengths(len(doc))
                            article.set_len(len(doc))
                            html = htmlParser(doc)
                            article = self.split_document(html.get_text(), article, page_count)
                            result.append(article)
                        else:
                            #process
                            pass
                dest.close()              
                     
        result = []
        logger.debug("VALUES FOR magazines "+str(len(listOfMagazines)))
        for id in listOfMagazines:
            if magazines[id] not in result:
                result.append(magazines[id])
        return result, listOfMagazines
    
    def read_html_page(self, filename):
        logger.info("Opening file "+filename+" to read")
        result = []
        page_count=1
        volume, issue=self.get_volume_issue_from_url(filename)
        mag = Magazine("", volume, issue)
        article = Article(filename, page_count, "")
        if self.validate_url(filename) == True:
            doc=self.upload_html_doc(filename)
            if len(doc)>0:
                html = htmlParser(doc)
                p = re.compile("<[-a-zA-Z0-9@:%_\+.~#?&\/=]*>")
                ids = p.findall(html.get_text())
                if len(ids)>0:
                    id = ids[0].replace("<","").replace(">","")
                    article.set_id(id)
                article = self.split_document(html.get_text(), article, page_count)
                mag.add_article(article)
                self.setLengths(len(doc))
                article.set_len(len(doc))
                result.append(mag)
            else:
                #process
                pass
        return result
    
    def retrieve_htmlpage_identifier(self,filename):
        str=list()
        filename = filename.replace("http://", "").replace("https://", "")
        for part in filename.split("/"):
            if not("." in part):
                if utils.contains_digits(part):
                    str.append(part)
        return str
    
    def get_volume_issue_from_url(self, url):
        str = self.retrieve_htmlpage_identifier(url)
        volume=0
        issue=0
        if len(str)>0:
            if len(str)>=1:
                volume=str[0]
            if len(str)>=2:
                issue=str[1]
            if len(str)>=3:
                issue=str[1]+"_"+str[2]
            if len(str)>=4:
                issue=str[1] + "_" + str[2] + "_" + str[3]
        return volume, issue
    
    def validate_url(self,url):
        import validators
        return validators.url(url)

    def upload_html_doc(self,url):
        try:
            import requests,time
            logger.info("Opening url "+url+" to read")
            #print("Opening url "+url+" to read")
            data =  requests.get(url)
            if data.status_code != 200:
                sleep_time=60
                while data.status_code != 200 and sleep_time < 4000:    
                    logger.debug("Unable to reach url "+url+" and waiting for" + str(sleep_time)+"s")
                    time.sleep(sleep_time)
                    sleep_time=sleep_time*2
                    data =  requests.get(url)
                    if sleep_time > 4000 and data.status_code != 200:
                        logger.debug("Unable to reach "+url+" in given time. Skipping it.")
            return data.text#.decode('utf-8')
        except Exception as e:
            print("Error during execution")
            print("Unexpected error while reading a html file ", e)
            error = traceback.format_exc()
            print(error.upper())
        return ""
    
    def split_document(self, doc, article, page):
        if len(doc)>3000:
            sentences=""
            splitted = doc.split(' ')
            for split in splitted:
                lenn = len(sentences) + len(split) + 1 #+1 for the space
                if lenn > 3000:
                    article.addText(sentences, page)
                    sentences = ""
                sentences += split+" "
            if len(sentences) > 0:
                article.addText(sentences, page)
        else:
            article.addText(doc, page)
            
        return article
    def read(self, filename):
        # File: readline-example-3.py
        logger.info("Opening file "+filename+" to read")
        file = open(filename, encoding="utf8")
        
        document=""
        empty_lines=0
        while 1:
            lines = file.readlines()
            if not lines:
                break
            for line in lines:
                stripped = line.strip("\r\n").strip()
                if (len(line)<3 or len(stripped)<1) and empty_lines<1:
                    if len(stripped) > 0:
                        document += stripped#line.strip()
                    empty_lines+=1
                else:
                    if len(stripped) > 0:
                        if len(document) > 0:
                            if document[-1] == "-":
                                document += stripped
                            else:
                                document += " "+stripped
                        else:
                            document += stripped
                        empty_lines=0
        
        #Cleanup procedure
        document = document.replace('[','').replace(']','')
        document = document.replace('{','').replace('}','')
        document = document.replace('#','').replace('@','')
        
        file.close()
        
        return document
