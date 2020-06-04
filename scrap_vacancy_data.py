import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from utils import load_temp_data, write_to_csv, write_to_mongo
from config import DRIVER_PATH


def main():
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)
    destination = 'csv'
    temp_storage_type = 'csv'
    links_to_vacancies, vacancy_titles, categories = load_temp_data(storage_type=temp_storage_type,
                                                                    data_type='vacancies')
    if destination == 'csv':
        write_to_csv(is_headline=True)

    for i in range(len(links_to_vacancies)):
        scrap_vacancy_data(driver=driver, destination=destination,
                           vacancy_title=vacancy_titles[i], vacancy_link=links_to_vacancies[i], category=categories[i])


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
        write_to_csv(category=category, title=vacancy_title, company=results['company'],
                     location=results['location'], date=results['date'], url=url)

    elif destination == 'mongo':
        write_to_mongo(category=category, title=vacancy_title, company=results['company'],
                       location=results['location'], date=results['date'], url=url)


if __name__ == '__main__':
    main()