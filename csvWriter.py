import csv, logging

logger = logging.getLogger('CSVWriter')
hdlr = logging.FileHandler('/tmp/annotator.log')
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)

class CSVWriter(object):
    
    def __init__(self):
    	pass
 
    def writeMagazineCSV(self, file, result):
        spamWriter = csv.writer(open(file, 'w', newline=''), dialect='excel')
        articles = result.get_articles()
        spamWriter.writerow(['Magazine','Article','Keyword', 'URI','Weight','Frequency'])
        spamWriter.writerow([str(result)])
        for article in articles:
            consepts = article.get_all_consepts()
            if len(consepts)>0:
                for consept in consepts:
                    i=0
                    links = consept.get_links()
                    if len(links)>0:
                        j=0
                        for link in links:
                            if i==0:
                                spamWriter.writerow(['',str(article),str(consept),str(link), str(consept.getWeight()), str(consept.get_frequency())])
                            elif j==0:
                                spamWriter.writerow(['','',str(consept),str(link), str(consept.getWeight()), str(consept.get_frequency())])
                            else:
                                spamWriter.writerow(['','','',str(link), str(consept.getWeight()), str(consept.get_frequency())])
                            j=j+1
                        i=i+1
                    else:
                        spamWriter.writerow(['',str(article),str(consept)])
            else:
                spamWriter.writerow(['',str(article)])
                
                
    def writeCandidatesCSV(self, file, result, top):
        spamWriter = csv.writer(open(file, 'w', newline=''), dialect='excel')
        spamWriter.writerow(['Magazine Article','Candidate', 'Weight'])
        for candidate in result:
            spamWriter.writerow([str(candidate)])
            count = 0
            logger.debug(candidate)
            candidate_list = result[candidate]
            for tuple in candidate_list:
            #for a,b in candidate_list:
                #if count < top:
                a, b = tuple
                if b >= top and count < 41:
                    logger.info(str(a) + ": " + str(b))
                    spamWriter.writerow(['',str(a),str(b)])
                    count = count + 1
            
                    
