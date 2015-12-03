import importlib
import os

#locals()["configuration"] = importlib.import_module("data_manager.configuration_{}".format(os.environ["COLLECSTER_CONFIG"]))
exec ("from data_manager.configuration_{} import *".format(os.environ["COLLECSTER_CONFIG"]))

#from .configuration_ndmusic import *
