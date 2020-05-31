import time
import csv

from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException

DRIVER_PATH = '/home/dmitrij/PycharmProjects/dou_scrap_selenium/chromedriver'
driver = webdriver.Chrome(executable_path=DRIVER_PATH)

driver.get('https://jobs.dou.ua/')
time.sleep(2)

categories = driver.find_elements_by_xpath("//a[@class='cat-link']")
links_to_categories = [category.get_attribute('href') for category in categories]
category_names = [category.text for category in categories]

count_scrapped = 0

with open('jobs2.csv', mode='w') as csv_file:
    fieldnames = ['category', 'title', 'company', 'location', 'date', 'url']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for i in range(len(links_to_categories)):
        category_name = category_names[i]
        print(category_name)
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

        print(f"For {category_name} detected {len(vacancies)} vacancies.")

        links_to_vacancies = [vacancy.get_attribute('href') for vacancy in vacancies]
        vacancy_titles = [vacancy.text for vacancy in vacancies]

        for j in range(len(links_to_vacancies)):
            title = vacancy_titles[j]
            driver.get(links_to_vacancies[j])
            time.sleep(5)

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

            writer.writerow({'category': category_name, 'title': title, 'company': company,
                             'location': location, 'date': date, 'url': url})

            count_scrapped += 1

            if count_scrapped % 10 == 0:
                print(count_scrapped)

        print(f"Scrapped category {category_name}")
        time.sleep(10)

driver.close()






