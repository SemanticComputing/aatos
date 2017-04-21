import configparser, os
from query.ArpaQueryExecuter import ArpaQueryExecuter
from FileReader import FileReader
from JSONParser import JSONParser
from query.arpa import Arpa
from query.sparql.sparqual_query import sparqlQuery
from datetime import datetime
from article import Article
from magazine import Magazine
import utils, time
import json
import sys, math
import logging, zipfile
import re
from annotationConfig import AnnotatorConfig
from csvWriter import CSVWriter
import traceback

logger = logging.getLogger('Annotator')
hdlr = logging.FileHandler('/tmp/annotator.log')
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)
    
LOG_SUCCESS=True
LOG_PROBLEMS=True

class Annotator(object):

    def __init__(self, conf_set=None, configFile="/home/minna/workspace/kataIE/kansataisteliapp/kata/conf/default.conf.ini"):
        self.__arpa_statistics = dict()
        self.__matched_statistics = dict()
        self.__simplified_statistics = dict()
        self.__conf_set = conf_set
        self.__target_graph = ""
        if len(configFile)>0:
            self.configure(configFile)
            logger.debug("Configure "+configFile)
    
    def configure(self, file):
        ''' >>> print("hello") '''
        if self.__conf_set == None:
            self.__conf_set=list()
        
        logger.debug("Read config file "+file)
        
        config = configparser.ConfigParser()
        r = config.read(file)
        if len(r) <= 0:
            logger.warn("Failed to open/find all files for path "+file)
            raise ValueError("Failed to open/find all files")
        
        for conf in config.sections():
            url=name=""
            ignore=None
            duplicates=False
            ngram=1
            prop=""
            graph=""
            primary=None
            secondary=None
            third=None
            freqlimit=0
            stopwordlist=""
            ranking=False
            ranking_min_range=14
            ranking_max_range=24
            
            logger.debug("Create config "+conf)
            
            for (each_key, each_val) in config.items(conf):
                
                if 'url' == each_key:
                    url=each_val
                
                if 'name' == each_key:
                    name=each_val
                
                if 'remove_duplicates' == each_key:
                    duplicates=each_val
                
                if 'ngram' == each_key:
                    ngram=each_val
                
                if 'ignore' == each_key:
                    ignore=each_val
                    
                if 'mapproptype' == each_key:
                    prop=each_val
                    
                if 'mapgraph' == each_key:
                    graph=each_val
                    self.__target_graph=graph
                    
                if 'primary' == each_key:
                    primary=each_val
                    
                if 'secondary' == each_key:
                    secondary=each_val
                    
                if 'third' == each_key:
                    third=each_val
                    
                if 'frequence_limit' == each_key:
                    freqlimit=each_val
                        
                if 'ordered' == each_key:
                    ordered =str(each_val)
                if 'stopwordlist' == each_key:
                    stopwordlist=str(each_val)
                    
                if 'ranked' == each_key:
                    ranking=str(each_val)
                    logger.debug("Set ranking to true")
                    logger.debug(ranking)
                if ranking == True:
                    if 'ranked_max_range' == each_key:
                        ranking_max_range=each_val
                    if 'ranked_min_range' == each_key:
                        ranking_min_range=each_val
            c = AnnotatorConfig(url, name, duplicates, ngram, ignore, prop, graph, primary, secondary, third, freqlimit,stopwordlist, ranking, ranking_max_range, ranking_min_range, ordered)
            self.__conf_set.append(c)
            
    def doRanking(self):
        rank = list()
        rank_range = dict()
        for conf in self.__conf_set:
            #print(conf)
            logger.debug(conf)
            logger.debug("Ranking conf "+str(conf.get_ranking()))
            if conf.get_ranking() == True:
                prop = conf.get_target_property()
                rank.append(prop)

                minm = conf.get_min_range()
                maxm = conf.get_max_range()
                c = float((100/(maxm - minm)) / 100)
                #rank_range[property_name] = (minimum range, maximum range, range coefiecient)
                rank_range[prop] = (minm,maxm,c)
            logger.debug(conf.get_ranking())
        return rank, rank_range
    
    def doAnnotationWithConfig(self,results, mags, magazines, csvlogging=False, units=None):
        ''' >>> print("hello") '''
        momentum = datetime.now()
        
        for conf in self.__conf_set:
            #print(conf.get_target_property())
            arpa = Arpa(conf.get_remove_duplicates(),conf.get_min_ngram_length(),conf.get_ignore(),conf.get_url(), conf.get_ordered())            
            units = self.executeArpa(results, magazines, arpa, conf.get_name())
            keywords, keyWordFreqs = self.parse_result_json(units, mags, conf.get_target_property(), conf.get_name(), conf.get_stopwordlist())
            #momentum = self.logQueryData(momentum, keywords, conf.get_name())
        
        if csvlogging == True:
            self.writeToCSV(units)
        self.indexAnnotations(units)
        return units

    def writeToCSV(self, magazines):
        if magazines != None:
            fileResults=CSVWriter()
            
            #zip old files first
            stamp=time.time() * 1000
            output = "old_csv_log."+str(stamp)+".zip"
            zipf = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)
            utils.zipdir('csv_log/', zipf)
            zipf.close()
            
            for mId, magazine in enumerate(magazines):
                filename="csv_log/"+magazine.get_name()+"_"+magazine.get_volume()+"_"+magazine.get_issue()+".csv"
                fileResults.writeMagazineCSV(filename, magazine)

    #Query all text relating to one article
    def arpafyTexts(self, magazines, results, arpa, name):
        pages = 0
        counter = 0
        article = ""
        
        for mId, magazine in enumerate(magazines):
            articles=magazine.get_articles()
            pages = len(articles)
            for id,article in enumerate(articles):
                counter += 1
                if (article.get_event()=="Talvisota" and name=="Warsa Units") or name!="Warsa Units":
                    
                    logger.debug("Read "+article.get_event()+ " to "+name)
                    values = article.get_texts()
                    article=self.do_arpa_query(results, arpa, article, values, name)
                    articles[id]=article
                            
                    if LOG_SUCCESS == True:
                        self.logSuccessfulCases(results, article)
                        print(str(counter) + "/" + str(pages))
                        #print(str(article))
                else:
                    logger.debug("Skip article "+str(article)+" because query to "+name)
                    
            magazine.set_articles(articles)
            magazines[mId]=magazine
        
        return pages, magazines


    def indexAnnotations(self, magazines):
        article = ""

        for mId, magazine in enumerate(magazines):
            articles=magazine.get_articles()
            for id,article in enumerate(articles):
                texts = article.get_texts()#.get_annotated_text()
                #    article=self.do_arpa_query(results, arpa, article, values, name)
                conseptList = article.get_consepts()#print(str(article))
                mappedIndexes = conseptList.getAllIndexesByForm()
                texts = self.matchIndexes(mappedIndexes, texts)
                #article.set_annotated_text(texts)

    def matchIndexes(self, indexMap, texts):
        for text in texts:
            annoText=text.get_annotated_text()
            for i in indexMap:
                index = ','.join(indexMap[i])
                substitute = '<annotation> '+index+' </annotation>'
                pattern = r'<annotation> '+i+' </annotation>'
                annoText = re.sub(pattern, substitute, annoText, flags=re.IGNORECASE)
            text.set_annotated_text(annoText)
        return texts

    #try to strip special characters and extra spaces from a string
    def stripInput(self, value):
        q=""
        try:
            stripped = value.strip()
            qstr = stripped.format()
            q = re.sub('\s+', ' ', qstr)
            text = q.replace('*', '').replace('<', '').replace('>', '').replace('^', '').replace("@", '').replace("+", '').replace("?", '').replace("_", '').replace("%", '')
            q = text.replace('§', '').replace('[', '').replace(']', '').replace('{', '').replace("}", '').replace("#", '').replace("~", '').replace('"', '').replace("+", '')
            q = q.replace('@', '').replace('$', '').replace('£', '').replace('µ', '').replace("!", '').replace("&", '').replace('=', '').replace("|", '')
            
            q = q.replace('*', '').replace('^', '').replace("@", '').replace("+", '').replace("?", '').replace("_", '').replace("%", '').replace("...",'').replace("|",'').replace("..",'').replace("■",'').replace("£",'')
            q = q.replace('•', '').replace('&', '').replace('´', '').replace('`', '').replace("§", '').replace("½", '').replace("=", '').replace('¤', '').replace("$", '').replace("--",'').replace(",,",'').replace("»",'').replace("—",'')
            q = q.replace('“', '').replace(' . ', ' ').replace("”", '').replace(".,", '').replace(',.', '').replace("“", '').replace(",,,",'').replace("'",'').replace("«",'')
            q = re.sub(r'[\.,:;-]{2}', "", q)
            text = re.sub(r'\x85', 'â€¦', text) # replace ellipses
            text = re.sub(r'\x91', "â€˜", text)  # replace left single quote
            text = re.sub(r'\x92', "â€™", text)  # replace right single quote
            text = re.sub(r'\x93', 'â€œ', text)  # replace left double quote
            text = re.sub(r'\x94', 'â€�', text)  # replace right double quote
            text = re.sub(r'\x95', 'â€¢', text)   # replace bullet
            text = re.sub(r'\x96', '-', text)        # replace bullet
            text = re.sub(r'\x99', 'â„¢', text)  # replace TM
            text = re.sub(r'\xae', 'Â®', text)    # replace (R)
            text = re.sub(r'\xb0', 'Â°', text)    # replace degree symbol
            text = re.sub(r'\xba', 'Â°', text)    # replace degree symbol
            
            text = re.sub('â€¦', '', text) # replace ellipses
            text = re.sub('â€¢', '', text)   # replace bullet
            text = re.sub('â– ', '', text)   # replace squares
            text = re.sub('â„¢', '', text)  # replace TM
            text = re.sub('Â®', '', text)    # replace (R)
            text = re.sub('®', '', text)    # replace (R)
            text = re.sub('Â°', '', text)    # replace degree symbol
            text = re.sub('Â°', '', text)    # replace degree symbol
            
            q = re.sub(r'\d\d.\d\d.\d\d\d\d',"",q) #dates
            text = re.sub(r'\d{1,2}.\d\d.',"",text) #times
            
            #q = re.sub(r'((\.|\s)+)', "", q)
            #q = re.sub(r'((\,|\s)+)', "", q)
            #q = re.sub(r'(\,+)', "", q)
            
        
            # Do you want to keep new lines / carriage returns? These are generally 
            # okay and useful for readability
            text = re.sub(r'[\n\r]+', ' ', text)     # remove embedded \n and \r
        
            # This is a hard-core line that strips everything else.
            #q = re.sub(r'[\x00-\x1f\x80-\xff]', ' ', text)
            #return text
            
        except ValueError as err:
            logger.warn("Unexpected error while formatting article " + article + ":", err)
            logger.warn("Error article " + article + " content:" + value)
            q = value
        except Exception as e:
            logger.warn("Unexpected error while formatting article " + article + ":", e)
            logger.warn("Error article " + article + " content:" + value)
            q = value
        return q
    
    #try to strip special characters and extra spaces from a string
    def stripInputAnnotatedText(self, value):
        q=""
        try:
            stripped = value.strip()
            qstr = stripped.format()
            q = re.sub('\s+', ' ', qstr)
            text = q.replace('*', '').replace('^', '').replace("@", '').replace("+", '').replace("?", '').replace("_", '').replace("%", '').replace("...",'').replace("|",'').replace("..",'').replace("■",'').replace("£",'')
            q = text.replace('^', '').replace('[', '').replace(']', '').replace('{', '').replace("}", '').replace("#", '').replace("~", '').replace('"', '').replace("+", '')
            q = q.replace('•', '').replace('&', '').replace('´', '').replace('`', '').replace("§", '').replace("½", '').replace("=", '').replace('¤', '').replace("$", '').replace("--",'').replace(",,",'').replace("»",'').replace("—",'')
            q = q.replace('“', '').replace(' . ', ' ').replace("”", '').replace(".,", '').replace(',.', '').replace("“", '').replace(",,,",'').replace("'",'').replace("«",'')
            
            q = re.sub(r'[\.,:;-]{2}', "", q)

            #q = re.sub(r'((\,|\s)+)', "", q)
            #q = re.sub(r'(\,+)', "", q)
            
        
            # Do you want to keep new lines / carriage returns? These are generally 
            # okay and useful for readability
            #q = re.sub(r'[\n\r]+', ' ', q)     # remove embedded \n and \r
        
            # This is a hard-core line that strips everything else.
            #q = re.sub(r'[\x00-\x1f\x80-\xff]', ' ', text)
            #return text
            
        except ValueError as err:
            logger.warn("Unexpected error while formatting article " + article + ":", err)
            logger.warn("Error article " + article + " content:" + value)
            q = value
        except Exception as e:
            logger.warn("Unexpected error while formatting article " + article + ":", e)
            logger.warn("Error article " + article + " content:" + value)
            q = value
        return q
    def read_stoplist(self, filename):
        stoplist = [line.strip().lower() for line in open(filename, 'r')]
        return stoplist

    #extract results from json to an python array
    def simplify_arpa_results(self, arpafied):
        simplified = dict()
        found = 0#self.read_stoplist(stopwordlist)
        if arpafied == None:
            return None
        if 'results' in arpafied:
            results = arpafied['results']
            for result in results:
                if 'label' in result:
                    label = result['label']
                    if 'matches' in result: 
                        matches = result['matches']
                        #print(matches)
                        for mlabel in matches:
                            #print(mlabel)
                            mlabel = mlabel.replace('"','')
                            found=found+1
                            #if mlabel not in simplified and mlabel not in filtered_words:
                            if mlabel not in simplified:
                                #found=found+1
                                labels = list()
                                labels.append(label)
                                simplified[mlabel] = labels
                            else:
                                if label not in simplified[mlabel]:
                                    simplified[mlabel].append(label)
                                
                    elif 'properties' in result and 'ngram' in result['properties']:
                        original_string = result['properties']['ngram'][0]
                        found=found+1
                        original_string = original_string.replace('"','')
                        if original_string not in simplified:
                            labels = list()
                            labels.append(label)
                            simplified[original_string] = labels
                        else:
                            if label not in simplified[original_string]:
                                simplified[original_string].append(label)
        else:
            print("Results do not exist in arpafied, "+str(arpafied))
        return simplified,found
    

    def uniteConsepts(self, string, arpafied, consepts):
        c = list()
        logger.debug(string+" being united")
        for a in arpafied:
            cn,i = consepts.getConseptByName(a)
            if cn != None:
                c.append(cn)
        if len(c)>1:
            index=c[0].getIndex()
            for item in c:
                item.setIndex(index)

    #match annotation results to the original text with annotation tags   
    def match_arpa_results(self, arpafied, original, conseptList):
        arpafied_strings = arpafied.keys()
        matched_text =  " "+original+" "
        xml_text = " "+original+" "
        matched=0
        i=0
        consept_map = dict()
        for string in arpafied_strings:
            c=""
            #self.uniteConsepts(string, arpafied[string], conseptList)
            i = i+1
            j = str(i) + "_" + string
            for a in arpafied:
                if len(c)>0:
                    c =c +","+ a
                else:
                    c = a
            consept_map[j]=c
            for arpafy in arpafied[string]:
                
                anno0="<annotation> " + string + " </annotation>"
                #anno3="<annotation> " + arpafy + " </annotation>"
                anno1="<annotation> " + string
                anno2=string + " </annotation>"
                anno4= "<annotation> ([^<]+?) "+string+" ([^<]+?) </annotation>"
                anno3= "<annotation> ([^<]+?) "+string+" ([^<]+?) </annotation>"
                normal_string = " "+string+" "
                normal_string_pattern =  r"(?<!-)\b" + string + r"\b(?!-)"
                anno5=re.findall(anno4, original,re.IGNORECASE)
                all_occurances=re.findall(normal_string_pattern, original,re.IGNORECASE)
                print(anno5)
                print(anno4)
                if len(all_occurances) > 0 and anno0 not in original and anno1 not in original and anno2 not in original: #and len(anno5) < 1:# and anno3 not in original:
                #print("Annotation found")
                    replacement =  " <annotation> " + string  + " </annotation> "
                    xml_replacement =  " </text> <annotation originalString='"+arpafy+"'> " + string  + " </annotation> <text> "
                    xml_text=self.replace_str(xml_text, string, xml_replacement)
                    #xml_text=re.sub(normal_string_pattern, xml_replacement, xml_text)#xml_text.replace(string, xml_replacement)
                    matched_text=self.replace_str(matched_text, string, replacement)
                    #matched_text=re.sub(normal_string_pattern, replacement, matched_text)#matched_text.replace(string, replacement)
                    matched=matched+1
                    #print(a)
                    print(xml_text)
                    #print(b)
                    print(matched_text)
                    
                    
        return matched_text, xml_text, matched
    
    def replace_str(self, text, string, replacement):
        positions = self.find_position(text, string)
        while positions != None:  
            start = positions[0]
            end = positions[1]          
            text = text[:start] +replacement+ text[end:]
            positions = self.find_position(text, string)
        return text
    
    def find_position(self, text, string):
        #pattern = r"(?<!<annotation>)([^<]+?)\b"+string+r"\b([^<]+?)(?!<\/annotation>)"
        pattern = r'(\b'+string+r'\b)(?![^<]*>|[^<>]*<\/)'
        matches = re.compile(pattern)
        iterator = matches.finditer(text)

        for i in iterator:        
            return i.span()
        return None

    
    def write_stats_matched(self, name, simplified):
        if name in self.__simplified_statistics:
            self.__simplified_statistics[name] =self.__simplified_statistics[name] + len(simplified)
        else:
            self.__simplified_statistics[name] = len(simplified)
    def write_stats_arpa(self, name, found):
        if name in self.__arpa_statistics:
            self.__arpa_statistics[name] = self.__arpa_statistics[name] + found
        else:
            self.__arpa_statistics[name] = found
            
    def write_stats_annotation(self, name, matched):
        if name in self.__matched_statistics:
            self.__matched_statistics[name] = self.__matched_statistics[name] + matched
        else:
            self.__matched_statistics[name] = matched
    def print_filtered_terms(self, mags):
        logger.info("PRINTING TERMS THAT WERE FILTERED OUT")
        lkm = 0
        matched=0
        if mags == None:
            return
        for magazine in mags:
            count = 0
            w_count = 0
            articles = magazine.get_articles()
            for article in articles:
                concept_container = article.get_consepts()
                if concept_container != None:
                    l = concept_container.get_consepts()
                    count = len(l)
                    for item in l:
                        if item.getWeight() == 0:
                            #logger.info(item)
                            logger.info(str(item)+" ... "+str(item.getWeight()))

    def print_included_terms(self, mags):
        logger.info("PRINTING TERMS THAT WERE INCLUDED")
        lkm = 0
        matched=0
        if mags == None:
            return
        for magazine in mags:
            count = 0
            w_count = 0
            articles = magazine.get_articles()
            for article in articles:
                concept_container = article.get_consepts()
                if concept_container != None:
                    l = concept_container.get_consepts()
                    count = len(l)
                    for item in l:
                        if item.getWeight() > 0:
                            logger.info(str(item)+" ... "+str(item.getWeight()))

    def print_stats(self, mags):
        logger.info("PRINTING STATISTICAL REPORT OF ANNOTATION PROCESS")
        logger.info("ARTICLE ... AMOUNT")
        lkm = 0
        matched=0
        if mags == None:
            return

        for magazine in mags:
            count = 0 
            #w_count = 0 
            articles = magazine.get_articles()
            for article in articles:
                concept_container = article.get_consepts()
                w_count = 0 
                if concept_container != None:
                    l = concept_container.get_consepts()
                    count = len(l)
                    for item in l:
                        if item.getWeight() > 0:
                            w_count = w_count+1
                logger.info(str(magazine)+" : "+str(article)+" ... "+str(count)+" TERMS")
                logger.info(str(article)+" ... "+str(w_count)+" TERMS WITH WEIGHT")
                logger.info(str(article)+" ... "+str(count-w_count)+" TERMS WITHout WEIGHT")
        logger.info("ARPA NAME ... AMOUNT")
        for i in self.__arpa_statistics:
            logger.info(str(i)+" ... "+str(self.__arpa_statistics[i]))
            lkm=self.__arpa_statistics[i]+lkm
        logger.info("ARPA NAME ... MATCHED")
        for i in self.__matched_statistics:
            c=(self.__matched_statistics[i]/self.__arpa_statistics[i])*100
            percentage=round(c,2)
            logger.info(str(i)+" ... "+str(self.__matched_statistics[i])+" "+str(percentage)+"% OF ANNOTATIONS MATCHED")
            matched=self.__matched_statistics[i]+matched
        c=(matched/lkm)*100
        percentage=round(c,2)
        logger.info(str(percentage)+"% OF ANNOTATIONS MATCHED")

    #Execute arpa queries
    def do_arpa_query(self, results, arpa, article, values, name):
        triples=[]
        parts = 0
        for value in values:
            triple = dict()
            parts += 1
            #q=value.get_annotated_text()
            #if len(q) < 1:
            q = self.stripInput(value.get_text())
            
            if len(q) > 0:
                startTime = datetime.now()
                logger.debug("Query to "+arpa._get_url())
                result = arpa._query(q)
                
                #store the results
                momentum = datetime.now()
                now = momentum - startTime
                logger.info("TIME : " + str(now) + " / (" + str(len(q)) + ") lines ")
                triple['original'] = value
                triple['querystring'] = q
                triple['arpafied'] = result
                simplified,found = self.simplify_arpa_results(result)
                triple['simplified'] = simplified
                triples.append(triple)
                
                annoText=value.get_annotated_text()
                if len(annoText) < 1:
                    annoText=value.get_text()
                self.write_stats_matched(name, simplified)
                self.write_stats_arpa(name, found)
                logger.debug("Text for matching "+str(annoText))
                logger.debug("Arpa results for matching "+str(simplified))
                if len(simplified)>0:
                    matched, xml, match_amount = self.match_arpa_results(simplified, self.stripInputAnnotatedText(annoText), article.get_consepts())
                    self.write_stats_annotation(name, match_amount)
                    value.set_annotated_text(matched) 
                    #logger.debug("XML TEXT:"+xml)
                    value.set_xml_text(xml) 
                    logger.debug(matched)              
            
            #save results
        article.set_query_result(triples)
        return article
    
    def executeArpa(self, results, magazines, arpa, name):
        logger.debug("query arpa")
        page, results = self.arpafyTexts(magazines, results, arpa, name)
        if LOG_PROBLEMS == False:
            logProblemCases(results, page)
            
        return results

    def logProblemCases(self, results, page):
        print("START TO LOG")
        for page in results:
            logger.debug('PAGE ' + page)
            res = results[page]['arpafied']
            if 'result' in res:
                if 'code' in res:
                    logger.debug('Query result ' + res['code'])
                if 'value' in res:
                    logger.debug('Query result ' + res['value'])
                if 'params' in res:
                    logger.debug('Query result ' + res['url'])
                if 'url' in res:
                    logger.debug('Query result ' + res['params'])
                logger.debug('Original text ' + results[page]['original'])
                logger.debug('Query string ' + results[page]['querystring'])
                
    def parse_result_json(self, input_magazines, complete_list_magazines, targetUri, arpaName, stopwordlist, keywords=None, keyWordsFreqs=None):
        parser = JSONParser()
        print("ANNO: JSON PARSERIIN")
        print(stopwordlist)
        return parser.parse(input_magazines, complete_list_magazines,targetUri,  arpaName, stopwordlist, keywords, keyWordsFreqs)
    
    def get_confs(self):
        return self.__conf_set
    
    def get_target_graph(self):
        return self.__target_graph
    
    def get_conf_set(self, rdf_target):
        for c in self.__conf_set:
            prop = c.get_target_property()
            if prop == rdf_target:
                return c
        return None

    def logArpaResults(self, url, keywords):
        if keywords != None:
            for keyword in keywords:
                try:
                    keys = keywords[keyword].keys()
                except:
                    keys = keywords[keyword]
                    
                try:
                    sorted_keys = sorted(keys)
                except:
                    sorted_keys = keys
                logger.debug(url+" " + keyword + " : " + str(sorted_keys))
        else:
            print("For this arpa " + url + " keyWords not found!")
    
    
    def logQueryData(self, momentum, keywords, url=None):
        now = datetime.now() - momentum
        for magazine in keywords:
            magazine.log_articles(True, False, 1)
            magazine.log_article_terms()
                
        #if url != None:
            #logArpaResults(logger, url, keywords)
        logger.info("Queried actors in " + str(now))
        momentum = datetime.now()
        return momentum
    
    def logSuccessfulCases(self, result, page):
        #result.log_results()
        if 'results' in result:
            magazine=result[page]
            logger.debug('successful PAGE ' + page)
            logger.debug('original page ' + magazine['original'])
            logger.debug('formatted page ' + magazine['querystring'])
            logger.debug('results for the page ' + str(magazine['arpafied']))

    def logConseptsByIndex(selfi, mags): 
        if mags == None:
            return
        for magazine in mags:
            articles = magazine.get_articles()
            for article in articles:
                concept_container = article.get_consepts()
                concept_container.logConseptsByIndex()
