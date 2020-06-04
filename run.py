import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from config import DRIVER_PATH
from utils import store_temp_data, write_to_csv, write_to_mongo, load_temp_data
from scrap_categories_links import scrap_categories_links
from scrap_vacancies_links import scrap_vacancies_links


def main(driver_path, destination, temporary_storage_type):
    """
    @param driver_path: string that represent the path to the web driver used for automation
    @param destination: either 'csv' or 'mongo' - the place where to store the scrapped data
    @param temporary_storage_type: either 'csv' or 'mongo' - the place where to store temporary data.
                                   This includes links that should be scrapped in future.
    """
    driver = webdriver.Chrome(executable_path=driver_path)

    links_to_categories, category_names = scrap_categories_links(driver=driver, storage_type=temporary_storage_type)

    count_scrapped = 0

    if destination == 'csv':
        write_to_csv(is_headline=True)

    for i in range(len(links_to_categories)):
        category = category_names[i]
        links_to_vacancies, vacancy_titles = scrap_vacancies_links(driver=driver, storage_type=temporary_storage_type,
                                                                   link_to_category=links_to_categories[i],
                                                                   category=category, iteration=i)
        for j in range(len(links_to_vacancies)):
            title = vacancy_titles[j]
            driver.get(links_to_vacancies[j])
            time.sleep(3)

            company = None
            location = None
            date = None

            try:
                company = driver.find_elements_by_xpath(
                    "//div[@class='b-vacancy']/div[@class='b-compinfo']/div[@class='info']//a[1]")[0].text
                location = driver.find_element_by_xpath("//div[@class='b-vacancy']//span[@class='place']").text
                date = driver.find_element_by_xpath("//div[@class='b-vacancy']//div[@class='date']").text
            except NoSuchElementException:
                pass

            url = driver.current_url

            if destination == 'csv':
                write_to_csv(category=category, title=title, company=company, location=location, date=date, url=url)
            elif destination == 'mongo':
                write_to_mongo(category=category, title=title, company=company, location=location, date=date, url=url)

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
