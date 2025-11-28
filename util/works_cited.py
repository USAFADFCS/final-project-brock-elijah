



class Works_Cited:
    def __init__(self):
        self.works = []
        
        
    def cite(self, type, format, citation):
        self.works.append(
            {
                "format" : format,
                "type" : type,
                "txt" : citation
            }
        )
        
        
    def purge(self):
        contents = ""
        for source in self.works:
            contents += source["txt"] + "\n\n"
        return contents