import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from utils import update_scrap_status, load_categories_to_parse, load_category_vacancies, \
    update_category_scrap_status, AdapterMongo, AdapterCSV
from config import DRIVER_PATH


def main(destination, temp_storage_type):
    if destination == 'mongo':
        destination_adapter = AdapterMongo('localhost', 27017, 'dou-scrapping-db')
    else:
        destination_adapter = AdapterCSV('jobs2.csv')

    driver = webdriver.Chrome(executable_path=DRIVER_PATH)
    categories_to_parse = load_categories_to_parse()
    print(categories_to_parse)
    print(len(categories_to_parse))

    if categories_to_parse and destination == 'csv':
        destination_adapter.create_csv_headline()

    for category in categories_to_parse:
        print(f"Start scrapping category: {category}")
        links_to_vacancies, vacancy_titles = load_category_vacancies(category=category)
        print(category, len(links_to_vacancies))

        for i in range(len(links_to_vacancies)):
            scrap_vacancy_data(driver=driver, destination_adapter=destination_adapter,
                               vacancy_title=vacancy_titles[i], vacancy_link=links_to_vacancies[i], category=category)

            update_scrap_status(vacancy_link=links_to_vacancies[i], vacancy_title=vacancy_titles[i], category=category,
                                storage_type=temp_storage_type)
            print(i)

        update_category_scrap_status(category=category)


def scrap_vacancy_data(driver, destination_adapter, vacancy_title, vacancy_link, category):
    driver.get(vacancy_link)
    time.sleep(3)

    xpaths = {'company': "//div[@class='b-vacancy']/div[@class='b-compinfo']/div[@class='info']//a[1]",
              'location': "//div[@class='b-vacancy']//span[@class='place']",
              'date': "//div[@class='b-vacancy']//div[@class='date']"}
    results = {'company': None, 'location': None, 'date': None}

    for target_name in xpaths:
        try:
            results[target_name] = driver.find_element_by_xpath(xpaths[target_name]).text
        except NoSuchElementException:
            pass

    url = driver.current_url

    destination_adapter.flush_result(category=category, title=vacancy_title, company=results['company'],
                                     location=results['location'], date=results['date'], url=url)


if __name__ == '__main__':
    DESTINATION = 'csv'
    TEMP_STORAGE = 'mongo'
    main(destination=DESTINATION, temp_storage_type=TEMP_STORAGE)
