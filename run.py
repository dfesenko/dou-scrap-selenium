import time

from selenium import webdriver

from config import DRIVER_PATH
from utils import update_scrap_status, update_category_scrap_status, AdapterCSV, AdapterMongo
from scrap_categories_links import scrap_categories_links
from scrap_vacancies_links import scrap_vacancies_links
from scrap_vacancy_data import scrap_vacancy_data


def main(driver_path, destination, temporary_storage_type):
    """
    @param driver_path: string that represent the path to the web driver used for automation
    @param destination: either 'csv' or 'mongo' - the place where to store the scrapped data
    @param temporary_storage_type: either 'csv' or 'mongo' - the place where to store temporary data.
                                   This includes links that should be scrapped in future.
    """
    driver = webdriver.Chrome(executable_path=driver_path)

    if destination == 'mongo':
        destination_adapter = AdapterMongo('localhost', 27017, 'dou-scrapping-db')
    else:
        destination_adapter = AdapterCSV('jobs2.csv')

    links_to_categories, category_names = scrap_categories_links(driver=driver, storage_type=temporary_storage_type)
    count_scrapped = 0

    if links_to_categories and destination == 'csv':
        destination_adapter.create_csv_headline()

    for i in range(len(links_to_categories)):
        category = category_names[i]
        links_to_vacancies, vacancy_titles = scrap_vacancies_links(driver=driver, storage_type=temporary_storage_type,
                                                                   link_to_category=links_to_categories[i],
                                                                   category=category, iteration=i)
        for j in range(len(links_to_vacancies)):
            scrap_vacancy_data(driver=driver, destination_adapter=destination_adapter, vacancy_title=vacancy_titles[j],
                               vacancy_link=links_to_vacancies[j], category=category)

            update_scrap_status(vacancy_link=links_to_vacancies[i], vacancy_title=vacancy_titles[i],
                                storage_type=temporary_storage_type, category=category)

            update_category_scrap_status(category=category)

            count_scrapped += 1

            if count_scrapped % 20 == 0:
                print(count_scrapped)

        print(f"Scrapped category {category}")
        time.sleep(5)

    driver.close()


if __name__ == '__main__':
    DESTINATION = 'mongo'
    TEMP_STORAGE = 'csv'
    main(driver_path=DRIVER_PATH, destination=DESTINATION, temporary_storage_type=TEMP_STORAGE)
