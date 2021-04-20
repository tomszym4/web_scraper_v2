import os
import configparser

#  TODO: sending mail after completing checking
#  Sending files (excel and pickle file to verification

if not os.path.isfile('config.ini'):
    print("Config file not found")
    exit(1)
config = configparser.ConfigParser()
config.read('config.ini')

