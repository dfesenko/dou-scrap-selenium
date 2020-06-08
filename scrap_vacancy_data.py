import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from utils import load_temp_data, write_result_to_csv, write_result_to_mongo, update_scrap_status
from config import DRIVER_PATH


def main(destination, temp_storage_type):
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)
    links_to_vacancies, vacancy_titles, categories = load_temp_data(storage_type=temp_storage_type,
                                                                    data_type='vacancies')
    if destination == 'csv':
        write_result_to_csv(is_headline=True)

    for i in range(len(links_to_vacancies)):
        scrap_vacancy_data(driver=driver, destination=destination,
                           vacancy_title=vacancy_titles[i], vacancy_link=links_to_vacancies[i], category=categories[i])

        update_scrap_status(vacancy_link=links_to_vacancies[i], vacancy_title=vacancy_titles[i],
                            storage_type=temp_storage_type)


def scrap_vacancy_data(driver, destination, vacancy_title, vacancy_link, category):
    driver.get(vacancy_link)
    time.sleep(3)

    xpaths = {'company': "//div[@class='b-vacancy']/div[@class='b-compinfo']/div[@class='info']//a[1]",
              'location': "//div[@class='b-vacancy']//span[@class='place']",
              'date': "//div[@class='b-vacancy']//div[@class='date']"}
    results = {}

    for target_name in xpaths:
        try:
            results[target_name] = driver.find_element_by_xpath(xpaths[target_name]).text
        except NoSuchElementException:
            pass

    url = driver.current_url

    if destination == 'csv':
        write_result_to_csv(category=category, title=vacancy_title, company=results['company'],
                            location=results['location'], date=results['date'], url=url)

    elif destination == 'mongo':
        write_result_to_mongo(category=category, title=vacancy_title, company=results['company'],
                              location=results['location'], date=results['date'], url=url)


if __name__ == '__main__':
    DESTINATION = 'mongo'
    TEMP_STORAGE = 'mongo'
    main(destination=DESTINATION, temp_storage_type=TEMP_STORAGE)
