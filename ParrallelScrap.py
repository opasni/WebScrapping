from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

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


def get_details():

    landkreis_codes = pd.read_excel('LandKreisKode.xlsx')

    part_dataf = landkreis_codes[landkreis_codes['Status'] == -1]

    reg_names = ['Regierungsbezirk',
                 'regierungsbezirk_eng', 
                 'regierungsbezirk_kurz', 
                 'Regierungsbezirk code']

    regbez, regbez_eng, regbez_kurz, regbez_code = [
        list(set(part_dataf[it])) for it in reg_names]

    regbez_code = ['0' + str(num) for num in regbez_code]


    landkreis = [list(part_dataf[part_dataf['Regierungsbezirk']
                                    == reg]['Landkreis']) for reg in regbez]
    landkreis_code = [list(part_dataf[part_dataf['Regierungsbezirk']
                                        == reg]['Landkreis code']) for reg in regbez]

    return (regbez, regbez_eng, regbez_kurz, regbez_code, landkreis, landkreis_code)


def get_the_search_page(list_of_districts, regierungsbezirk_code):
    driver.get("https://www.bayern-international.de/en/company-database/")

    # foldable_header = driver.find_element_by_class_name(name="foldable header")
    foldable_header = driver.find_element_by_css_selector(
        "div.foldable-container.keytech-search-form-extended.collapsed")
    foldable_header.click()

    select = Select(driver.find_element_by_name(
        name="tx_keytechrenew_keytech[state_province]"))
    select.select_by_value(regierungsbezirk_code)

    time.sleep(8)

    select_none = driver.find_element_by_css_selector(
        "a.form-district-select-none")
    select_none.click()

    driver.get_screenshot_as_file("test.png")

    picked_districts = list_of_districts
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
    
    time_to_wati = max(0, 0.2 + np.random.normal(0, 1))
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

if __name__ == '__main__':


    # The Important Stuff!!! Change to what needed!
    regbez, regbez_eng, regbez_kurz, regbez_code, landkreis, landkreis_code = get_details()

    print("Scrapping {} regoins, which are:" .format(len(regbez)), regbez)

    for reg in range(len(regbez)):

        print("Started with {} districts, which are:" .format(
            len(landkreis[reg])), landkreis[reg])

        print("The codes for the districts are:", landkreis_code[reg])

        # Execute the specyfic search. If we want to get all the results should make an iteration from here on!
        get_the_search_page(landkreis_code[reg], regbez_code[reg])
        # Capture the screen to make sure all is ok
        driver.get_screenshot_as_file("capture.png")

        load_page_time = time.time()
        print("Page sucessfully loaded! Time to load:", {load_page_time - start_time}, 's\n')
    


        # Get the number of pages and total amount of results we need to process
        n_of_pages = int(driver.find_element_by_xpath(
            "//*[@id='keytech_list_result']/div[1]/nav/ul/li[5]/a").text)
        n_of_resutls = (driver.find_element_by_xpath("//*[@id = 'keytech_list_result']/p/strong").text)
        print("There are:", n_of_pages, "pages")
        print("Total number of results is:", n_of_resutls)

        # try: list_of_links
        # except NameError: list_of_links = []

        list_of_links = []

        n_of_pages = 1
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
        
        # Define DATAFRAME and add the links to sites
        df = pd.DataFrame(all_info)
        df["Bayer Internatinal Links"] = list_of_links

        file_name = regbez[reg] + '_info.csv'

        df.to_csv(file_name, sep=';',
                encoding='utf-8', index_label=False, index=False)

        end_time = time.time()
        print('Total time:', {end_time - load_page_time}, 's\n')


        # We try to produce the final data

        from DataClean import DataClean
        # try:
        dataF = pd.DataFrame([DataClean(row, regbez[reg], regbez_eng[reg])
                            for index, row in df.iterrows()])

        # dataF = DataClean(df)

        # Remove the Gigatronic and MBtech
        dataF = dataF.drop(dataF[(dataF['Email Address'] == 'info@mbtech-group.com')
                                | (dataF['Email Address'] == 'info-ing@gigatronik.com')].index)

        # Create a list where we remove all the companies without e-mails or other requrements
        dataF_with_email = dataF[dataF['Email Address']
                                != 'not available']  # .reset_index(drop=True)

        fin_file_name = regbez[reg] + '_cleaned.csv'
        # Seving the data in tab delimited format (readable by mailchunk)
        dataF_with_email.to_csv(fin_file_name, sep='\t',
                                encoding='utf-8', index_label=False, index=False)

        # Let's make the separated lists
        all_landkreis_name = [item.replace(' ', '_').replace(',', '_').replace(
            '.', '_').replace('__', '_') for item in landkreis[reg]]
        for j in range(len(landkreis[reg])):
            filename = './/' + regbez[reg] + '/' + regbez_kurz[reg] + '_' + all_landkreis_name[j] + '.csv'
            print(filename)
            dataF_with_email[dataF_with_email['Landkreis'] == landkreis[reg][j]].to_csv(
                filename, sep='\t', encoding='utf-8', index_label=False, index=False)

        # except:
        #     print("There was an error while cleaning the data!")

        del df

