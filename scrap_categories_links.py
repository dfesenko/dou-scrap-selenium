import time
from utils import store_temp_data
from selenium import webdriver

from config import DRIVER_PATH


def main():
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)
    storage_type = 'csv'
    scrap_categories_links(driver=driver, storage_type=storage_type)


def scrap_categories_links(driver, storage_type):
    driver.get('https://jobs.dou.ua/')
    time.sleep(2)

    categories = driver.find_elements_by_xpath("//a[@class='cat-link']")
    links_to_categories = [category.get_attribute('href') for category in categories]
    category_names = [category.text for category in categories]

    store_temp_data(temp_storage_type=storage_type,
                    links=links_to_categories, links_info=category_names, iteration=0, is_categories=True)

    print(f'{len(links_to_categories)} categories scrapped')

    return links_to_categories, category_names


if __name__ == '__main__':
    main()
