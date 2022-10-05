import xml.etree.ElementTree as ET

from xp_loader import load_xp_string
from generator.prefab import Prefab

def load_config(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()

    if root.tag != "config":
        raise Error("Incorrect File Type")

    features = root.find("features")
    prefabs = []
    weights = []
    for element in features:
        if element.tag == "prefab":
            definition_path = element.get("definition")
            tiledata_path = element.get("filepath")
            with open(tiledata_path, "rb") as f:
                tiledata = load_xp_string(f.read())
            definition = ET.parse(definition_path)
            prefab = Prefab(tiledata=tiledata, definition=definition)
            prefabs.append(prefab)
            weights.append(element.get("weight", default=1))
