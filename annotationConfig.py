from query.ArpaQueryExecuter import ArpaQueryExecuter
from FileReader import FileReader
from JSONParser import JSONParser
from query.arpa import Arpa
from query.sparql.sparqual_query import sparqlQuery
from datetime import datetime
from article import Article
from magazine import Magazine
import utils
import json
import sys
import logging
import os
import re
import ast, sys
#from test.test_os import TermsizeTests

logger = logging.getLogger('AnnotatorConfig')
hdlr = logging.FileHandler('/tmp/annotator.log')
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)
	
LOG_SUCCESS=True
LOG_PROBLEMS=True

class AnnotatorConfig(object):
	
	def __init__(self, url="", name="", bDuplicates=False, min_ngram_length=1, ignore=None, prop=None, graph=None, primary=None, secondary=None, third=None, limit=0, stopwords="", ranking=False, ranking_max_range=0, ranking_min_range=0, ordered=False):
		self.__url=url
		self.__name=name
		self.__remove_duplicates=ast.literal_eval(bDuplicates)
		self.__min_ngram_length=int(min_ngram_length)
		self.__ignore=ignore
		self.__target_property=prop
		self.__target_graph=graph
		self.__primary=primary
		self.__secondary=secondary
		self.__third=third
		self.__limit=int(limit)
		self.__stopwords=stopwords
		self.__ranking=ast.literal_eval(ranking)
		self.__ordered=ast.literal_eval(ordered)
		self.__ranking_min_range=int(ranking_min_range)
		self.__ranking_max_range=int(ranking_max_range)
		logger.info("Setting config: "+str(self))

	def get_min_range(self):
            return self.__ranking_min_range
	def get_max_range(self):
            return self.__ranking_max_range
	def get_ranking(self):
		return self.__ranking

	def get_primary(self):
	    return self.__primary
	def set_ordered(self, value):
	    self.__ordered = ast.literal_eval(value)
	def get_ordered(self):
	    return self.__ordered

	def get_secondary(self):
	    return self.__secondary


	def get_third(self):
	    return self.__third


	def set_primary(self, value):
	    self.__primary = value


	def set_secondary(self, value):
	    self.__secondary = value


	def set_third(self, value):
	    self.__third = value


	def del_primary(self):
	    del self.__primary


	def del_secondary(self):
	    del self.__secondary


	def del_third(self):
	    del self.__third


	def get_url(self):
		return self.__url


	def get_name(self):
		return self.__name


	def get_remove_duplicates(self):
		return self.__remove_duplicates


	def get_min_ngram_length(self):
		return self.__min_ngram_length

	def get_stopwordlist(self):
		print(self.__stopwords)
		return self.read_stoplist(self.__stopwords)      
	def get_ignore(self):
		return self.__ignore
	   
	def get_target_property(self):
		return self.__target_property

	def set_url(self, value):
		self.__url = value
		
	def get_uri_filter(self):
		if self.__primary == None:
			if self.__secondary == None:
				if self.__third == None:
					return None, 0
				else:
					return self.__third, 3
			else:
				return self.__secondary, 2
		else:
			return self.__primary, 1

	def get_frequence_filter(self, terms): #add a check if limit is 0 -> return terms
		accepterdterms=[]
		if self.__limit < 1:
			return terms
		for term in terms:
			uris=term.retrieve_link_uris()
			if term.get_frequency()>self.__limit:
				accepterdterms.append(term)
			elif len(uris)>1:
				accepterdterms.append(term)
		return accepterdterms
	def read_stoplist(self,filename):
		stoplist = [str(line).strip().lower() for line in open(filename, 'r',encoding='utf-8', errors='ignore')]
		return stoplist
     
	def filter_terms_using_stopwordlist(self, terms):
		accepterdterms=[]
		filtered_words = self.read_stoplist(self.__stopwords)
		for term in terms:
			label = term._getLabel()
			if label not in filtered_words:
				accepterdterms.append(term)
	def filter_using_stopwordlist(self, term):
		filtered_words = self.read_stoplist(self.__stopwords)
		label = term._getLabel()
		if label.lower() not in filtered_words:
			return False
		return True
	def filter_using_frequency(self, term):
		if term.get_frequency()>self.__limit:
			return False
		return True
	
	
	def set_name(self, value):
		self.__name = value


	def set_remove_duplicates(self, value):
		self.__remove_duplicates = value


	def set_min_ngram_length(self, value):
		self.__min_ngram_length = value


	def set_ignore(self, value):
		self.__ignore = value
		
	def set_target_property(self, value):
		self.__target_property = value


	def del_url(self):
		del self.__url


	def del_name(self):
		del self.__name


	def del_remove_duplicates(self):
		del self.__remove_duplicates


	def del_min_ngram_length(self):
		del self.__min_ngram_length


	def del_ignore(self):
		del self.__ignore
		
	def __repr__(self):
		return ""+self.__name+ " ( "+str(self.__url)+" )"
	
	def __str__(self):
		return ""+self.__name+ " ( "+str(self.__url)+" ) with the following setup: min_ngram_length="+str(self.__min_ngram_length)+" remove_duplicates="+str(self.__remove_duplicates)+" ignore="+str(self.__ignore) +" target_property="+str(self.__target_property)+" execute candidate ranking="+str(self.__ranking)

	url = property(get_url, set_url, del_url, "url's docstring")
	name = property(get_name, set_name, del_name, "name's docstring")
	remove_duplicates = property(get_remove_duplicates, set_remove_duplicates, del_remove_duplicates, "remove_duplicates's docstring")
	min_ngram_length = property(get_min_ngram_length, set_min_ngram_length, del_min_ngram_length, "min_ngram_length's docstring")
	ignore = property(get_ignore, set_ignore, del_ignore, "ignore's docstring")
	primary = property(get_primary, set_primary, del_primary, "primary's docstring")
	secondary = property(get_secondary, set_secondary, del_secondary, "secondary's docstring")
	third = property(get_third, set_third, del_third, "third's docstring")
		
