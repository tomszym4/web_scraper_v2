import configparser
import mysql.connector
import datetime
import re
import scraper_object as so
import scraper_database as sd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from time import sleep


driver_path = r"C:\Users\Criminalman\PycharmProjects\webscraper\chromedriver.exe"
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options, executable_path=driver_path)


config = configparser.ConfigParser()
config.read('config.ini')

host = config['database']['host']
user = config['database']['user']
password = config['database']['password']
database = config['database']['database']


#  TODO days=13 instead of 14
def get_link_for_matches_in_x_days(main_link, days=13):
    """Changes main_link of betexplorer.com to link for matches depended on days argument
    default is 14 days from now, values below 0 will check in past"""
    try:
        now = datetime.datetime.now()
        date_to_check = now + datetime.timedelta(days)
        #  Here script could make it go through days until 14 day from now
        print(f"Checking matches at: {date_to_check.date()}")
        year = date_to_check.strftime("%Y")
        month = date_to_check.strftime("%m")
        day = date_to_check.strftime("%d")
        link_for_checking = f"{main_link}?year={year}&month={month}&day={day}"
        return link_for_checking
    except:
        print(f"There was a problem with creating link, returning input link {main_link}")
        return main_link


def list_of_links_to_check(main_link):
    """Finds all matches that will be played tomorrow and returns a list of links to them"""
    #  TODO: try else-here, when didn't finds links, then restart
    list_of_links = []
    driver.get(main_link)
    sleep(1)
    temp_list = driver.find_elements_by_class_name("table-main__tt")
    for block in temp_list:
        elements = block.find_elements_by_tag_name("a")
        for el in elements:
            if "soccer" in el.get_attribute("href"):
                list_of_links.append(el.get_attribute("href"))
    return list_of_links


def get_date_of_match(wd):
    """finds and returns date of a match if WebElement provided
    returns date in datetime format"""
    sleep(0.2)
    try:
        temp_date = wd.find_element_by_id("match-date").text
        date_list = clean_date_element(temp_date)
        date_of_match = datetime.datetime(int(date_list[2]), int(date_list[1]),
                                          int(date_list[0]), int(date_list[3]),
                                          int(date_list[4]))
        return date_of_match
    except:
        print("N/A Date")
        failed_date = datetime.datetime(2000, 1, 1, 1, 0)
        return failed_date


def clean_date_element(temp_string):
    """Throws away any signs and letters from provided string"""
    try:
        element = ""
        for c in temp_string:
            if c.isnumeric():
                element += c
            elif c == "." or c == "-" or c == ":":
                element += "."
        date_list = element.split(".")
        return date_list
    except:
        return "Something went wrong with processing date"


def click_two_times(wd):
    """Clicks on two elements on page to get access to historic matches"""
    sleep(1.5)
    try:
        wd.find_element_by_xpath('//*[@id="mutual_div"]/a').click()
    except NoSuchElementException:
        print("There's problem with getting historical matches of current pair")
    sleep(1.5)
    try:
        wd.find_element_by_id("mutual-link-moreless").click()
    except NoSuchElementException:
        #  print("There's no second link")
        pass


def get_league_name(wd):
    """Finds a league name if WebDriver element provided
    and returns it in string format"""
    try:
        league = wd.find_element_by_xpath('/html/body/div[4]/div[5]/div/div/div[1]/section/header/h1/a').text
        #  There used to be cleaning to letters but there can be years of league (and endings like league 1)
        return league
    except:
        return "N/A League"


def get_leagues_country(wd):
    """Returns string with country name for given league if WebElement provided"""
    try:
        country = wd.find_element_by_tag_name("img").get_attribute("alt")
        return country
    except:
        return "N/A Country"


def get_names_of_teams(wd):
    """Finds teams names and links to their site if WebDriver element
    provided and returns a string lists - [home_team, away_team]"""
    name_of_teams = []
    try:
        elements = wd.find_elements_by_class_name("list-details__item__title")
        for i in elements:
            temp_name = i.find_element_by_tag_name("a").text
            name_of_teams.append(temp_name)
        return name_of_teams
    except:
        return ["N/A Home Team", "N/A Away Team"]


def get_links_to_teams(wd):
    try:
        links_to_teams = []
        content_blocks = wd.find_elements_by_class_name("list-details__item__team")
        for block in content_blocks:
            element = block.find_element_by_tag_name("a").get_attribute("href")
            if "/soccer/":
                links_to_teams.append(element)
        return links_to_teams
    except:
        return ["N/A link to Home team", "N/A link to Away team"]


def get_links_to_historic_matches(wd):
    """After click_two_times we can access and save list of links"""
    list_of_links = []
    content_blocks = wd.find_elements_by_id("js-mutual-table")
    for block in content_blocks:
        elements = block.find_elements_by_tag_name("a")
        for el in elements:
            one_link = el.get_attribute("href")
            if one_link.count("/") > 6:
                list_of_links.append(one_link)
    return list_of_links


def clean_minutes_of_goals(temp_string):
    """Returns minutes of match with a '+' if it was in additional time"""
    minute = ""
    for c in temp_string:
        if c.isnumeric():
            minute += c
        elif c == "+":
            minute += c
    return minute


def get_result(wd):
    """Finds and returns result of a match if WebDriver element provided
    Returns result in string format"""
    try:
        result = wd.find_element_by_id("js-score").text
        return result
    except:
        return "N/A Result"


def clean_goals(result):
    list_goals = []
    goals = ""
    for c in result:
        if c.isnumeric():
            goals += c
        elif c == ":" or c == ",":
            goals += c
    return goals


def get_result_ht(wd):
    """Finds and returns result of a first half if WebDriver element provided
    Returns result in string format"""
    try:
        result = wd.find_element_by_id("js-partial").text
        ht = clean_goals(result)
        ht = ht.split(",")
        return ht[0]
    except:
        return "N/A HT Result"


def get_result_ft(wd):
    """Finds and returns result of a second half if WebDriver element provided
    Returns result in string format"""
    try:
        result = wd.find_element_by_id("js-partial").text
        ft = clean_goals(result)
        ft = ft.split(",")
        return ft[1]
    except:
        return "N/A FT Result"


def check_if_postponed(wd):
    """Checks if match was not canceled or postponed"""
    try:
        result = wd.find_element_by_id("js-eventstage").text
        if result == "Postponed":
            print("Postponed")
            return 1
        else:
            return 0
    except:
        return 0


#  TODO saving additional info about goals like scorers or if it was a penalty
def get_minutes_of_goals(wd):
    """Returns minutes of scored goals,
    and check_if_late_goal() should be
    called after this function with goals[]
    as a parameter"""
    goals = []
    try:
        temp_goals = wd.find_elements_by_tag_name("td")
        for element in temp_goals:
            temp2 = element.get_attribute("style")
            if temp2 == "width: 4ex; text-align: right;":
                temp3 = clean_minutes_of_goals(element.text)
                if temp3.isnumeric():
                    goals.append(temp3)
                elif temp3.find("+") > 0:
                    goals.append(temp3)
        return goals
    except:
        return "N/A minutes of goals"


def check_if_late_goal(goals_minutes):
    """Takes list with minutes of goals and
    checks if goals in game was late (after 35' or 75')
    and should be called after get_minutes_of_goals
    returns bool value"""
    was_late = False
    was_ht_late = False
    was_ft_late = False
    for list_element in goals_minutes:
        try:
            if 30 <= int(list_element) <= 45:
                was_late = True
                was_ht_late = True
            elif 75 <= int(list_element) <= 90:
                was_late = True
                was_ft_late = True
        except ValueError:
            if re.search("45+", list_element):
                was_late = True
                was_ht_late = True
            elif re.search("90+", list_element):
                was_late = True
                was_ft_late = True
    late_list = [was_late, was_ht_late, was_ft_late]
    return late_list


def effectiveness_of_a_pair(list_of_historic_matches):
    """Checks the history of current pair and returns
    effectiveness in list of strings"""
    was_late_list = []
    was_ht_late_list = []
    was_ft_late_list = []
    late_matches = 0
    ht_late_matches = 0
    ft_late_matches = 0
    if len(list_of_historic_matches) >= 5:
        for match in list_of_historic_matches:
            all_late = check_if_late_goal(match.match_goals_minutes)
            was_late_list.append(all_late[0])
            was_ht_late_list.append(all_late[1])
            was_ft_late_list.append(all_late[2])
        total_matches = len(list_of_historic_matches)
        for j in range(len(was_late_list)):
            if was_late_list[j]:
                late_matches += 1
        effectiveness = f"{late_matches}/{total_matches}"
        for j in range(len(was_ht_late_list)):
            if was_ht_late_list[j]:
                ht_late_matches += 1
        ht_effectiveness = f"{ht_late_matches}/{late_matches}"
        for j in range(len(was_ft_late_list)):
            if was_ft_late_list[j]:
                ft_late_matches += 1
        ft_effectiveness = f"{ft_late_matches}/{late_matches}"
    else:
        return ["0/0", "0/0", "0/0"]
    return [effectiveness, ht_effectiveness, ft_effectiveness]


def creating_history_of_pair(wd):
    """For each historic match that is later than final date we're
    creating new PairObject and save it to list to later use this list
    while adding history of results"""
    final_date = datetime.datetime(2015, 1, 1)
    list_of_links = get_links_to_historic_matches(wd)
    list_of_historic_matches = []
    if len(list_of_links) > 5:
        for i in range(len(list_of_links)):
            sleep(1)
            wd.get(list_of_links[i])
            temp_pair = so.PairOfTeams()
            temp_pair.result = get_result(wd)
            temp_pair.result_ht = get_result_ht(wd)
            temp_pair.result_ft = get_result_ft(wd)
            temp_pair.match_goals_minutes = get_minutes_of_goals(wd)
            sleep(0.5)
            temp_pair.date_of_match = get_date_of_match(wd)
            temp_pair.league = get_league_name(wd)
            temp_pair.match_postponed = check_if_postponed(wd)
            temp_pair.link = list_of_links[i]
            temp_pair.url_active = 1
            list_of_historic_matches.append(temp_pair)
            if temp_pair.date_of_match < final_date:
                list_of_historic_matches.pop(i)
                break
    return list_of_historic_matches


def doing_one_link(link_to_pair):
    """try:"""
    my_db = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    temp_pair = so.PairOfTeams()
    temp_pair.link = link_to_pair
    driver.get(temp_pair.link)
    temp_pair.date_of_match = get_date_of_match(driver)
    click_two_times(driver)
    temp_pair.league = get_league_name(driver)
    temp_pair.country = get_leagues_country(driver)
    names_of_teams = get_names_of_teams(driver)
    temp_pair.home_team = names_of_teams[0]
    temp_pair.away_team = names_of_teams[1]
    links_to_teams = get_links_to_teams(driver)
    temp_pair.home_team_link = links_to_teams[0]
    temp_pair.away_team_link = links_to_teams[1]
    list_of_historic_matches = creating_history_of_pair(driver)
    all_effectiveness = effectiveness_of_a_pair(list_of_historic_matches)
    temp_pair.effectiveness = all_effectiveness[0]
    temp_pair.ht_effectiveness = all_effectiveness[1]
    temp_pair.ft_effectiveness = all_effectiveness[2]
    """print(temp_pair.effectiveness)
    print(temp_pair.ht_effectiveness)
    print(temp_pair.ft_effectiveness)"""
    #  Here can be printing effectiveness eventually
    #  TODO: giving minimal effectivity and number of matches to this method
    if sd.check_if_gonna_save_in_database(temp_pair.effectiveness):
        teams_id = sd.writing_in_teams_table(my_db, names_of_teams, links_to_teams)
        temp_pair.home_team_id = teams_id[0]
        temp_pair.away_team_id = teams_id[1]
        temp_pair.pair_id = sd.writing_in_pairs_table(my_db, temp_pair)
        sd.adding_past_results(my_db, list_of_historic_matches, temp_pair)
    sleep(1)
    return 1
    """except:
        return 0"""


def closing_chrome():
    driver.close()
    driver.quit()
