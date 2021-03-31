import csv_writer as cw
import scraper_main as sm
import pickle


def checking_save_file(main_link):
    list_of_saved_links = cw.reading_file()

    #  Should get dispose of empty lists after reading a file
    #  TODO check whats going on here if it works and needed
    for link in range(len(list_of_saved_links)):
        if not list_of_saved_links[link]:
            list_of_saved_links.pop(link)

    #  If list of links from csv is empty should look for links online
    if len(list_of_saved_links) < 1:
        print("Starting online")
        link_for_next_day_matches = sm.get_link_for_matches_in_x_days(main_link)
        list_of_links_to_check = sm.list_of_links_to_check(link_for_next_day_matches)
        #  TODO instead of removing items from links list (that probably makes more problems)
        #  TODO should make a counter and saves by pickling
        cw.clearing_file()
        cw.saving_progress(list_of_links_to_check)
        #  TODO: Setting pickle to 0 as we start from 0
    else:
        print("Reading CSV")
        list_of_links_to_check = list_of_saved_links

    #  There was initiating main_function before
    return list_of_links_to_check


def main_function(list_of_links, save_state_counter=0):
    """Takes links to tomorrow matches, then checks one by one,
    saving in temporary scraper_object all details about a pair,
    then decides if save current pair to DB"""
    if save_state_counter != 0:
        list_of_links = list_of_links[save_state_counter:]
    #  TODO: After cropping should save new list and count from 0
    if len(list_of_links) > 0 < save_state_counter:
        for link_to_pair in list_of_links:
            #  print(f"Links to check: {len(list_of_links)}")
            status = sm.doing_one_link(link_to_pair)
            if status == 1:
                save_state_counter += 1
                saving_state(save_state_counter)
            else:
                #  TODO:  something like reinitialization
                print("Something went wrong, status of link == 0")
    else:
        print("DONE LIST OF LINKS, check database please")


def saving_state(saved_progress_pickle):
    try:
        with open('save_state.pkl', 'w') as file:
            pickle.dump(saved_progress_pickle, file)
    except:
        print("Problem with saving progress (saving_state)")


def loading_state():
    try:
        with open('save_state.pkl') as file:
            saved_progress_pickle = pickle.load(file)
        return saved_progress_pickle
    except:
        print("Problem with loading saved_state returning 0")
        return 0
