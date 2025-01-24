
import json

class configParser():
    def __init__(self, configPath = None):
        if configPath == None:
            configPath = "goDBA.cnf"
        with open(configPath, mode="r") as json_file:
            self.config = json.load(json_file)
        self.servers = self.config["serverList"]
        self.backupDir =self.config["backupDir"]