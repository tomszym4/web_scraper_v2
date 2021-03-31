import datetime


class PairOfTeams:
    def __init__(self):
        self.country = ""
        self.league = ""
        self.home_team = ""
        self.home_team_id = 0
        self.home_team_link = ""
        self.away_team = ""
        self.away_team_id = 0
        self.away_team_link = ""
        self.date_of_match = datetime.datetime.now()
        self.goals = []
        self.link = ""
        self.effectiveness = 0
        self.ht_effectiveness = 0
        self.ft_effectiveness = 0
        self.pair_id = 0
        #  These are for result checking
        self.match_goals_minutes = ""
        self.url_active = 1
        self.result = ""
        self.result_ht = ""
        self.result_ft = ""
        self.match_postponed = 0


def print_all_info(scraper_object):
    stats = "----------------------------------------------------------------\n" \
            "{} - {} at {}\n" \
            "ID {} - {} vs. ID {} - {}\n" \
            "Effectiveness: {}\n" \
            "Link: {}"
    print(stats.format(scraper_object.country, scraper_object.league, scraper_object.date_of_match,
                       scraper_object.home_team_id, scraper_object.home_team,
                       scraper_object.away_team_id, scraper_object.away_team,
                       scraper_object.effectiveness, scraper_object.link))
