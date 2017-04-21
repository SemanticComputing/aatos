'''
Created on 17.2.2016

@author: Claire
'''
import urllib, codecs
from requests import Request, Session
import requests, json, logging

logger = logging.getLogger('lasQuery')
hdlr = logging.FileHandler('/tmp/linguistics.log')
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)

class lasQuery:
    def __init__(self, file_name_pattern="", path="", full_path=""):
        self.__file_name_pattern = file_name_pattern
        self.__path = path
        
    def analysis(self, input):
        res = " "
        j = self.morphological_analysis(input)
        reader = codecs.getreader("utf-8")
        prevword=""
        upos=""
        for w in j:
            word = w['word']
            analysis = w['analysis']
            for r in analysis:
                if word != prevword and len(upos)<1:
                    prevword=word
                    wp = r['wordParts']
                    for part in wp:
                        lemma = part['lemma']
                        upos=""
                        if 'tags' in part:
                            p = part['tags']
                            if 'UPOS' in p:
                                p1 = p['UPOS']
                                if len(p1)>0:
                                    upos = part['tags']['UPOS'][0]
                        if upos == 'NOUN' or upos == 'PROPN':
                            res = res + lemma + " "
                
        return res
    
    #morphological_analysis    
    def morphological_analysis(self,input):
        
        # do POST
        url = 'http://demo.seco.tkk.fi/las/analyze'
        #values = dict(text=input)
        params = {'text': input, 'locale':'fi', "forms":"V+N+Nom+Sg"}
        data = urllib.parse.urlencode(params).encode()
        
        content =  None
        content = self.prepared_request_morphological(input)
        if content == None:
            return ""
        #print(str(content)+" / "+str(input))
        json=None#print(str(content)+" / "+str(input))
        try:
            json= content.json()
        except:
            json={}
            print("Unablto to produce json:"+str(content))
        return json
    
    def lexical_analysis(self,input):

        #cookie_jar = cookielib.CookieJar()
        #opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
        #urllib2.install_opener(opener)
        
        # acquire cookie
        #url_1 = 'http://www.bkstr.com/webapp/wcs/stores/servlet/BuybackMaterialsView?langId=-1&catalogId=10001&storeId=10051&schoolStoreId=15828'
        #req = urllib2.Request(url_1)
        #rsp = urllib2.urlopen(req)
        
        # do POST
        url = 'http://demo.seco.tkk.fi/las/baseform'
        #values = dict(text=input)
        params = {'text': input}
        data = urllib.parse.urlencode(params).encode()
        
        #with urllib.request.urlopen(url, data) as f:
        #    content = f.read().decode('utf-8')
        #    print(content)
            
        #url = 'http://example.com:8080/testAPI/testAPIServlet'
        
        #response = requests.post(url, data=data)
        #print(response)
        #content = rsp.read()
        
        # print result
        #import re
        #pat = re.compile('Title:.*')
        #print pat.search(content).group()
        #print(response.headers)
        #print (response.status_code, response.text, response.headers)
        #print(params)
        
        content =  None
        content = self.prepared_request(input)
        if content == None:
            return ""
        return content.content
    
    def prepared_request(self, input):
        s = Session()
        url = 'http://demo.seco.tkk.fi/las/baseform'
        #values = dict(text=input)
        #print(input)
        params = {'text': input, 'locale' : 'fi'}
        data = urllib.parse.urlencode(params).encode()
        req = Request('POST','http://demo.seco.tkk.fi/las/baseform',headers={'X-Custom':'Test'},data=params)
        prepared = req.prepare()
        
        #print(prepared.headers)
        #print(prepared.body)
        logger.info(prepared.headers)
        logger.info(prepared.body)
        #self.pretty_print_POST(req)
        
        try:
            resp = s.send(prepared)
            return resp
        except requests.ConnectionError as ce:
            logger.warn("Unable to open with native function. Error: "  + str(ce))
        return None
        
    def prepared_request_morphological(self, input):
        s = Session()
        url = 'http://demo.seco.tkk.fi/las/baseform'
        #values = dict(text=input)
        params = {'text': input, 'locale':'fi', "forms":"V+N+Nom+Sg"}
        data = urllib.parse.urlencode(params).encode()
        req = Request('POST','http://demo.seco.tkk.fi/las/analyze',headers={'X-Custom':'Test'},data=params)
        prepared = req.prepare()
        
        #print(input)
        #print(prepared.headers)
        #print(prepared.body)
        #logger.info(prepared.headers)
        #logger.info(prepared.body)
        #self.pretty_print_POST(req)
        
        try:
            resp = s.send(prepared)
            return resp
        except requests.ConnectionError as ce:
            logger.warn("Unable to open with native function. Error: "  + str(ce))
        return None
    
    def pretty_print_POST(self,req):
        """
        At this point it is completely built and ready
        to be fired; it is "prepared".
    
        However pay attention at the formatting used in 
        this function because it is programmed to be pretty 
        printed and may differ from the actual request.
        """
        print('{}\n{}\n{}\n\n{}'.format(
            '-----------START-----------',
            req.method + ' ' + req.url,
            '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
            req.body,
        ))
        
