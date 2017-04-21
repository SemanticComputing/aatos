from SPARQLWrapper import SPARQLWrapper, JSON

class sparqlQuery:
    def __init__(self, file_name_pattern="", path="", full_path=""):
        self.__file_name_pattern = file_name_pattern
        self.__path = path
    
    def query_kata(self):
        sparql = SPARQLWrapper("http://ldf.fi/warsa/sparql")
        sparql.setQuery("""
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        PREFIX art: <http://ldf.fi/schema/warsa/articles/>
                        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                        PREFIX dc: <http://purl.org/dc/elements/1.1/>
                        PREFIX dct: <http://purl.org/dc/terms/>
                        SELECT ?sub ?author ?page ?vol ?issue ?title ?event WHERE { GRAPH <http://ldf.fi/warsa/articles> {
                          ?sub rdf:type art:Article .
                          OPTIONAL {
                             ?sub art:author ?kirj .
                              ?kirj skos:prefLabel ?author .
                            } OPTIONAL {                         
                          ?sub art:page ?page .
                          ?sub art:volume/dct:issued ?vol .
                          ?sub dc:title ?title .
                          ?sub art:issue/dct:issued ?issue .
                            } OPTIONAL {
                          ?sub art:event/skos:prefLabel ?event .
                          }
                        }} order by ?vol ?issue ?page
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        
        return results
    
    