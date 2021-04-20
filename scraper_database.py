import datetime

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


def writing_in_teams_table(my_db, teams, links):
    """Creates new row in DB.teams and return teams_id list"""
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
    sql = "SELECT * FROM pairs_temp"
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
    names = [temp_pair.home_team, temp_pair.away_team]
    pair_id = check_if_pair_is_already_in_db(my_db, names)
    cursor = my_db.cursor()
    temp_date = datetime.datetime.now()
    now_date = datetime.datetime(temp_date.year, temp_date.month, temp_date.day,
                                 temp_date.hour, temp_date.minute, temp_date.second)
    if pair_id == 0:
        #  TODO: pairs_temp temporarily
        sql = "INSERT INTO pairs_temp (date, effectivity, league, country, " \
              "team_1_id, team_1_name, team_2_id, team_2_name, url, " \
              "ht_effectivity, ft_effectivity, last_updated)" \
              "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, (temp_pair.date_of_match, temp_pair.effectiveness,
                             temp_pair.league, temp_pair.country, temp_pair.home_team_id,
                             temp_pair.home_team, temp_pair.away_team_id, temp_pair.away_team,
                             temp_pair.link, temp_pair.ht_effectiveness,
                             temp_pair.ft_effectiveness, now_date))
        my_db.commit()
        print("creating new one")
    else:
        sql = "UPDATE pairs_temp SET date = %s, effectivity = %s, url = %s, ht_effectivity = %s," \
              "ft_effectivity = %s, last_updated = %s  WHERE pair_id = %s"
        cursor.execute(sql, (temp_pair.date_of_match, temp_pair.effectiveness,
                             temp_pair.link, temp_pair.ht_effectiveness, temp_pair.ft_effectiveness,
                             now_date, pair_id))
        my_db.commit()
        print(f"Updating pair number: {pair_id}")
    return pair_id


#  TODO: results should be done for every historic match
def adding_past_results(my_db, list_of_matches, master_pair):
    """try:"""
    """Adding all historic matches since final date (usually 01.01.2015)
    as a separate entry in db.results table"""
    cursor = my_db.cursor()

    for i in range(len(list_of_matches)):
        temp_pair = list_of_matches[i]
        temp_pair.pair_id = master_pair.pair_id
        minutes_as_string = ','.join(temp_pair.match_goals_minutes)
        #  TODO: checking if already in db, then compare
        #  TODO: results_temp temporarily was made in db
        sql = "INSERT INTO results_temp (result, result_ht, result_ft, " \
              "goals, date, postponed, url, url_active, pair_id)" \
              "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, (temp_pair.result, temp_pair.result_ht, temp_pair.result_ft,
                             minutes_as_string, temp_pair.date_of_match,
                             temp_pair.match_postponed, temp_pair.link,
                             temp_pair.url_active, temp_pair.pair_id))
        my_db.commit()
    """except:
        print("Failing while adding past results")"""


def writing_in_results(my_db, temp_pair, update):
    """Adds a new row in results table for every pair of teams"""
    cursor = my_db.cursor()
    if update:
        print("Only updating in DB")
        # to co wyżej
    else:
        sql = "INSERT INTO results (pair_id, result, result_ht, result_ft, " \
              "goals, date, postponed, url, url_active)" \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (temp_pair.pair_id, temp_pair.result, temp_pair.result_ht,
                             temp_pair.result_ft, temp_pair.match_goals_minutes,
                             temp_pair.date_of_match, temp_pair.match_postponed,
                             temp_pair.link, temp_pair.url_active))
    my_db.commit()

