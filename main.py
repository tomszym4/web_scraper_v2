import main_logic as ml
import configparser
import os
import datetime
import scraper_main as sm
import result_sender as rs
import pytz


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
    uct = pytz.utc
    print(f"Starting at: {day_of_checking}")
    temp_list_of_links = ml.checking_save_file(main_link)
    saved_progress_pickle = ml.loading_state()

    ml.main_function(temp_list_of_links, saved_progress_pickle)

# It's needed
"""import scraper_database as sd
import scraper_object as so
import mysql.connector

def checking_db():
    temp_pair = so.PairOfTeams()
    names_of_teams = ["teamA", "teamB"]
    links_to_teams = ["linkToTeamA", "linkToTeamB"]
    temp_pair.pair_id = 1254
    temp_pair.url = "linkToMatch"
    temp_pair.url_active = 1
    temp_pair.league = "leagueOfPair"
    temp_pair.country = "countryOfPair"
    temp_pair.effectivity = "6/326"
    temp_pair.ft_effectivity = "0/46"
    temp_pair.ht_effectivity = "24/1"
    temp_pair.team_1_id = 11
    temp_pair.team_2_id = 33
    temp_pair.team_1_name = "teamAName"
    temp_pair.team_2_name = "teamBName"
    temp_pair.postponed = 0
    temp_pair.date_of_match = datetime.datetime(day=29, month=3, year=1993)
    my_db = mysql.connector.connect(
        host="latebot.vps.webdock.io",
        user="remote_lattebot",
        password="juliettuniform1913",
        database="lattebot"
    )
    sd.writing_in_teams_table(my_db, names_of_teams, links_to_teams)
    sd.writing_in_pairs_table(my_db, temp_pair)"""

where_to_start()

#  checking_db()

end_of_day = datetime.datetime.now()
print(f"DONE ALL DAY {end_of_day}")
sm.closing_chrome()
rs.done_all_mail(end_of_day)
