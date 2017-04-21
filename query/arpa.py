"""
A module for linking resources to an RDF graph with an [ARPA](https://github.com/jiemakel/arpa) service

## Requirements
Python 3, [RDFLib](http://rdflib.readthedocs.org/en/latest/) and [Requests](http://docs.python-requests.org/en/latest/)

## Usage

The module can be invoked as a script from the command line or by calling `arpa.arpafy` in your Python code.

    usage: arpa.py [-h] [--fi INPUT_FORMAT] [--fo OUTPUT_FORMAT]
                [--rdf_class CLASS] [--prop PROPERTY]
                [--ignore [TERM [TERM ...]]] [--min_ngram N]
                [--no_duplicates [TYPE [TYPE ...]]]
                input output target_property arpa

    Link resources to an RDF graph with ARPA.

    positional arguments:
    input                 Input rdf file
    output                Output file
    target_property       Target property for the matches
    arpa                  ARPA service URL

    optional arguments:
    -h, --help            show this help message and exit
    --fi INPUT_FORMAT     Input file format (rdflib parser). Will be guessed if
                          omitted.
    --fo OUTPUT_FORMAT    Output file format (rdflib serializer). Default is
                          turtle.
    --rdf_class CLASS     Process only subjects of the given type (goes through
                          all subjects by default).
    --prop PROPERTY       Property that's value is to be used in matching.
                          Default is skos:prefLabel.
    --ignore [TERM [TERM ...]]
                        Terms that should be ignored even if matched
    --min_ngram N         The minimum ngram length that is considered a match.
                          Default is 1.
    --no_duplicates [TYPE [TYPE ...]]
                        Remove duplicate matches based on the 'label' returned
                        by the ARPA service. Here 'duplicate' means a subject
                        with the same label as another subject in the same
                        result set. A list of types can be given with this
                        argument. If given, prioritize matches based on it -
                        the first given type will get the highest priority and
                        so on. Note that the response from the service has to
                        include a 'type' variable for this to work.

The arguments can also be read from a file using "@" (example arg file [arpa.args](https://github.com/SemanticComputing/python-arpa-linker/blob/master/arpa.args)):

`$ python3 arpa.py @arpa.args`

## Examples

See [menehtyneet.py](https://github.com/SemanticComputing/python-arpa-linker/blob/master/menehtyneet.py)
for a code example and [arpa.args](https://github.com/SemanticComputing/python-arpa-linker/blob/master/arpa.args)
for an example arg file.
"""

LABEL_PROP = 'label'
"""The name of the property containing the label of the match in the ARPA results."""

TYPE_PROP = 'type'
"""
The name of the property containing the type of the match in the ARPA results->properties.
Only needed for prioritized duplicate removal.
"""

from query.ArpaQueryExecuter import ArpaQueryExecuter
import json
import logging


                    #logging setup
logger = logging.getLogger('Arpa')
hdlr = logging.FileHandler('/tmp/myapp.log')
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)

class Arpa:
    """Class representing the ARPA service"""

    def __init__(self, remove_duplicates=False, min_ngram_length=1, ignore=None, url="", ordered=False):
        """
        Initialize the Arpa service object.

        `url` is the ARPA service url.

        If `remove_duplicates` is `True`, choose only one subject out of all the
        matched subjects that have the same label (arbitrarily).
        If, instead, the value is a list or a tuple, assume that it represents
        a list of class names and prefer those classes when choosing
        the subject. The ARPA results must include a property (`TYPE_PROP`)
        that has the class of the match as the value.

        `min_ngram_length` is the minimum ngram match length that will be included when
        returning the query results.

        `ignore` is a list of matches that should be removed from the results (case insensitive).
        """
        
        self._url=url
        self._order = ordered

        self._ignore = [s.lower() for s in ignore or []]
        self._min_ngram_length = min_ngram_length

        if type(remove_duplicates) == bool:
            self._no_duplicates = remove_duplicates
        else:
            self._no_duplicates = tuple("<{}>".format(x) for x in remove_duplicates)
            
    def _get_url(self):
        return self._url

    def _remove_duplicates(self, entries):
        """
        Remove duplicates from the entries.

        A 'duplicate' is an entry with the same `LABEL_PROP` property value.
        If `self._no_duplicates == True`, choose the subject to keep any which way.
        If `self._no_duplicates` is a tuple (or a list), choose the kept subject
        by comparing its type to the types contained in the tuple. The lower the
        index of the type in the tuple, the higher the priority.

        `entries` is the ARPA service results as a JSON object.
        """

        res = entries
        if self._no_duplicates == True:
            labels = set()
            add = labels.add
            res = [x for x in res if not (x[LABEL_PROP] in labels 
                # If the label is not in the labels set, add it to the set.
                # This works because set.add() returns None.
                or add(x[LABEL_PROP]))]

        elif self._no_duplicates:
            # self._no_duplicates is a tuple - prioritize types defined in it
            items = {}
            for x in res:
                x_label = x[LABEL_PROP].lower()
                # Get the types of the latest most preferrable entry that 
                # had the same label as this one
                prev_match_types = items.get(x_label, {}).get('properties', {}).get(TYPE_PROP, [])
                # Get matches from the preferred types for the previously selected entry
                prev_pref = set(prev_match_types).intersection(set(self._no_duplicates))
                try:
                    # Find the priority of the previously selected entry
                    prev_idx = min([self._no_duplicates.index(t) for t in prev_pref])
                except ValueError:
                    # No previous entry or previous entry doesn't have a preferred type
                    prev_idx = float('inf')
                # Get matches in the preferred types for this entry
                pref = set(x['properties'][TYPE_PROP]).intersection(self._no_duplicates)
                try:
                    idx = min([self._no_duplicates.index(t) for t in pref])
                except ValueError:
                    # This one is not of a preferred type
                    idx = float('inf')

                if (not prev_match_types) or idx < prev_idx:
                    # There is no previous entry with this label or
                    # the current match has a higher priority preferred type
                    items[x_label] = x

            res = [x for x in res if x in items.values()]

        return res

    def _filter(self, response):
        """
        Filter matches based on `self._ignore` and remove matches that are
        for ngrams with length less than `self.min_ngram_length`.

        Return the response with the ignored matches removed.

        `response` is the parsed ARPA service response.
        """

        res = response['results']

        if self._order:
            print("ORDER")
            print(res)
            res = self._reverse_order(res)
        else:
            print("DISORDER")

        # Filter ignored results
        if self._ignore:
            res = [x for x in res if x[LABEL_PROP] != None and x[LABEL_PROP].lower() not in self._ignore]

        # Filter by minimum ngram length
        if self._min_ngram_length > 1:
            res = [x for x in res if len(x['properties']['ngram'][0].split()) >= self._min_ngram_length]

        # Remove duplicates if requested
        res = self._remove_duplicates(res)

        response['results'] = res
        return response

    def _reverse_order(self, res):
        r = [x for x in reversed(res)]
        return r

    def _sanitize(self, text):
        # Remove quotation marks and brackets - ARPA can return an error if they're present
        return text.replace('"', '').replace("(", "").replace(")", "").replace("/", "\/")
    
    def _query(self, querystring):
        url = self._get_url()
        query = ArpaQueryExecuter('',url, querystring)
        result = query.getArpa()
        
        if 'data' in result:
            res = self._filter(json.loads(result['data']))
            return res
        else:
            return result
