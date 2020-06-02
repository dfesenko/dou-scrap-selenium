import time
import csv

from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException

from pymongo import MongoClient
from typing import List
from datetime import datetime

from config import DRIVER_PATH


def main(driver_path, destination):
    driver = webdriver.Chrome(executable_path=driver_path)

    driver.get('https://jobs.dou.ua/')
    time.sleep(2)

    categories = driver.find_elements_by_xpath("//a[@class='cat-link']")
    links_to_categories = [category.get_attribute('href') for category in categories]
    category_names = [category.text for category in categories]

    insert_plan_into_mongodb(links=links_to_categories, links_info=category_names, is_categories=True)

    count_scrapped = 0

    if destination == 'csv':
        write_to_csv(is_headline=True)

    for i in range(len(links_to_categories)):
        category = category_names[i]
        print(category)
        driver.get(links_to_categories[i])
        time.sleep(1)

        more_btn = driver.find_element_by_xpath("//div[@class='more-btn']/a")
        while True:
            try:
                more_btn.click()
                time.sleep(2)
            except ElementNotInteractableException:
                break

        vacancies = driver.find_elements_by_xpath("//div[@class='vacancy']/div[@class='title']/a[@class='vt']")

        print(f"For {category} detected {len(vacancies)} vacancies.")

        links_to_vacancies = [vacancy.get_attribute('href') for vacancy in vacancies]
        vacancy_titles = [vacancy.text for vacancy in vacancies]

        insert_plan_into_mongodb(links=links_to_vacancies, links_info=vacancy_titles, is_vacancies=True)

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


def write_to_csv(is_headline=False, category=None, title=None, company=None, location=None, date=None, url=None):
    fieldnames = ['category', 'title', 'company', 'location', 'date', 'url']
    with open('jobs2.csv', mode='a+') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if is_headline:
            writer.writeheader()
        else:
            writer.writerow({'category': category, 'title': title, 'company': company,
                             'location': location, 'date': date, 'url': url})


def write_to_mongo(category, title, company, location, date, url):
    client = MongoClient('localhost', 27017)
    db = client['dou-scrapping-db']

    collection = db['dou-jobs-data']
    doc_to_insert = {'category': category, 'title': title, 'company': company,
                     'location': location, 'date': date, 'url': url}
    collection.insert_one(doc_to_insert)


def insert_plan_into_mongodb(links: List[str], links_info: List[str], is_categories=None, is_vacancies=None):
    """
    Inserts items that should be scrapped in the future into the MongoDB database.

    @param links: links to items that should be scrapped
    @param links_info: description of an item (name of category or vacancy title, for example)
    @param is_categories: flag for categories
    @param is_vacancies: flag for vacancies
    """
    if is_categories and is_vacancies:
        raise Exception("insert_into_mongodb() function can insert just 1 type of content at a time")
    elif not is_categories and not is_vacancies:
        raise Exception("insert_into_mongodb() function expects a flag of what is the kind of the content to insert")

    client = MongoClient('localhost', 27017)
    db = client['dou-scrapping-db']

    kind = 'category' if is_categories else 'vacancy'
    collection = db[f'{kind}-links-to-process']
    links_to_insert = [{'link': item[0], f'{kind}_name': item[1], 'is_scrapped': False,
                        'created_at': datetime.utcnow()} for item in zip(links, links_info)]
    collection.insert_many(links_to_insert)


if __name__ == '__main__':
    DESTINATION = 'mongo'
    main(DRIVER_PATH, DESTINATION)
