#  import scraper_main as sm
#  import scraper_object as so
#  import scraper_database as sd
import main_logic as ml
import configparser
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import mysql.connector
import datetime


#  Starts here, should decide what to do now
#  Firstly, should check what's the time and day
#  Should check if there's something in saving file or to start by getting list of links from site


"""Checking if config.ini exist"""
if not os.path.isfile('config.ini'):
    print("Config file not found")
    exit(1)
config = configparser.ConfigParser()
config.read('config.ini')

"""main_link for betexplorer.com/next/soccer is settable in config.ini"""
main_link = config['source']['main_link']


def where_to_start():
    """Checking if there are some links in csv file
    and reacts accordingly"""
    day_of_checking = datetime.datetime.now()
    print(f"Starting at: {day_of_checking}")
    saved_progress_pickle = ml.loading_state()
    temp_list_of_links = ml.checking_save_file(main_link)
    #  TODO: there should be pickle loading if needed
    list_of_links = ml.main_function(temp_list_of_links, saved_progress_pickle)



    ml.main_function(list_of_links, saved_progress_pickle)



where_to_start()

end_of_day = datetime.datetime.now()
print(f"DONE ALL DAY {end_of_day}")
#  driver.quit()
