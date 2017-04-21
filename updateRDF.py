import logging
import argparse
import requests
import time
from datetime import timedelta
from requests.exceptions import HTTPError
from rdflib import ConjunctiveGraph,Graph, URIRef
from rdflib.namespace import RDF, SKOS
from rdflib.util import guess_format
import traceback

logger = logging.getLogger('updateRDF')
hdlr = logging.FileHandler('/tmp/myapp.log')
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)

class updateRDF(object):
	
	def update(self, graph, target_prop, match_uris, rdf_class, source_prop=None, progress=None):
		if source_prop is None:
			source_prop = SKOS['prefLabel']
	
		subgraph = Graph()
	
		if rdf_class:
			# Filter out subjects that are not of the given type
			for s in graph.subjects(RDF.type, rdf_class):
				subgraph += graph.triples((s, source_prop, None))
		else:
			subgraph += graph.triples((None, source_prop, None))
	
		triple_match_count = 0
		subject_match_count = 0
		errors = []
	
		#bar = get_bar(len(subgraph), progress)
	
		for s, o in subgraph.subject_objects():
			
			triple_match_count += len(match_uris)
			if match_uris:
				subject_match_count += 1
			# Add each uri found as a value of the target property
			for uri in match_uris:
				graph.add((s, target_prop, URIRef(uri)))
			#bar.update()
	
		res = {'processed': len(subgraph), 'matches': triple_match_count,
			   'subjects_matched': subject_match_count, 'errors': errors}
	
		logger.info("Processed {} triples, found {} matches ({} errors)"
					.format(res['processed'], res['matches'], len(res['errors'])))
	
		return res
	
	
	def process(self,input_file, input_format, output_file, output_format, units, filters):
	    """
	    Parse the given input file, run `arpa.arpafy`, and serialize the resulting
	    graph on disk.
	    `input_file` is the name of the rdf file to be parsed.
	    `output_file` is the output file name.
	    `output_format` is the output file format.
	    All other arguments are passed to `arpa.arpafy`.
	    Return the results dict as returned by `arpa.arpafy` with the graph added
	    with key 'graph'.
	    """
	    g = None
	    #g.parse(input_file, format=input_format)
	    #logger.info('Parsing complete')
	    logger.info('Begin processing')
	    start_time = time.monotonic()
	    
	    res=None
	    
	    if output_format=="nquads":
	    	g = ConjunctiveGraph(identifier=filters.get_target_graph())
	    	res = self.write(g, units, filters)
	    else:
	    	g = Graph()
	    	logger.info('Parsing file {}'.format(input_file))
	    	g.parse(input_file, format=input_format)
	    	logger.info('Parsing complete')
	    	res = self.write(g, units, filters)
	
	    end_time = time.monotonic()
	
	    logger.info("Processing complete, runtime {}".
	    format(timedelta(seconds=(end_time - start_time))))
	
	    logger.info('Serializing graph as {}'.format(output_file))
	    g.serialize(destination=output_file, format=output_format)
	    logger.info('Serialization complete')
	
	    # Add the graph to the results
	    res['graph'] = g
	
	    return res
	   
	   
	def updateRDFFile(self, graph, target_prop, match_uris, subject, source_prop=None, progress=None):
		errors = []
		subject_match_count=0
		triple_match_count=0
		triple_match_count += len(match_uris)
		if match_uris:
			subject_match_count += 1
		# Add each uri found as a value of the target property
		for uri in match_uris:
			graph.add((URIRef(subject), URIRef(target_prop), URIRef(uri)))
		#bar.update()
	
		res = {'processed': len(match_uris), 'matches': triple_match_count,
			   'subjects_matched': subject_match_count, 'errors': errors}
	
		logger.info("Processed {} triples, found {} matches ({} errors)"
					.format(res['processed'], res['matches'], len(res['errors'])))
	
		return res
	def write(self,g,units,filters):
		res = {}
		for magazine in units:
			articles = magazine.get_articles()
			
			for article in articles:
				article_id = str(article.get_id())
				if len(article_id)>0:
					concepts = article.get_consepts()
					if concepts != None:
						if len(concepts.get_ranked_consepts())>0:
							l = concepts.get_ranked_consepts()
						else:
							l = concepts.get_consepts()
						for concept in l:
							target_uri = concept.getType()
							filter = filters.get_conf_set(target_uri)
							if not(filter.filter_using_stopwordlist(concept)) and not(filter.filter_using_frequency(concept)):
								links = concept.retrieve_link_uris()
								if links != None:
									uri_filter, key = filter.get_uri_filter()
									if uri_filter != None:
										logger.info("Filtering using key "+str(key)+" next step is to prioritize all uris of each consept that contain str ="+str(uri_filter))
									matching = None
									if uri_filter != None:
										matching = [s for s in links if uri_filter in s]
									if matching != None and len(matching)>0:
										logger.info("Writing matching to source "+str(matching)+" for article "+article_id)
										res = self.updateRDFFile(g, target_uri, matching, article_id)
									else:
										logger.info("Writing links to source "+str(links)+" for article "+article_id)
										res = self.updateRDFFile(g, target_uri, links, article_id)
		return res
