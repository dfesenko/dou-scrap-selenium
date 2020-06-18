import time
from utils import AdapterMongo, AdapterCSV
from selenium import webdriver

from config import DRIVER_PATH, TEMP_STORAGE


def main(driver_path, storage_type):
    driver = webdriver.Chrome(executable_path=driver_path)
    scrap_categories_links(driver=driver, storage_type=storage_type)


def scrap_categories_links(driver, storage_type):
    driver.get('https://jobs.dou.ua/')
    time.sleep(2)

    if storage_type == 'mongo':
        storage_adapter = AdapterMongo('localhost', 27017, 'dou-scrapping-db')
    else:
        storage_adapter = AdapterCSV()

    categories = driver.find_elements_by_xpath("//a[@class='cat-link']")
    links_to_categories = [category.get_attribute('href') for category in categories]
    category_names = [category.text for category in categories]

    storage_adapter.temp_store_category_links(links=links_to_categories, categories_names=category_names)

    print(f'{len(links_to_categories)} categories scrapped')

    return links_to_categories, category_names


if __name__ == '__main__':
    main(driver_path=DRIVER_PATH, storage_type=TEMP_STORAGE)
