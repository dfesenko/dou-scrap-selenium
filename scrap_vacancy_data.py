import time
from random import randint

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from utils import AdapterMongo, AdapterCSV
from config import DRIVER_PATH, TEMP_STORAGE, DESTINATION


def main(driver_path, destination, temp_storage_type):
    if destination == 'mongo':
        destination_adapter = AdapterMongo('localhost', 27017, 'dou-scrapping-db')
    else:
        destination_adapter = AdapterCSV(filename='dou-jobs-data.csv')

    if temp_storage_type == 'mongo':
        temp_storage_adapter = AdapterMongo('localhost', 27017, 'dou-scrapping-db')
    else:
        temp_storage_adapter = AdapterCSV()

    driver = webdriver.Chrome(executable_path=driver_path)
    categories_to_parse = temp_storage_adapter.load_categories_to_parse()
    print(categories_to_parse)
    print(len(categories_to_parse))

    for category in categories_to_parse:
        print(f'Start scrapping category: {category}')
        links_to_vacancies, vacancy_titles = temp_storage_adapter.load_category_vacancies(category=category)
        print(category, len(links_to_vacancies))

        for i in range(len(links_to_vacancies)):
            scrap_vacancy_data(driver=driver, destination_adapter=destination_adapter,
                               vacancy_title=vacancy_titles[i], vacancy_link=links_to_vacancies[i], category=category)

            temp_storage_adapter.update_vacancy_scrap_status(vacancy_link=links_to_vacancies[i],
                                                             vacancy_title=vacancy_titles[i], category=category)
            print(i+1)

        temp_storage_adapter.update_category_scrap_status(category=category)


def scrap_vacancy_data(driver, destination_adapter, vacancy_title, vacancy_link, category):
    driver.get(vacancy_link)
    time.sleep(randint(1, 5))

    xpaths = {'company': "//div[@class='b-vacancy']/div[@class='b-compinfo']/div[@class='info']//a[1]",
              'location': "//div[@class='b-vacancy']//span[@class='place']",
              'date': "//div[@class='b-vacancy']//div[@class='date']"}
    results = {}

    for target_name in xpaths:
        try:
            results[target_name] = driver.find_element_by_xpath(xpaths[target_name]).text
        except NoSuchElementException:
            results[target_name] = None

    url = driver.current_url

    destination_adapter.flush_result(category=category, title=vacancy_title, company=results['company'],
                                     location=results['location'], date=results['date'], url=url)


if __name__ == '__main__':
    main(driver_path=DRIVER_PATH, destination=DESTINATION, temp_storage_type=TEMP_STORAGE)
