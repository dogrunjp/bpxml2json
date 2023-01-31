class DefaultDictVal:
    def get_value(self, elem, path):
        try:
            val = elem.xpath(path)[0].text
        except:
            val = ""
        return val

    def get_vals(self, elem, path):
        try:
            obj = elem.findall(path)
            xid = [x.text for x in obj]
        except:
            xid = ""
        return xid

    def get_dict(self, elem, path):
        try:
            dct = elem.xpath(path)[0]
        except:
            dct = {}
        return dct

    def get_attr(self, elem, name):
        try:
            attr = elem.attrib[name]
        except:
            attr = ""
        return attr

    def get_xattr(self, elem, path):
        try:
            attr = elem.xpath(path)[0]
        except:
            attr = ""
        return attr
    
    def get_xattrs(self, elem, path):
        try:
            attrs = elem.xpath(path)
        except:
            attrs = []
        return attrs

    def get_chld(self, elem, path):
        try:
            tag = elem.xpath(path)[0][0].tag
        except:
            tag = ""
        return tag

    def get_text(self, elem):
        try:
            txt = elem.text
        except:
            txt = ""
        return txt
