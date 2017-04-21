'''
Created on 26.2.2016

@author: Claire
'''
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup


class xmlParser:
    def __init__(self, input_file=None, xml_string=None):
        tree = None
        root = None
        
        if xml_string != None:
            root = ET.fromstring(xml_string)
        elif input_file != None:
            tree = ET.parse(input_file)
            root = tree.getroot()
        else:
            print("Unable to process xml. Input undefined!")
    
    """
    
    result:
    country {'name': 'Liechtenstein'}
    country {'name': 'Singapore'}
    country {'name': 'Panama'} 
    """       
    def browse_tags(self):
        for child in root:
            print(child.tag, child.attrib)
            
    """
    
    result:
    {'name': 'Austria', 'direction': 'E'}
    {'name': 'Switzerland', 'direction': 'W'}
    {'name': 'Malaysia', 'direction': 'N'}
    {'name': 'Costa Rica', 'direction': 'W'}
    {'name': 'Colombia', 'direction': 'E'}
    """
    def iterate_elements(self, element_name):
        for element in root.iter(element_name):
            print(element.attrib)
          
    def find_element_and_tag(self, tag_name, element_name):  
        for tag in root.findall(tag_name):
            e = tag.find(element_name)
            return e, tag
        
    def find_tag(self, tag_name):  
        return root.findall(tag_name)
            
