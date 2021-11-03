# system modules
import os
from os import path
from xml.etree import ElementTree as ET

# custom modules
from pythonconverter_pkg import DatabaseInterface as zdb

class XmlInterface(zdb.DatabaseInterface):
    def __init__(self):
        print("init XML Interface")
        super().__init__()
        self.root = []

    def openDatabase(self, uri):
        try:
            self.path = uri
            if path.exists(uri):
                uri=uri+"_"
            dir=path.dirname(self.path)
            if not path.exists(dir):
                os.makedirs(dir)
            return True
        except:
            return False

    def closeDatabase(self):
        print("Not implemented yet")

    def saveChanges(self):
        myfile = open(self.path, "wb")
        self.indent(self.root)
        data = ET.tostring(self.root)
        myfile.write(data)
        myfile.close()

    def readDatasetList(self):
        print("not implemented yet")

    def readDataset(self, datasetName):
        print("not implemented yet")

    def writeDataset(self, d={}):
        def _to_etree(d, root):
            if not d:
                pass
            elif isinstance(d, str):
                root.text = d
            elif isinstance(d,list):
                for ele in d:
                    _to_etree(ele, root)
            elif isinstance(d, dict):
                for k,v in d.items():
                    assert isinstance(k, str)
                    if k.startswith('#text'):
                        assert k == '#text' and isinstance(v, str)
                        root.text = v
                    elif k.startswith('@'):
                        assert isinstance(v, str)
                        root.set(k[1:], v)
                    elif k.startswith('#childs'):
                        assert isinstance(v, list)
                        _to_etree(v,root)
                    else:
                        _to_etree(v, ET.SubElement(root, k))
        assert isinstance(d, dict) and len(d) == 1
        tag, body = next(iter(d.items()))
        self.root = ET.Element(tag)
        _to_etree(body, self.root)

    def indent(self,elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
                for elem in elem:
                    self.indent(elem, level+1)
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
