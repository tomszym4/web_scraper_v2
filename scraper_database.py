import datetime
import scraper_object as so

minimal_amount_of_matches = 5
minimal_effectivity = 8/10


def check_if_gonna_save_in_database(effectiveness):
    """Checking if current pair have requested effectivity, returns bool value"""
    effectiveness_check = effectiveness.rsplit("/")
    if int(effectiveness_check[1]) >= minimal_amount_of_matches:
        if int(effectiveness_check[0]) / int(effectiveness_check[1]) > minimal_effectivity:
            return True
        else:
            return False
    else:
        return False


def writing_in_teams_table(my_db, teams, links):
    """Creates new row in DB.teams and return teams_id list"""
    my_db.reconnect()
    cursor = my_db.cursor()

    teams_id = []
    n = 0
    for team in teams:
        x = check_if_team_is_already_in_db(cursor, team)
        if not x:
            my_result = one_team_at_a_time(my_db, cursor, teams[n], links[n])
            teams_id.append(my_result)
        else:
            teams_id.append(x)
        n += 1
    return teams_id


def check_if_team_is_already_in_db(cursor, name):
    """Checks if team is already in DB, if yes, then
    returns id of team, else return False value"""
    sql = "SELECT * FROM teams"
    cursor.execute(sql)
    my_result = cursor.fetchall()
    for item in my_result:
        for n in item:
            if n == name:
                return item[0]
    # TODO fails if table empty in pairs and history could be same
    #  Or maybe its ok
    return False


def one_team_at_a_time(my_db, cursor, name, url):
    sql = """INSERT INTO teams (team_name, team_url) VALUES (%s,%s)"""
    cursor.execute(sql, (name, url))
    my_db.commit()
    team_id = cursor.lastrowid
    return team_id


def check_if_pair_is_already_in_db(my_db, names):
    """Checks if current pair is in DB, if it is,
    then returns id of pair, and adds last match score if it's not
    in Db already"""
    sql = "SELECT * FROM pairs"
    cursor = my_db.cursor()
    cursor.execute(sql)
    my_result = cursor.fetchall()
    for record in my_result:
        checker = 0
        for column in record:
            for name in names:
                if name == column:
                    checker += 1
        if checker == 2:
            id_of_pair = record[0]
            return id_of_pair
    return 0


def writing_in_pairs_table(my_db, temp_pair):
    """Creates new row in DB.pairs table and returns pair_id as int"""
    names = [temp_pair.team_1_name, temp_pair.team_2_name]
    pair_id = check_if_pair_is_already_in_db(my_db, names)
    cursor = my_db.cursor()
    temp_date = datetime.datetime.now()
    now_date = datetime.datetime(temp_date.year, temp_date.month, temp_date.day,
                                 temp_date.hour, temp_date.minute, temp_date.second)
    if pair_id == 0:

        #  TODO link and date_of_match should be updated as new record in upcoming_matches
        """It should work if most recent element is added, if new match will appear in
        a few days then this method should create new entry in upcoming_matches table
        eventually if match is postponed it should add new entry of new date anyway
        so result_checker should only removes postponed matches"""
        #  TODO: pairs_temp temporarily
        sql = "INSERT INTO pairs (date, effectivity, league, country, " \
              "team_1_id, team_1_name, team_2_id, team_2_name, url, " \
              "ht_effectivity, ft_effectivity, last_updated)" \
              "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, (temp_pair.date_of_match, temp_pair.effectivity,
                             temp_pair.league, temp_pair.country, temp_pair.team_1_id,
                             temp_pair.team_1_name, temp_pair.team_2_id, temp_pair.team_2_name,
                             temp_pair.url, temp_pair.ht_effectivity,
                             temp_pair.ft_effectivity, now_date))
        my_db.commit()
        pair_id = check_if_pair_is_already_in_db(my_db, names)
        print("creating new one")
    else:
        sql = "UPDATE pairs SET date = %s, effectivity = %s, url = %s, ht_effectivity = %s," \
              "ft_effectivity = %s, last_updated = %s  WHERE pair_id = %s"
        cursor.execute(sql, (temp_pair.date_of_match, temp_pair.effectivity,
                             temp_pair.url, temp_pair.ht_effectivity, temp_pair.ft_effectivity,
                             now_date, pair_id))
        my_db.commit()
        print(f"Updating pair number: {pair_id}")
    return pair_id


def writing_in_upcoming_matches(my_db, temp_pair):
    """Creates new row in DB.upcoming_matches table"""
    cursor = my_db.cursor()
    if not checking_if_upcoming_match_is_on_db(my_db, temp_pair):
        sql = "INSERT INTO upcoming_matches (pair_id, date_of_match, postponed," \
              "url, url_active, effectivity)" \
              "VALUES (%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, (temp_pair.pair_id, temp_pair.date_of_match,
                             0, temp_pair.url, temp_pair.url_active, temp_pair.effectivity))
        """temp_pair.postponed"""
        my_db.commit()
    else:
        print("This match is already in DB")


def checking_if_upcoming_match_is_on_db(my_db, temp_pair):
    list_of_upcoming_matches = []
    sql = "SELECT * FROM upcoming_matches"
    cursor = my_db.cursor()
    cursor.execute(sql)
    my_result = cursor.fetchall()
    for item in my_result:
        n = 0
        upcoming_match = so.UpcomingMatches()
        upcoming_match.id = item[n]
        upcoming_match.pair_id = item[n+1]
        upcoming_match.date_of_match = item[n+2]
        upcoming_match.postponed = item[n+3]
        upcoming_match.url = item[n+4]
        upcoming_match.url_active = item[n+5]
        list_of_upcoming_matches.append(upcoming_match)
    for match in list_of_upcoming_matches:
        if temp_pair.pair_id == match.pair_id and temp_pair.date_of_match == match.date_of_match:
            return True
    return False


def adding_past_results(my_db, list_of_matches, master_pair):
    """try:"""
    """Adding all historic matches since final date (usually 01.01.2015)
    as a separate entry in db.results table"""
    cursor = my_db.cursor()
    my_result = get_results(my_db)

    for i in range(len(list_of_matches)):
        temp_pair = list_of_matches[i]
        temp_pair.pair_id = master_pair.pair_id
        #  Making string out of list to pass to DB
        minutes_as_string = ','.join(temp_pair.match_goals_minutes)
        result_in_db = check_if_result_is_already_in_db(my_result, temp_pair.pair_id, temp_pair.date_of_match)
        print(temp_pair.result_ht)
        print(temp_pair.url)
        if not result_in_db:
            #  TODO: results_temp temporarily was made in db
            sql = "INSERT INTO results (result, result_ht, result_ft, " \
                  "goals, date, postponed, url, url_active, pair_id)" \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql, (temp_pair.result, temp_pair.result_ht, temp_pair.result_ft,
                                 minutes_as_string, temp_pair.date_of_match,
                                 temp_pair.match_postponed, temp_pair.url,
                                 temp_pair.url_active, temp_pair.pair_id))
            my_db.commit()
    """except:
        print("Failing while adding past results")"""


def get_results(my_db):
    sql = "SELECT * FROM results"
    cursor = my_db.cursor()
    cursor.execute(sql)
    my_result = cursor.fetchall()
    return my_result


def check_if_result_is_already_in_db(my_result, master_id, date_of_match):
    """Checks if current result is in DB, if it is,
    then return True"""

    for record in my_result:
        checker = 0
        for column in record:
            if master_id == column:
                checker += 1
            if date_of_match == column:
                checker += 1
        if checker == 2:
            return True
    return False
