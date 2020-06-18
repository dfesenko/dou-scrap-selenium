import time

from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, \
    StaleElementReferenceException

from utils import AdapterMongo, AdapterCSV
from config import DRIVER_PATH, TEMP_STORAGE


def main(driver_path, storage_type):
    driver = webdriver.Chrome(executable_path=driver_path)

    if storage_type == 'mongo':
        storage_adapter = AdapterMongo('localhost', 27017, 'dou-scrapping-db')
    else:
        storage_adapter = AdapterCSV()

    links_to_categories, category_names = storage_adapter.load_category_links()

    for i in range(len(links_to_categories)):
        links_to_vacancies, vacancy_titles = scrap_vacancies_links(driver=driver, storage_adapter=storage_adapter,
                                                                   link_to_category=links_to_categories[i],
                                                                   category=category_names[i])

        print(f"Scrapped vacancies links for category: {category_names[i]}. Num links: {len(links_to_vacancies)} \n")


def scrap_vacancies_links(driver, storage_adapter, link_to_category, category):
    print(category)
    driver.get(link_to_category)
    time.sleep(2)

    while True:
        try:
            more_btn = driver.find_element_by_xpath("//div[@class='more-btn']/a")
            more_btn.click()
            time.sleep(2)
        except (NoSuchElementException, ElementNotInteractableException):
            break
        except StaleElementReferenceException:
            pass

    vacancies = driver.find_elements_by_xpath("//div[@class='vacancy']/div[@class='title']/a[@class='vt']")

    print(f"For {category} detected {len(vacancies)} vacancies.")

    links_to_vacancies = [vacancy.get_attribute('href') for vacancy in vacancies]
    vacancy_titles = [vacancy.text for vacancy in vacancies]

    storage_adapter.temp_store_vacancy_links(links=links_to_vacancies, vacancy_titles=vacancy_titles,
                                             category_name=category)

    return links_to_vacancies, vacancy_titles


if __name__ == '__main__':
    main(driver_path=DRIVER_PATH, storage_type=TEMP_STORAGE)
