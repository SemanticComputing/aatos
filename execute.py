from query.ArpaQueryExecuter import ArpaQueryExecuter
from FileReader import FileReader
from JSONParser import JSONParser
from query.arpa import Arpa
from query.sparql.sparqual_query import sparqlQuery
from datetime import datetime
from article import Article
from magazine import Magazine
from annotator import Annotator
from updateRDF import updateRDF
from csvWriter import CSVWriter
import traceback
import utils, time
import json, zipfile
import sys, getopt
import logging
import os
import re, sys
from linguistics import linguistics

LOG_SUCCESS=True
LOG_PROBLEMS=True

def logProblemCases(logger, results, page):
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



def logSuccessfulCases(logger, result, page):
    if 'results' in result:
        magazine=result[page]
        logger.debug('successful PAGE ' + page)
        logger.debug('original page ' + magazine['original'])
        logger.debug('formatted page ' + magazine['querystring'])
        logger.debug('results for the page ' + str(magazine['arpafied']))

def getKeyAndValuePair(field,result):
    key = 'value'
    return utils.getKeyAndValuePair(field,result,key)


def addOrUpdateMagazine(title, author,  volume, issue, id, pageNro, event, magazines, namePostFix):
    if namePostFix in magazines:
        magazine = magazines[namePostFix]
        if magazine == None:
            magazine = Magazine("", volume, issue)
        else:
            a = Article(title, pageNro, author, id, event)
            if magazine.is_article_in_magazine(a) == False:
                magazine.add_article(a)
    else:
        magazine = Magazine("", volume, issue)
        a = Article(title, pageNro, author, id, event)
        magazine.add_article(a)
    return magazine

def mapKataSparQL(logger, results):
    articles = dict()
    title= volume= issue= id = ""
    prevPostFixId= namePostFixId=""
    pageNro = 0
    pages=[]
    magazines = dict()
    for result in results["results"]["bindings"]:
        try:
            title = getKeyAndValuePair('title', result)
            volume = getKeyAndValuePair('vol', result)
            issue = getKeyAndValuePair('issue', result)
            if "-" in issue:
                try:
                    #add leading zeroes like in the files
                    nro1=issue.split("-")[0].zfill(2) 
                    nro2=issue.split("-")[1].zfill(2) 
                    issue = nro1+"_"+nro2
                except:
                    issue = issue.replace("-", "")
                
            pageNro = getKeyAndValuePair('page', result)
            id = getKeyAndValuePair('sub', result)
            author = getKeyAndValuePair('author', result)
            event = getKeyAndValuePair('event', result)
            
        except:
            logger.error("Error happened here ")
        
        prevPostFixId=namePostFixId
        namePostFix = utils.fixToFIleNameFormat(issue)
        namePostFix += "_" + volume
        namePostFixId = namePostFix # + "_page"+pageNro
        
        #book keeping
        magazine = addOrUpdateMagazine(title, author, volume, issue, id, pageNro, event, magazines, namePostFix)
        magazines[namePostFix]=magazine
        
        if namePostFixId != prevPostFixId:
            if len(prevPostFixId)>0:
                articles[prevPostFixId] = pages
                pages=[]
            
        article = dict()
        article['id'] = id
        article['fileID'] = namePostFix
        article['title'] = title
        article['page'] = pageNro
        article['volume'] = volume
        article['issue'] = issue
        article['event'] = event
        
        idx=0
        try:
            idx = int(pageNro)
        except:
            idx=len(pages)-1
        
        if idx in pages:
            pages.append(article)
        else:
            pages.insert(idx, article)
            
    articles[namePostFixId] = pages
    
    return articles, magazines


def executeArpa(logger, results, magazines, arpa):
    page, results = arpafyTexts(logger, magazines, results, arpa)
    if LOG_PROBLEMS == False:
        logProblemCases(logger, results, page)
        
    return results

def parse_result_json(input_magazines, complete_list_magazines, keywords=None, keyWordsFreqs=None):
    parser = JSONParser()
    return parser.parse(input_magazines, complete_list_magazines, keywords, keyWordsFreqs)


def logArpaResults(logger, url, keywords):
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


def logQueryData(logger, momentum, keywords, url=None):
    now = datetime.now() - momentum
    for magazine in keywords:
        magazine.log_articles(True, False, 1)
        magazine.log_article_terms()
            
    #if url != None:
        #logArpaResults(logger, url, keywords)
    logger.info("Queried actors in " + str(now))
    momentum = datetime.now()
    return momentum


def readKataMagazines(logger):
    kata = sparqlQuery()
    results = kata.query_kata()
    articles, mags = mapKataSparQL(logger, results)
    for magId in mags:
        #logger.debug(magId)
        mag = mags[magId]
        if mag != None:
            mag.log_articles()
    
    return mags, results

def find_prev_next(elem, elements):
    previous, next = None, None
    index = elements.index(elem)
    if index > 0:
        previous = elements[index -1]
    if index < (len(elements)-1):
        next = elements[index +1]
    return previous, next

def filter_texts_using_stopwords(input, logger):
    stopwordlist="conf/stop-words_finnish_3_own_additions_fi.txt"
    filtered_words = read_stoplist(stopwordlist)
    text = ' '.join([i for i in re.findall(r'\S+', input) if i not in filtered_words])
    words=re.findall(r'\S+', input)
    skip = False
    t = ""
    for item in words:
        prev, next = find_prev_next(item, words)
        if "<annotation>" not in item:
            skip=True
            t = t+' '+item
        elif "</annotation>" in item:
            skip=False
            t = t+' '+item
        else:
            if skip == False:
                if item not in filtered_words:
                    t = t+' '+item
            else:
                t = t+' '+item
    
    #logger.debug("Compare regex powers")
    #logger.debug("Looping has "+str(len(t.split()))+" items and is of len "+str(len(t)))
    #logger.debug("regex has "+str(len(text.split()))+" items and is of len "+str(len(text)))
    #logger.info(t)
    #logger.info(text)
    
    return text
def read_stoplist(filename):
    stoplist = [line.strip().lower() for line in open(filename, 'r')]
    return stoplist

def do_linguistics(magazines, logger):
    pages = 0
    counter = 0
    article = ""
    one_mag=list()
    ling = linguistics(None)
    magnro = len(magazines)
    documents=dict()
    for mId, magazine in enumerate(magazines):
        articles=magazine.get_articles()
        pages = len(articles)
        full_text=""
        for id,article in enumerate(articles):
            counter += 1
                
            logger.debug("Read "+article.get_event())
            full_text = article.get_annotated_full_text(0)
            logger.debug(str(full_text[0:100])+"...")
            mag=(str(magazine.get_name()).replace(":","")+str(article.get_title())).replace(" ","_").replace("__","_")
            documents[mag]=full_text#filter_texts_using_stopwords(full_text, logger)
                    
            if LOG_SUCCESS == True:
            #    self.logSuccessfulCases(results, article)
                logger.debug("TF-IDF: "+str(counter) + "/" + str(pages))
            else:
                logger.debug("Skip article "+str(article)+" because query to "+name)
        
        logger.debug("TF-IDF: "+str(counter) + "/" + str(magnro))
                
    #print(len(documents))
    tfidf=ling.do_tfidf(documents)
    candidates=translateIndexes(magazines,ling.get_candidates())
    limit = ling.get_avg_tfidf_score()
    return tfidf,candidates, limit

def translateIndexes(magazines, candidates):
    #l = candidatesToList(candidates)
    print(candidates.keys())
    for mId, magazine in enumerate(magazines):
        articles=magazine.get_articles()
        for id,article in enumerate(articles):
            concept_container = article.get_consepts()
            magId=(str(magazine.get_name()).replace(":","")+str(article.get_title())).replace(" ","_").replace("__","_")
            l = candidatesToDict(candidates[magId])
            print("Candidates for "+str(magId)+ " : "+str(len(l)))
            candidate_list=list()
            if concept_container != None:
                consepts = concept_container.get_consepts() 
                for consept in consepts:
                    index = consept.getIndex()
                    label = consept._getLabel()
                    if index in l:
                        tuple=(label,l[index])
                        if tuple not in candidate_list:
                            candidate_list.append(tuple)
            candidates[magId]=sorted(candidate_list, key=lambda candidate: float(candidate[1]), reverse=True)
    return candidates

def candidatesToDict(candidates):
    l = dict()
    for tuple in candidates:
        a, b = tuple
        l[a] = b
    return l    
                


def readFile(logger, pattern, now, path, mags):
    magazines=None
    reader = FileReader(pattern, path)
    if pattern.endswith(".html")==True and reader.validate_url(path)==True:
        magazines = reader.read_html_page(path)
    else:
        magazines, listOfArticles = reader.execute_with_params(pattern, path, mags)
    results = dict()
    logger.info("Read all the magazines (it took " + str(now) + "), now send them to arpa")
    mini = reader.getMinLength()
    maxi = reader.getMaxLength()
    return results, magazines, mini, maxi


def writeResultsToRDF(data, filters, counter, targetformat, inputfile, inputformat):
    """
    Prepare to write given results to a rdf format. By default use turtle format.
     
    `inputfile` is the name of the rdf file to be used as a base for creating a targetfile.
    `targetfile` is the output file's file name.
    `targetformat` is the output file's file format.
    `counter` is file counter that contains a integer. Used to name outputfiles.
    'filters' contains possible filtering information.
    'data' contains the data that is going to be written into the output file.
    """
    try:
        writeToRDF = updateRDF()
        outputfile = "target_file/target"+str(counter)+".ttl"
        if targetformat == "nquads":
            outputfile = "target_file/target"+str(counter)+".nq"
        #writeToRDF.process(inputfile, inputformat, outputfile, targetformat, data, filters)
        writeToRDF.process(inputfile, inputformat, outputfile, targetformat, data, filters)
    except Exception as e:
        print("Error during execution")
        print("Unexpected error while formatting rdf ", e)
        error = traceback.format_exc()
        print(error.upper())


def executeAnnotator(logger, startTime, datetime, confpath, pattern, paths):
    print("execute Annotator")
    momentum = datetime.now()
    now = momentum - startTime
    l = list(paths)
    for path in l:
        mags = results = None
        mags, results = readKataMagazines(logger)
        units = None
        magazines = None
        results, magazines, minl, maxl = readFile(logger, pattern, now, path, mags)
        annotator = Annotator(None, confpath)
        units = annotator.doAnnotationWithConfig(results, mags, magazines)
        momentum = logQueryData(logger, momentum, units, None)
        print("execute Annotator")
    
    
    writeResultsToRDF(units)
    
    now = datetime.now() - momentum
    end = datetime.now() - startTime
    
    print("Finished queries in " + str(now))
    print("REACHED THE END in " + str(end))
    logger.info("Application execution ended, and it lasted for " + str(end))

def writeXmlOutput(results):
    
    #zip old files first
    stamp=time.time() * 1000
    output = "backup/xml_output."+str(stamp)+".zip"
    zipf = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)
    utils.zipdir('xml_output/', zipf)
    zipf.close()
    
    for magazine in results:
        articles = magazine.get_articles()
        for article in articles:
            document_id=(str(magazine.get_name()).replace(":","")+str(article.get_title())).replace("/","_").replace(" ","_").replace("__","_")
            document_name = "xml_output/"+document_id + ".xml"
            f = open(document_name,'w')
            xml = article.get_full_text_in_xmlformat()
            f.write(xml) # python will convert \n to os.linesep
            f.close()
                        
def writeTextOutput(results):
    
    #zip old files first
    stamp=time.time() * 1000
    output = "backup/old_logs."+str(stamp)+".zip"
    zipf = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)
    utils.zipdir('log/', zipf)
    zipf.close()
    
    for magazine in results:
        articles = magazine.get_articles()
        for article in articles:
            document_id=(str(magazine.get_name()).replace(":","")+str(article.get_title())).replace("/","_").replace(" ","_").replace("__","_")
            document_name = "log/"+document_id + "_FULLTEXT_" + ".txt"
            f = open(document_name,'w')
            xml = article.get_article_full_text()
            f.write(xml) # python will convert \n to os.linesep
            f.close()
            
def writeCSVOutputOfResults(magazines):
    if magazines != None:
        fileResults=CSVWriter()
        
        #zip old files first
        stamp=time.time() * 1000
        output = "backup/old_csv_log."+str(stamp)+".zip"
        zipf = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)
        utils.zipdir('csv_log/', zipf)
        zipf.close()
        
        for mId, magazine in enumerate(magazines):
            filename="TEST_"+magazine.get_name()+"_"+magazine.get_volume()+"_"+magazine.get_issue()
            filename = "csv_log/"+filename.replace("/","_")+".csv"
            fileResults.writeMagazineCSV(filename, magazine)


def get_limits(ind, limits, rank_range, document_len):
    #document lengths
    limit_min_range = limits[0]
    limit_max_range = limits[1]
    
    #defined in configs
    rank_range_min = rank_range[ind][0]
    rank_range_max = rank_range[ind][1]
    
    limit = 0
    rank_range_c = rank_range[ind][2]
    number_of_ranges = (rank_range_max - rank_range_min) +1
    range_limit = (limit_max_range - limit_min_range) / number_of_ranges
    range_count = range_limit + limit_min_range
    if document_len < range_count:
        return rank_range_min
    while ((document_len > range_count) and (range_count <= limit_max_range)):
        limit = limit + 1
        range_count = range_limit + range_count
        
    return limit

def apply_weights(results, corpus_weights, ranked_type, logger, limits, rank_range, rellim):
    for magazine in results:
        articles = magazine.get_articles()
        for article in articles:
            ranked_concepts=list()
            article_id = str(article.get_id())
            if len(article_id)>0:
                
                #take document specific weight into use here
                document_id=(str(magazine.get_name()).replace(":","")+str(article.get_title())).replace(" ","_").replace("__","_")
                weights=corpus_weights[document_id]
                tf_idf_labels = weights.keys()
                weight_list = list()

                #give a weight for each recognized term
                concept_container = article.get_consepts()
                if concept_container != None:
                    l = concept_container.get_consepts()
                    for concept in l:
                        label = concept._getLabel().lower()
                        index = concept.getIndex()
                        if (index in tf_idf_labels) and (concept.getType() in ranked_type):
                            #limit = get_limits(concept.getType(), limits, rank_range, article.get_len())
                            w = weights[index]
                            concept.setWeight(w)
                            #if len(ranked_concepts) < limit:
                            #    ranked_concepts.append(concept)
                            weight_list.append(w)
                        elif (concept.getType() not in ranked_type):
                            w = 0
                            if index in tf_idf_labels:
                                w = weights[index]
                                concept.setWeight(w)
                            #if w >= limit:
                            #    ranked_concepts.append(concept)
                            ranked_concepts.append(concept)
                    if len(weight_list)>0: 
                        weight_list.sort()
                        ranked_concepts=get_top_consepts(ranked_type, ranked_concepts, l,  limits, rank_range, article.get_len(), weight_list, rellim)
                      
                            
                #print("For article "+str(article)+" ranked concept_container are : "+str(ranked_concepts))
                logger.debug("For article "+str(article)+" ranked concept_container are : "+str(ranked_concepts))
                concept_container.set_ranked_consepts(ranked_concepts)
                #concept_container.set_consepts(ranked_concepts)
            else:
               print("Skipped article "+str(article))
               #print("Article ID:"+article_id)
                        

def get_top_consepts(ranked_type, ranked_concepts, consepts,  limits, rank_range, art_len, weight_list, rellim):
    #print("FILTERING")
    #print(limits)
    #print(rank_range)
    for c in consepts:
        if c.getType() in ranked_type:
            #limit = limits
            limit = get_limits(c.getType(), limits, rank_range, art_len)
            weights = c.getWeight()
            i = (len(weight_list))-limit
            if (i < 0):
                i = (len(weight_list))-1
            #if lim <= weights:
            if rellim <= weights and len(ranked_concepts) < limit:
                ranked_concepts.append(c)
                #print("INSERTing...")
                #print(limit)
                #print(art_len)
            
    return ranked_concepts

"""
Main - program. Requires parameters.
"""

def extractConfigurations(argv):
    configfile = ''
    inputfilepath = ''
    special=''
    csvlogging = False
    target_format = source_format = "turtle"
    source_file="source_file/tar.ttl"#"source_file/kata.source.ttl"
    #source_file="source_file/source.ttl"#"source_file/kata.source.ttl"
    #source_file="source_file/kata.source.ttl"
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('test.py -i <configfile> -o <inputfilepath>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -c <configfile> -i <inputfilepath> -is -p <filepattern>')
            sys.exit()
        elif opt in ("-c", "--cfile"):
            configfile = arg
        elif opt in ("-i", "--ifile"):
            inputfilepath = arg
        elif opt in ("-p", "--filepattern"):
            filepattern = arg
        elif opt in ("-is", "--isfilesource"):
            source = [line for line in open(inputfilepath, 'r')]
        elif opt in ("-csv", "--logtocsv"):
            csvlogging = True
        elif opt in ("-sfi", "--sourcefile"):
            source_file = arg
        elif opt in ("-sf", "--sourceformat"):
            source_format = arg
        elif opt in ("-tf", "--targetformat"):
            target_format = arg
        elif opt in ("-if", "--inputformat"):
            format = arg
        elif opt in ("--special"):
            special = "kata"
    
    print('Config file is "', configfile)
    print('Input file path is "', inputfilepath)
    print('Input file filepattern is "', inputfilepath)
    #special="kata"
    
    #configfile = "conf/warsa.conf.ini"
    #configfile = "conf/finlex-default.conf.ini"#"conf/warsa.conf.ini"
    #configfile = "conf/finlex-new.conf.ini"#"conf/warsa.conf.ini"
    configfile = "conf/finlex-comp.conf.ini"#"conf/warsa.conf.ini"
    
    #kata sources
    #inputfilepath = "source_file/kata_read.txt" #semi-automatically fixed regex
    #inputfilepath = "source_file/kata_read_test.txt" #test
    #inputfilepath = "source_file/kata_read_two.txt" #unfixed, pure ocr translations
    #inputfilepath = "source_file/kata_read_fixed.txt" #regex fixes applied
    #inputfilepath = "source_file/konilotat.txt"
    
    #finlex sources
    #inputfilepath = "source_file/output.txt"#"source_file/kata_read_test.txt"
    #inputfilepath = "source_file/chapters.txt"#"source_file/kata_read_test.txt"
    inputfilepath = "source_file/read_1.txt"#"source_file/kata_read_test.txt"
    
    #filepattern = ".tes.txt"
    #filepattern = ".txt.txt"
    format = "html" #"txt"
    #format = "txt"
    filepattern="fin.html"
    if format == "html":
        inputfilepath = [line.strip() + "/" + filepattern for line in open(inputfilepath, 'r')]
    elif format == "txt":
        inputfilepath = [line.strip() for line in open(inputfilepath, 'r')]
    return configfile, filepattern, inputfilepath, csvlogging, target_format, source_file, source_format, special

def logCandicates(logger, full_list_magazines, rank):
    
    tfidf=None
    if full_list_magazines != None:
        count = 0
        tfidf, candidates, limit = do_linguistics(full_list_magazines, logger)
        #print(tfidf)
        if len(rank)>0:
            limit = 0
        #zip old files first
        stamp=time.time() * 1000
        output = "backup/old_candidate_log."+str(stamp)+".zip"
        zipf = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)
        utils.zipdir('TEST_ALL_CANDIDATES.csv', zipf)
        zipf.close()
        
        #print candidates to csv
        fileResults=CSVWriter()
        fileResults.writeCandidatesCSV("TEST_ALL_CANDIDATES.csv", candidates, limit)
        
        #log candidates
        logger.debug("Candidates for each magazine: ")
        for candidate in candidates:
            count = 0
            logger.debug(candidate)
            candidate_list = candidates[candidate]
            for tuple in candidate_list:
            #for a,b in candidate_list:
                #if count < 21:
                a, b = tuple
                if b > limit and count < 41:
                    logger.info(str(a) + ": " + str(b))
                    count = count + 1
    
    return tfidf, limit

def checkLength(length, max_len, min_len, logger):
        if length > max_len:
            if int(min_len) <= 0 and int(max_len) > 0:
                min_len = max_len
            max_len = int(length)
        elif (length < min_len or min_len == 0) and length > 0:
            min_len = int(length)     
        return min_len, max_len 

def main(argv):
    #logging detup
    logger = logging.getLogger('myapp')
    hdlr = logging.FileHandler('/tmp/myapp.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.DEBUG)
    
    startTime = datetime.now()
    logger.info("Application execution started at " + str(startTime))
    
    #retrieve options for this job
    configfile, filepattern, inputfilepath, csvlogging, target_format, source_file, source_format, special = extractConfigurations(argv)
    
    momentum = datetime.now()
    now = momentum - startTime
    units=None
    counter=1
    annotator = Annotator(None, configfile)
    
    full_list_magazines=None
    minm = 0
    maxm = 0 
    print(filepattern)
    print(inputfilepath)
    print(configfile)
    #kata=True   
 
    for path in inputfilepath:
        try:
            mags=results=None
            #print("Before anything")
            #print(full_list_magazines)
            if special == "kata":
                mags, results = readKataMagazines(logger)
        
            magazines=None
            results, magazines, min, max = readFile(logger, filepattern, now, path, mags)
            minm, maxm=checkLength(min,minm, maxm, logger)
            minm, maxm=checkLength(max,minm, maxm, logger)
            #print("After reading files")
            #print(minm)
            #print(maxm)
            #print(results)
            #print(magazines)
            #print(full_list_magazines)
            u = annotator.doAnnotationWithConfig(results, mags, magazines, csvlogging, units)
            #print("After annotating them")
            #print(magazines)
            if full_list_magazines != None:
                for m in magazines:
                    if m not in full_list_magazines:
                        full_list_magazines.append(m)
                #print(magazines)
                #print(full_list_magazines)
            else:
                full_list_magazines=magazines
           
            #for m in full_list_magazines:
            #    print(m)
 
            if units != None:
                #units.extend(u)
                for node in u:
                    if node not in units:
                        units.append(node)
            else:
                units = u
            logger.info("Processed "+str(counter)+"/"+str(len(inputfilepath)))
            counter = counter + 1
            #print("After everything")
            #print(full_list_magazines)
            
            #if counter == 10:
                #remove this later
        except Exception as e:
            print("Error happened during execution: "+str(path))
            print("Error happened during execution: "+str(e))
            logger.warn("Unexpected error while processing data " + str(path) + ":", e)
            error = traceback.format_exc()
            print(error.upper())

    if full_list_magazines != None:
        writeTextOutput(full_list_magazines)
    else:
        logger.error("magaine list is empty!")
    
    rank = annotator.doRanking()
    tfidf, limit = logCandicates(logger, full_list_magazines, rank)
    #logger.debug(tfidf)
    if units != None:
        print("Check ranking" + str(limit))
        rank, rank_range = annotator.doRanking()
        print(len(rank))
        if len(rank)>0:
            limits = (minm, maxm)
            logger.info("Execute candidate ranking for "+str(rank)+ " "+ str(limit))
            apply_weights(units, tfidf, rank, logger, limits, rank_range, limit)
            #use when using ranges
            #apply_weights(units, tfidf, rank, logger, limits, rank_range)
        print("convert to rdf")
        writeResultsToRDF(units,annotator,counter, target_format, source_file, source_format)  
        writeXmlOutput(full_list_magazines)
        writeCSVOutputOfResults(full_list_magazines)
        annotator.writeToCSV(full_list_magazines)
        annotator.logConseptsByIndex(full_list_magazines)
        
        #writeResultsToRDF(u,annotator,counter, target_format, source_file, source_format)
    annotator.print_filtered_terms(full_list_magazines)
    annotator.print_included_terms(full_list_magazines)
    annotator.print_stats(full_list_magazines)
    
    now = datetime.now() - momentum
    end = datetime.now() - startTime
    
    print("Finished queries in " + str(now))
    print("REACHED THE END in " + str(end))
    logger.info("Application execution ended, and it lasted for " + str(end))
    
if __name__ == '__main__':
    stamp=int(time.time() * 1000)
    outputfile = "target_file/old_targets."+str(stamp)+".zip"
    zipf = zipfile.ZipFile(outputfile, 'w', zipfile.ZIP_DEFLATED)
    utils.zipdir('target_file/', zipf)
    zipf.close()
    main(sys.argv[1:])
    
