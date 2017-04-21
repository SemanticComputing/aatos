class TextSlice:
    def __init__(self, text="", page=0):
        self.__text = text
        self.__annotated_version = ""
        self.__page = page
        self.__xml_version = ""
        self.format_text()

    def get_text(self):
        return self.__text

    def set_xml_text(self, xml):
        
        self.__xml_version = xml
    def get_xml_text(self):
        return self.__xml_version

    def get_page(self):
        return self.__page

    def set_text(self, value):
        self.__text = value

    def set_annotated_text(self, value):
        self.__annotated_version = value

    def get_annotated_text(self):
        return self.__annotated_version
    
    def get_annotated_text_pretty_print(self):
        text = self.__annotated_version.replace("</annotated>", "").replace("<annotated>", "")
        return text

    def set_page(self, value):
        self.__page = value


    def del_text(self):
        del self.__text


    def del_page(self):
        del self.__page

    
    def __str__(self):
        s= "Page : "+str(self.__page)+" Text : "+self.__text[0:50]+"..."+self.__text[50:0]
        return s

    def __sizeof__(self):
        return len(self.__text)
    
    def __repr__(self):
        s=""
        if len(self.__text)>49:
            s= ""+str(self.__text[0:50])+"..."+str(self.__text[50:0])+" (p. "+str(self.__page)+")"
        return s
    
    def __eq__(self, other):
        if self.__text == other.get_text():
            if self.__page == other.get_page():
                return True
        return False        
    
    def __cmp__(self, other):
        if hasattr(other, 'page'):
            return self.__page.__cmp__(other.get_page())
    
    def format_text(self):
        formatted =""
        try:
            s=self.__text.format()
            s=s.strip()
            formatted=s.replace("@", '').replace("*", '').replace("<",'').replace(">", '').replace("#", '')
        except Exception as e:
            formatted=self.__text
            self.__text = formatted
            print("Unexpected exception while formatting "+str(self)+". Exception "+e)
        self.__text = formatted
