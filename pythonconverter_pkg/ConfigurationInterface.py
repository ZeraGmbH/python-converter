#system modules
import json


class configurationInterface:
    def __init__(self):
        print("init configuration interface")
        self.mapping=dict()
    
    def readFile(self, file):
        fileHd = open(file)
        data = json.load(fileHd)
        for d in data['context1']:
            self.mapping[d['id']]=d
        print(self.mapping)

