'''
Created on 26.2.2016

@author: Claire

Install http://www.crummy.com/software/BeautifulSoup/bs4/doc/
'''
from bs4 import BeautifulSoup

class htmlParser:
    def __init__(self, html_doc):
        self.soup = BeautifulSoup(html_doc, 'html.parser', from_encoding="UTF-8")
        
    def get_text(self):
        return str(self.soup.get_text(separator=u' '))
    def get_prettyfied_text(self):
        return self.soup.prettify(encoding='utf-8')
    def file_contains_html(self):
        return bool(soup.find())