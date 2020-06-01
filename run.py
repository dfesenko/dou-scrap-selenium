import time
import csv

from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException

from pymongo import MongoClient
from typing import List
from datetime import datetime

from config import DRIVER_PATH


def main(driver_path):
    driver = webdriver.Chrome(executable_path=driver_path)

    driver.get('https://jobs.dou.ua/')
    time.sleep(2)

    categories = driver.find_elements_by_xpath("//a[@class='cat-link']")
    links_to_categories = [category.get_attribute('href') for category in categories]
    category_names = [category.text for category in categories]

    insert_into_mongodb(links=links_to_categories, links_info=category_names)

    count_scrapped = 0

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

            write_to_csv(category=category, title=title, company=company, location=location, date=date, url=url)

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


def insert_into_mongodb(links: List[str], links_info: List[str]):
    client = MongoClient('localhost', 27017)
    db = client['dou-scrapping-db']
    collection = db['links-to-process']
    links_to_insert = [{'link': item[0], 'description': item[1], 'status': 'Todo', 'created_at': datetime.utcnow()}
                       for item in zip(links, links_info)]
    collection.insert_many(links_to_insert)


if __name__ == '__main__':
    main(DRIVER_PATH)
