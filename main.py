import main_logic as ml
import configparser
import os
import datetime
import scraper_main as sm
import result_sender as rs


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
    #  TODO! Send an e-mail while starting with number of links to check and approximation
    #   when the script will be done
    day_of_checking = datetime.datetime.now()
    print(f"Starting at: {day_of_checking}")
    temp_list_of_links = ml.checking_save_file(main_link)
    saved_progress_pickle = ml.loading_state()

    ml.main_function(temp_list_of_links, saved_progress_pickle)


where_to_start()

end_of_day = datetime.datetime.now()
print(f"DONE ALL DAY {end_of_day}")
sm.closing_chrome()
rs.done_all_mail(end_of_day)
