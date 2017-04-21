# coding: utf8
'''
Created on 5.4.2016

@author: Claire
'''
from las_query import lasQuery
import utils, time
import json
import sys
import logging
import re, math

logger = logging.getLogger('linguistics')
hdlr = logging.FileHandler('/tmp/linguistics.log')
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)


class linguistics(object):
    '''
    classdocs
    '''


    def __init__(self, corpus):
        '''
        Constructor
        '''
        self._candidates = dict()
        self._avg_tfidf_score = 0
        if corpus != None:
            self.corpuses = corpus
        else:
            self.corpuses = dict()
    def get_avg_tfidf_score(self):
        return self._avg_tfidf_score
    def average_tfidf_score(self, tfidf):
        '''
        >>> ling = linguistics({'doc1' : 'nainen eläin hevonen maatila tytär eläinlääketiede opiskelija maatalousylioppilas Lotta Svärd toimisto jatkosota kevät maatalousylioppilas joukko kehotus Kintausi eläinlääkintäkurssi kurssin johtaja eläinlääkintäeversti Staufer', 'doc2' : 'komento kenttähevossairaala 16. kenttähevossairaala sijoituspaikka Kolatselkä Jessoilat Essoila Äänislinna Petroskoi työ eläinlääkäri assistentti instrumentti leikkaus eläinlääkäri sirpale haava tuffari Esimies kuva rauhallisuus ystävä ruotsalainen vapaaehtoinen veterinääri', 'doc3' : 'hevonen etujalka takajalka side nivel kurssi johtaja eläinlääkäri potkuri hevonen kavio Eversti Staufer tyttö kurssi hevonen jalka jatkokurssi trikiinikurssi eläinlääketieteellinen korkeakoulu laboratorio pieneläjä vihollinen'})
        >>> tfidf = {'doc2': {'sijoituspaikka': 0.042254318794927304, 'komento': 0.042254318794927304, 'kuva': 0.042254318794927304, 'esimies': 0.042254318794927304, 'jessoilat': 0.042254318794927304, 'kentt\xc3\xa4hevossairaala': 0.08450863758985461, 'instrumentti': 0.042254318794927304, 'veterin\xc3\xa4\xc3\xa4ri': 0.042254318794927304, 'essoila': 0.042254318794927304, 'rauhallisuus': 0.042254318794927304, 'sirpale': 0.042254318794927304, 'assistentti': 0.042254318794927304, 'tuffari': 0.042254318794927304, 'petroskoi': 0.042254318794927304, 'el\xc3\xa4inl\xc3\xa4\xc3\xa4k\xc3\xa4ri': 0.03118962370062803, 'ruotsalainen': 0.042254318794927304, 'haava': 0.042254318794927304, 'leikkaus': 0.042254318794927304, 'vapaaehtoinen': 0.042254318794927304}, 'doc3': {'nivel': 0.0457755120278379, 'el\xc3\xa4inl\xc3\xa4\xc3\xa4k\xc3\xa4ri': 0.016894379504506847, 'trikiinikurssi': 0.0457755120278379, 'johtaja': 0.0457755120278379, 'kurssi': 0.0915510240556758, 'kavio': 0.0457755120278379, 'jalka': 0.0457755120278379, 'laboratorio': 0.0457755120278379, 'vihollinen': 0.0457755120278379, 'jatkokurssi': 0.0457755120278379, 'takajalka': 0.0457755120278379, 'etujalka': 0.0457755120278379, 'korkeakoulu': 0.0457755120278379, 'hevonen': 0.05068313851352055, 'potkuri': 0.0457755120278379, 'el\xc3\xa4inl\xc3\xa4\xc3\xa4ketieteellinen': 0.0457755120278379, 'side': 0.0457755120278379, 'eversti': 0.0457755120278379}, 'doc1': {'tyt\xc3\xa4r': 0.04993692221218681, 'el\xc3\xa4inl\xc3\xa4\xc3\xa4kint\xc3\xa4kurssi kurssin johtaja': 0.04993692221218681, 'opiskelija': 0.04993692221218681, 'joukko': 0.04993692221218681, 'el\xc3\xa4inl\xc3\xa4\xc3\xa4ketiede': 0.04993692221218681, 'el\xc3\xa4inl\xc3\xa4\xc3\xa4kint\xc3\xa4eversti staufer': 0.04993692221218681, 'el\xc3\xa4in': 0.04993692221218681, 'kehotus': 0.04993692221218681, 'maatila': 0.04993692221218681, 'nainen': 0.04993692221218681, 'jatkosota': 0.04993692221218681, 'hevonen': 0.018430232186734747, 'kintausi': 0.04993692221218681, 'maatalousylioppilas': 0.09987384442437362, 'kev\xc3\xa4t': 0.04993692221218681, 'toimisto': 0.04993692221218681, 'lotta': 0.04993692221218681}}
        >>> ling.average_tfidf_score(tfidf)
        0.04730122201240098
        '''
        #calc = dict()
        avgsum = 0
        termsum = 0
        avg = 0
        try:
            for document_name in tfidf:
                terms=tfidf[document_name]
                termsum=0
                for term in terms:
                    termsum = terms[term] + termsum
                avgsum = (termsum / len(tfidf[document_name])) + avgsum
            #calc[document_name] = avgsum
            avg = avgsum / len(tfidf.keys())
        except Exception as e:
            logger.warn("Error happened during avg calculations")
            logger.warn(e)
            return 0
        return avg
 
    def tf_idf(self, cutoff=0):
        '''
        >>> ling = linguistics({'doc1' : 'nainen eläin <annotation> hevonen </annotation> maatila tytär <annotation> eläinlääketiede </annotation> opiskelija maatalousylioppilas <annotation> Lotta Svärd </annotation> toimisto jatkosota kevät maatalousylioppilas joukko kehotus Kintausi <annotation> eläinlääkintäkurssi kurssin johtaja </annotation> <annotation> eläinlääkintäeversti Staufer </annotation>', 'doc2' : 'komento kenttähevossairaala 16. kenttähevossairaala sijoituspaikka <annotation> Kolatselkä </annotation> <annotation> Jessoilat </annotation> Essoila Äänislinna Petroskoi työ <annotation> eläinlääkäri </annotation> assistentti instrumentti leikkaus <annotation> eläinlääkäri </annotation> sirpale haava tuffari Esimies kuva rauhallisuus ystävä ruotsalainen vapaaehtoinen veterinääri', 'doc3' : '<annotation> hevonen </annotation> etujalka takajalka side nivel kurssi johtaja <annotation> eläinlääkäri </annotation> potkuri <annotation> hevonen </annotation> kavio <annotation> Eversti Staufer </annotation> tyttö kurssi <annotation> hevonen </annotation> jalka <annotation> jatkokurssi </annotation> trikiinikurssi eläinlääketieteellinen korkeakoulu <annotation> laboratorio </annotation> pieneläjä vihollinen'}) 
        >>> ling.tf_idf()
         {'doc2': {'sijoituspaikka': 0.042254318794927304, 'komento': 0.042254318794927304, 'kuva': 0.042254318794927304, 'esimies': 0.042254318794927304, 'jessoilat': 0.042254318794927304, 'kentt\xc3\xa4hevossairaala': 0.08450863758985461, 'instrumentti': 0.042254318794927304, 'veterin\xc3\xa4\xc3\xa4ri': 0.042254318794927304, 'essoila': 0.042254318794927304, 'rauhallisuus': 0.042254318794927304, 'sirpale': 0.042254318794927304, 'assistentti': 0.042254318794927304, 'tuffari': 0.042254318794927304, 'petroskoi': 0.042254318794927304, 'ruotsalainen': 0.042254318794927304, 'haava': 0.042254318794927304, 'leikkaus': 0.042254318794927304, 'vapaaehtoinen': 0.042254318794927304}, 'doc3': {'nivel': 0.0457755120278379, 'trikiinikurssi': 0.0457755120278379, 'johtaja': 0.0457755120278379, 'kurssi': 0.0915510240556758, 'kavio': 0.0457755120278379, 'jalka': 0.0457755120278379, 'laboratorio': 0.0457755120278379, 'vihollinen': 0.0457755120278379, 'jatkokurssi': 0.0457755120278379, 'takajalka': 0.0457755120278379, 'etujalka': 0.0457755120278379, 'korkeakoulu': 0.0457755120278379, 'potkuri': 0.0457755120278379, 'el\xc3\xa4inl\xc3\xa4\xc3\xa4ketieteellinen': 0.0457755120278379, 'side': 0.0457755120278379, 'eversti': 0.0457755120278379}, 'doc1': {'tyt\xc3\xa4r': 0.04993692221218681, 'el\xc3\xa4inl\xc3\xa4\xc3\xa4kint\xc3\xa4kurssi kurssin johtaja': 0.04993692221218681, 'opiskelija': 0.04993692221218681, 'joukko': 0.04993692221218681, 'el\xc3\xa4inl\xc3\xa4\xc3\xa4ketiede': 0.04993692221218681, 'el\xc3\xa4inl\xc3\xa4\xc3\xa4kint\xc3\xa4eversti staufer': 0.04993692221218681, 'el\xc3\xa4in': 0.04993692221218681, 'kehotus': 0.04993692221218681, 'maatila': 0.04993692221218681, 'nainen': 0.04993692221218681, 'jatkosota': 0.04993692221218681, 'kintausi': 0.04993692221218681, 'maatalousylioppilas': 0.09987384442437362, 'kev\xc3\xa4t': 0.04993692221218681, 'toimisto': 0.04993692221218681, 'lotta': 0.04993692221218681}}
        '''
        tfidf = dict()
        for corpus in self.corpuses:
            text = self.corpuses[corpus]
            #print(text)#logger.debug(corpus)
            tf = self.tf(text.lower(), corpus)
            print(tf)
            tfidf[corpus]=tf
            tf_len=len(tf)
            tf2_len=len(tfidf[corpus])
            if tf_len < 100:
                logger.debug("For corpus "+str(corpus)+" the given tf (LEN="+str(tf2_len)+") is "+str(tfidf[corpus])[0:tf2_len])
                logger.debug("For corpus "+str(corpus)+" the given tf (LEN="+str(tf_len)+") is "+str(tf)[0:tf_len])
            else:
                logger.debug("For corpus "+str(corpus)+" the given tf (LEN="+str(tf2_len)+") is "+str(tfidf[corpus])[0:300])
                logger.debug("For corpus "+str(corpus)+" the given tf (LEN="+str(tf_len)+") is "+str(tf)[0:300])
        result = self.idf(tfidf, cutoff)
        self._candidates = self.extract_candidates(result, tfidf)
        self._avg_tfidf_score = self.average_tfidf_score(result)
        return result
        
    def extract_candidates(self,documents, tf_arr):
        candidates=dict()
        #candidate_list=list()
        logger.info(tf_arr.keys())
        for document_name in documents:
            candidate_list=list()
            terms=documents[document_name]
            for term in terms:
                tuple=(term,terms[term])
                if tuple not in candidate_list:
                    candidate_list.append(tuple)
            candidates[document_name]=sorted(candidate_list, key=lambda candidate: float(candidate[1]), reverse=True)
        return candidates
            
    def get_candidates(self):
        return self._candidates
            
    def set_corpuses(self, corpus):
        self.corpuses = corpus
        
    def tf(self, corpus, name):
        ner_term=False
        tf_list = dict()
        
        #calculate total number of words
        #BUG:fixit
        w=corpus.replace("<annotation>","").replace("</annotation>","").split(" ")
        filtered_corpus=' '.join(w).split()
        total = len(filtered_corpus)
        
        text = ' '.join(corpus.split(" ")).split()
        concept=""
        helper=""
        if name == "http://dev.finlex.seco.cs.aalto.fi/eli/sd/1937/388/fin.html":
            logger.info(text)
        for term in text:
            if term == "<annotation>":
                ner_term=True
            elif term == "</annotation>":
                helper = helper + " " +term
                ner_term=False
                if logger != None and name == "http://dev.finlex.seco.cs.aalto.fi/eli/sd/1937/388/fin.html":
                    logger.debug("tf:Recognized annotation: "+concept)
                helper=""
                
            if ner_term == True:
                helper = helper + " " +term
            
            if len(concept)<1:
                concept = term
            
            if ner_term == False:
                #t = self.count_term_in_document(concept, corpus)
                n = self.regex_count_terms_in_doc(concept.strip(), corpus.strip(), name)
                #if n != t:
                print(str(concept)+" Compare: "+str(concept)+" to "+str(n))
                if "huutokauppa" in concept and name == "http://dev.finlex.seco.cs.aalto.fi/eli/sd/1937/388/fin.html":
                    logger.debug("Printing TERM ("+str(concept)+") and its F ("+str(n)+")")
                if n > 0:
                    tf= float(float(n)/float(total))
                    if concept == "hevonen":#print(tf)
                        print(tf)
                        print(total)
                        print(n)
                    if concept not in tf_list: 
                        tf_list[concept] = tf
                    elif concept in tf_list and tf_list[concept] < n: 
                        tf_list[concept] = tf
                        print("elif "+str(concept))
                    else:
                        print("Unaccepted:"+str(concept))
                        
                    if ("huutokauppa" in concept and name == "http://dev.finlex.seco.cs.aalto.fi/eli/sd/1937/388/fin.html") or "maa" in concept or "annotation" in concept:
                        logger.debug("Printing TERM ("+str(concept)+") and its TF ("+str(tf)+")")
                #else:
                   # print(concept+" was not found from the corpus "+str(n))
                concept=""
                    
            else:
                if term != "<annotation>":
                    if len(concept)>len(term):
                        concept = concept + " " + term
                else:
                    concept=""
        return tf_list
    
    def idf(self, matrix, cutoff=0):
        tfidf_corpus = dict()
        total = len(matrix)
        for document in matrix:
            tf = matrix[document]
            if document == "http://dev.finlex.seco.cs.aalto.fi/eli/sd/1937/388/fin.html":
                logger.debug(tf)
            else:
                logger.debug(document)
            tfidf_arr = dict()
            for term in tf:
                try:
                    tf_val = tf[term]
                    n = self.check_term_in_documents(term, matrix)
                    idf = math.log(float(float(total) /float( n)))
                    tfidf = tf_val*idf
                    if tfidf > 0:
                        tfidf_arr[term]=tfidf
                    if "huutokauppa" in term :#or "maa" in term:
                        logger.debug("Printing TERM ("+str(concept)+") and its IDF (LN("+str(total)+"/"+str(n)+")="+str(tfidf)+")")
                        logger.debug("Printing TERM ("+str(concept)+") and its TF-IDF ("+str(tf_val)+"*"+str(idf)+"="+str(tfidf)+")")
                except Exception as err:
                    logger.error("Error happened while counting")
                    logger.error(format(err))
            tfidf_corpus[document]=tfidf_arr
        return tfidf_corpus
    
    def check_term_in_documents(self, term, matrix):
        c = 0
        for document in matrix:
            tf = matrix[document]
            if term in tf:
                c = c+1
        return c
    
    def regex_count_terms_in_doc(self, t, doc, name):
        n=0
        if len(t)>1:
            try:
                term = r"(?:^|[^-])\b(" + t + r")\b(?=$|[^-])"
                #term2 = t+" "
                #term3 = " "+t+"\n"
                n =len(re.findall(term, doc, re.IGNORECASE))
                #print(str(t)+" appears " + str(n)+" times.")
                if "huutokauppa" in t and name == "http://dev.finlex.seco.cs.aalto.fi/eli/sd/1937/388/fin.html":# or "maa" in t:
                    logger.debug("Printing TERM ("+str(t)+") and its count ("+str(n)+")")
            except Exception as e:
                print("Failed with pattern :"+term)
                print(e)
                #term = "\b"+t+"\b"
                #n = len(re.findall(term, doc))
        return n
    
    def count_term_in_document(self, t, doc):
        c=0
        ner_term=False
        helper=""
        concept=""
        skip_concept=False
        for term in doc.split(" "):
            if len(term.strip())>1:
                if term == "<annotation>":
                    helper=""
                    ner_term=True
                elif term == "</annotation>":
                    helper = helper + " " +term
                    ner_term=False
                    #print("count_term_in_document: Recognized annotation: "+concept)
                    skip_concept=True
                    
                if ner_term == False:
                    if term == t:
                        c=c+1
                        concept=""
                    elif concept == t:
                        c=c+1
                        concept=""
                    elif concept != t and skip_concept== True:
                        #print("count_term_in_document: Skip: "+concept)
                        skip_concept=False
                        concept=""
                else:
                    if term != "<annotation>":
                        concept = concept + " " + term
                    else:
                        concept=""
                        
        #print(t+" was found "+c+" times...")
        return c
        
    def baseform(self, text):
        baseform = ""
        annotation_mode=False
        las = lasQuery()
        stopwordlist="conf/stop-words_finnish_3_own_additions_fi.txt"
        filtered_words = self.read_stoplist(stopwordlist)
        #if logger != None:
        #    logger.debug("Text before baseforming...")
        #    logger.debug(text)
        #text = self.filter_texts_using_stopwords(text.lower())
        inputtext = text.split(' ')
        logger.info("STARTING BASEFORMING ")
        #logger.debug(inputtext)
        for input in inputtext:
            #if len(input) > 100:
            if input == "<annotation>":
                annotation_mode=True
            elif input == "</annotation>":
                annotation_mode=False
                
            if annotation_mode == False and (input != "</annotation>"):
                value = self.stripInput(input)
                if len(value) > 2 and value not in filtered_words:
                    baseformRes = las.analysis(value)
                    if len(baseformRes) > 1 and baseformRes not in filtered_words:
                        baseform = baseform + " " + str(baseformRes)
            else:
                #if input != "</annotation>" and input !="<annotation>":
                #logger.debug("Skipping las "+input)
                if len(input)>1:
                    baseform = baseform + " " + input
                
        #if logger != None:
            #logger.debug("Text after baseforming...")
            #logger.debug(baseform)
                
        return baseform
    
    def do_tfidf(self, documents):
        corpus = dict()
        for id in documents:
            corpus[id] = self.baseform(documents[id])
            logger.debug(str(id)+" of LEN "+str(len(corpus[id])))
            #logger.info(documents[id])
            #logger.info(corpus[id])
        #print(len(corpus))
        self.corpuses=corpus
        self.write_to_file()
        tfidf_res=self.tf_idf()
        #logger.debug(tfidf_res)
        #print(tfidf_res)
        return tfidf_res
    
    def stripInput(self, value):
        q=""
        try:
            stripped = value.strip().strip("[]").strip("()").strip("{}")
            qstr = stripped.format()
            q = re.sub('\s+', ' ', qstr)
            q = q.replace('*', '').replace('§', '').replace('€', '').replace('^', '').replace("@", '').replace("+", '').replace("?", '').replace("_", '').replace("%", '')
            q = q.replace('^', '').replace('[', '').replace(']', '').replace('{', '').replace("}", '').replace("#", '').replace("~", '').replace("(", '').replace(")", '')
            q = q.replace('*', '').replace('^', '').replace("@", '').replace("+", '').replace("?", '').replace("_", '').replace("%", '').replace("...",'').replace("|",'').replace("..",'').replace("■",'').replace("£",'')
            q = q.replace('^', '').replace('[', '').replace(']', '').replace('{', '').replace("}", '').replace("#", '').replace("~", '').replace('"', '').replace("+", '')
            q = q.replace('•', '').replace('&', '').replace('´', '').replace('`', '').replace("§", '').replace("½", '').replace("=", '').replace('¤', '').replace("$", '').replace("--",'').replace(",,",'').replace("»",'').replace("—",'')
            q = q.replace('“', '').replace(' . ', '').replace("”", '').replace(".,", '').replace(',.', '').replace("“", '').replace(",,,",'').replace("'",'').replace("«",'').replace("..",'')
            text="" 
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
            
            bad_chars = '(){}'
            rgx = re.compile('[%s]' % bad_chars)            
            text = rgx.sub('', text)    # replace parenthesis symbol
            
            text = re.sub(r'\d\d.\d\d.\d\d\d\d',"",text) #dates
            text = re.sub(r'\d{1,2}.\d\d.',"",text) #times
            
            text = re.sub(r'((\.|\s)+)', "", text)
            text = re.sub(r'((\,|\s)+)', "", text)
            text = re.sub(r'(\,+)', "", text)
            
        
            # Do you want to keep new lines / carriage returns? These are generally 
            # okay and useful for readability
            q = re.sub(r'[\n\r]+', ' ', text)     # remove embedded \n and \r
        
            # This is a hard-core line that strips everything else.
            #q = re.sub(r'[\x00-\x1f\x80-\xff]', ' ', text)
            
        except ValueError as err:
            logger.warn("Unexpected error while formatting text " + value + ":", err)
            q = value
        except Exception as e:
            logger.warn("Unexpected error while formatting text " + value + ":", e)
            q = value
        return q
    
    def write_to_file(self):
        for corpus in self.corpuses:
            filename=corpus.replace("/","_").replace("http:","") + ".txt"
            f = open(filename,'w')
            f.write(self.corpuses[corpus]) # python will convert \n to os.linesep
            f.close()

    def filter_texts_using_stopwords(self, input):
    	stopwordlist="conf/stop-words_finnish_3_own_additions_fi.txt"
    	filtered_words = self.read_stoplist(stopwordlist)
    	#print(filtered_words)
    	text = ' '.join([i for i in re.findall(r'\S+', input) if i not in filtered_words])
    	words=re.findall(r'\S+', input)
    	skip = False
    	t = ""
    	if skip != False:
            for item in words:
    	        prev, next = self.find_prev_next(item, words)
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
    def read_stoplist(self,filename):
    	stoplist = [line.strip().lower() for line in open(filename, 'r')]
    	return stoplist
    def find_prev_next(self,elem, elements):
        previous, next = None, None
        index = elements.index(elem)
        if index > 0:
            previous = elements[index -1]
        if index < (len(elements)-1):
            next = elements[index +1]
        return previous, next


