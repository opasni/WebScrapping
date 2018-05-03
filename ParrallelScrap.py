from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

import DataClean

import os
import time
import concurrent.futures
import pandas as pd
import numpy as np

def inititate_driver():
    # instantiate a chrome options object so you can set the size and headless preference
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument('log-level=3')

    if os.name == 'nt':
        chrome_driver = os.getcwd() + "\\chromedriver.exe"
    else:
        chrome_driver = os.getcwd() + "/chromedriver"

    driver = webdriver.Chrome(chrome_options=chrome_options,
                            executable_path=chrome_driver)
    
    return driver

def get_the_search_page(choose):
    driver.get("https://www.bayern-international.de/en/company-database/")

    # foldable_header = driver.find_element_by_class_name(name="foldable header")
    foldable_header = driver.find_element_by_css_selector(
        "div.foldable-container.keytech-search-form-extended.collapsed")
    foldable_header.click()

    select = Select(driver.find_element_by_name(
        name="tx_keytechrenew_keytech[state_province]"))
    select.select_by_value('091')

    time.sleep(5)

    select_none = driver.find_element_by_css_selector(
        "a.form-district-select-none")
    select_none.click()

    picked_districts = [list_of_districts[i] for i in choose]
    #Do not pick too many districts, otherwise it returns too many results (limited to 6000)
    for item in picked_districts:
        select_district = driver.find_element_by_id(item)
        select_district.click()


    search_button = driver.find_element_by_name(
        name="tx_keytechrenew_keytech[search]")
    search_button.click()

def load_result_page(i):
    url = "https://www.bayern-international.de/en/company-database/results/" + \
        str(i) + "/"
    driver.get(url)

    # Get the html of the data and only get the 'a' tags
    html_doc = driver.page_source
    soup = BeautifulSoup(html_doc, "lxml")
    a_tags = soup.find_all('a')
    return a_tags

def pars_result_page(link):
    if 'en/company-database/company-details/' in link.get('href'):
        # list_of_links.append()
        return link.get('href').split('/')[-2]


stand = 'https://www.bayern-international.de/en/company-database/company-details/'
list_of_div = ["//*[@id='content']/div/article/ul[2]/li[1]/div/dl[1]",
               "//*[@id='content']/div/article/ul[2]/li[1]/div/dl[2]", "//*[@id='content']/div/article/ul[2]/li[1]/dl[1]"]
list_of_districts = ["form_district_09171", "form_district_09173", "form_district_09172", "form_district_09174", "form_district_09175", "form_district_09176", "form_district_09177", "form_district_09178", "form_district_09179", "form_district_09180", "form_district_09161",
                     "form_district_09181", "form_district_09182", "form_district_09183", "form_district_09184", "form_district_09162", "form_district_09185", "form_district_09186", "form_district_09187", "form_district_09163", "form_district_09188", "form_district_09189", "form_district_09190"]


def page_pars(link_to_page):
    print("Parsing subpage number:", link_to_page[0], end='\r')
    url = stand + link_to_page[1]
    driver.get(url)
    d = {}
    list_of_labels = []
    list_of_definitions = []
    # with open('progress_log.txt', 'a') as file:
    # file.write("\nSite number: " + str(page_num))
    # file.write("\nSite name: " + str(url))
    # print("\nSite name: " + str(url))
    # try:
    for path in list_of_div:
        label = driver.find_element_by_xpath(path)
        all_children_by_css = label.find_elements_by_css_selector("*")
        for item in all_children_by_css:
            attr = item.get_attribute("class")
            text = item.text
            if 'Map' in text:
                break
            elif attr == 'label':
                list_of_labels.append(text)
            elif attr == 'definition':
                list_of_definitions.append(text)
    for i, item in enumerate(list_of_labels):
        d[item] = list_of_definitions[i]
    
    time_to_wati = max(0, 1 + np.random.normal(0, 1))
    # file.write("\n" + str(time_to_wati))
    # print("\n" + str(time_to_wati))
    time.sleep(time_to_wati)
    # except:
    #     # file.write("\nSomething went wrong.")
    #     print("\nSomething went wrong.")
    return d

start_time = time.time()

# Initiate the main driver
driver = inititate_driver()

# Initiate another driver for page parsing
# driver_page = inititate_driver()


if __name__ == '__main__':

    # Execute the specyfic search. If we want to get all the results should make an iteration from here on!
    get_the_search_page([1])

    # Capture the screen to make sure all is ok
    driver.get_screenshot_as_file("capture.png")
    load_page_time = time.time()
    # print(f'Page sucessfully loaded! Time to load: {load_page_time - start_time:.2f}s\n')
    print("Page sucessfully loaded! Time to load:", {load_page_time - start_time}, 's\n')
    # We can also store the source code of the page
    # driver.page_source

    # Get the number of pages and total amount of results we need to process
    n_of_pages = int(driver.find_element_by_xpath(
        "//*[@id='keytech_list_result']/div[1]/nav/ul/li[5]/a").text)
    n_of_resutls = (driver.find_element_by_xpath("//*[@id = 'keytech_list_result']/p/strong").text)
    print("There are:", n_of_pages, "pages")
    print("Total number of results is:", n_of_resutls)

    try: list_of_links
    except NameError: list_of_links = []
        # print("Not exists yet. Defining now!")
        # list_of_links = []
    # else: print("Already exists!")

    n_of_pages = 4
    all_info = []

    with concurrent.futures.ProcessPoolExecutor() as executors:

        # Get only the links that we need
        with concurrent.futures.ThreadPoolExecutor() as executor:

            # Let's start parsing the pages
            for i in range(n_of_pages):
                a_tags = load_result_page(i)

                links_result = executor.map(pars_result_page, a_tags)
                links_result = list(filter(None, links_result))

                list_of_links = list_of_links + links_result
                print('\n', "Started parsing page:", i + 1)
                page_start_time = time.time()

                results = executors.map(page_pars, enumerate(links_result))
                all_info = all_info + list(results)

                page_end_time = time.time()
                print("Time needed for parsing subpages:", {page_end_time - page_start_time}, 's')
                # all_info.append(list(results))
                # print(list(results))
      
    # Define DATAFRAME and add the links to sites
    df = pd.DataFrame(all_info)
    df["Bayer Internatinal Links"] = list_of_links
    df = DataClean.DataClean(df)
    cols = df.columns.tolist()
    order_list = [0, 9, 7, 2, 8, 4, 3, 5, 6, 1, 10]
    cols = [cols[i] for i in order_list]
    df = df[cols]
    df.to_csv('Upper_Bavaria_info.csv', sep=';',
              encoding='latin-1', index_label=False, index=False)

    end_time = time.time()
    print('Total time:', {end_time - load_page_time}, 's\n')



