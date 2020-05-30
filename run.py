import time
import csv

from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException

DRIVER_PATH = '/home/dmitrij/PycharmProjects/dou_scrap_selenium/chromedriver'
driver = webdriver.Chrome(executable_path=DRIVER_PATH)

driver.get('https://jobs.dou.ua/')
time.sleep(2)

categories = driver.find_elements_by_xpath("//a[@class='cat-link']")

count_scrapped = 0

with open('jobs.csv', mode='w') as csv_file:
    fieldnames = ['category', 'title', 'company', 'location', 'date', 'url']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for i in range(len(categories)):
        category_name = categories[i].text
        print(category_name)
        categories[i].click()
        time.sleep(1)

        more_btn = driver.find_element_by_xpath("//div[@class='more-btn']/a")
        while True:
            try:
                more_btn.click()
                time.sleep(2)
            except ElementNotInteractableException:
                break

        vacancies = driver.find_elements_by_xpath("//div[@class='vacancy']/div[@class='title']/a[@class='vt']")

        for j in range(len(vacancies)):
            title = vacancies[j].text
            vacancies[j].click()
            time.sleep(1)
            company = driver.find_elements_by_xpath(
                "//div[@class='b-vacancy']/div[@class='b-compinfo']/div[@class='info']//a[1]")[0].text

            location = driver.find_element_by_xpath("//div[@class='b-vacancy']//span[@class='place']").text
            date = driver.find_element_by_xpath("//div[@class='b-vacancy']//div[@class='date']").text
            url = driver.current_url

            writer.writerow({'category': category_name, 'title': title, 'company': company,
                             'location': location, 'date': date, 'url': url})

            count_scrapped += 1

            if count_scrapped % 10 == 0:
                print(count_scrapped)

            driver.back()
            time.sleep(0.5)
            vacancies = driver.find_elements_by_xpath("//div[@class='vacancy']/div[@class='title']/a[@class='vt']")

        driver.back()
        time.sleep(1)
        categories = driver.find_elements_by_xpath("//a[@class='cat-link']")

driver.close()






