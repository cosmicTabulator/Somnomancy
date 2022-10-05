import xml.etree.ElementTree as ET

from xp_loader import load_xp_string
from generator.prefab import Prefab

class Generator:
    def __init__(self, filepath):
        self.prefabs = []
        self.weights = []
        self.load_config(filepath)

    def load_config(self, filepath):
        tree = ET.parse(filepath)
        root = tree.getroot()

        if root.tag != "config":
            raise Error("Incorrect File Type")

        features = root.find("features")
        for element in features:
            if element.tag == "prefab":
                definition_path = element.get("definition")
                tiledata_path = element.get("filepath")
                with open(tiledata_path, "rb") as f:
                    tiledata = load_xp_string(f.read())
                definition = ET.parse(definition_path)
                prefab = Prefab(tiledata=tiledata, definition=definition)
                self.prefabs.append(prefab)
                self.weights.append(element.get("weight", default=1))
