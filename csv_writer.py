import csv

"""Keeps track of list of links for matches and saves progress,
so scraping can be stopped any time and after launch again, returns to point where
it stopped, so-called saving"""


def deleting_nesting(temp_list):
    """When reading a csv by reading_file() there is problem
    that new list is nested, this function reverts this process"""
    list_of_links = []
    for element in temp_list:
        if type(element) is list:
            for item in element:
                list_of_links.append(item)
        else:
            list_of_links.append(element)
    return list_of_links


def reading_file():
    """Opens progress_saving file and returns links to matches as list"""
    with open("progress_saving.csv", "r", newline="") as file:
        reader = csv.reader(file, delimiter=',', quoting=csv.QUOTE_NONE)
        temp_list = list(reader)
    """Reading file creates nested list, function below creates new
    list that's not nested anymore"""
    list_of_links = deleting_nesting(temp_list)
    return list_of_links


def clearing_file():
    """Just clearing csv file, needed for check at starting of script"""
    with open("progress_saving.csv", "w") as file:
        csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE)


def saving_progress(list_of_links):
    """Saving list of links to check to csv file, each link on separate row"""
    for element in list_of_links:
        with open("progress_saving.csv", "a", newline="") as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE)
            writer.writerow([element])
