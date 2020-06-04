import time

from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException

from utils import store_temp_data, load_temp_data
from config import DRIVER_PATH


def main():
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)
    storage_type = 'csv'
    links_to_categories, category_names = load_temp_data(storage_type=storage_type, data_type='categories')

    for i in range(len(links_to_categories)):
        links_to_vacancies, vacancy_titles = scrap_vacancies_links(driver=driver, storage_type=storage_type,
                                                                   link_to_category=links_to_categories[i],
                                                                   category=category_names[i], iteration=i)

        print(f"Scrapped vacancies links for category: {category_names[i]}. Num links: {len(links_to_vacancies)} \n")


def scrap_vacancies_links(driver, storage_type, link_to_category, category, iteration=None):
    print(category)
    driver.get(link_to_category)
    time.sleep(1)

    try:
        more_btn = driver.find_element_by_xpath("//div[@class='more-btn']/a")

        while True:
            try:
                more_btn.click()
                time.sleep(1)
            except ElementNotInteractableException:
                break

    except NoSuchElementException:
        pass

    vacancies = driver.find_elements_by_xpath("//div[@class='vacancy']/div[@class='title']/a[@class='vt']")

    print(f"For {category} detected {len(vacancies)} vacancies.")

    links_to_vacancies = [vacancy.get_attribute('href') for vacancy in vacancies]
    vacancy_titles = [vacancy.text for vacancy in vacancies]

    store_temp_data(temp_storage_type=storage_type, category_name=category,
                    links=links_to_vacancies, links_info=vacancy_titles, iteration=iteration, is_vacancies=True)

    return links_to_vacancies, vacancy_titles


if __name__ == '__main__':
    main()
