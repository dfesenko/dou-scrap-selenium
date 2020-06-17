import csv
import os
import shutil

from tempfile import NamedTemporaryFile
from pymongo import MongoClient
from typing import List
from datetime import datetime


class AdapterMongo:
    def __init__(self, host, port, db_name):
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]

    def flush_result(self, category, title, url, company=None, location=None, date=None):
        """
        Writes the scrapped data to MongoDB database collection.
        @param category: scrapped category of the vacancy
        @param title: scrapped title of the vacancy
        @param company: scrapped company name
        @param location: scrapped location of the job
        @param date: scrapped date of vacancy posting
        @param url: url of the vacancy
        """
        collection = self.db['dou-jobs-data']
        doc_to_insert = {'category': category, 'title': title, 'company': company,
                         'location': location, 'date': date, 'url': url}
        collection.insert_one(doc_to_insert)

    def load_category_links(self):
        """
        Needed for further collection of links to vacancies
        """
        links_to_categories = []
        category_names = []
        collection = self.db['category-links-to-process']

        for item in collection.find({"is_scrapped": False}):
            links_to_categories.append(item['link'])
            category_names.append(item['category_name'])
        return links_to_categories, category_names

    def load_categories_to_parse(self):
        """
        Fetch categories that have more than 0 not-scrapped vacancies
        """
        collection = self.db['vacancy-links-to-process']
        return collection.distinct("category", {"is_scrapped": False})

    def load_category_vacancies(self, category):
        """
        Fetch all not-scrapped vacancies links for the given category
        """
        links_to_vacancies = []
        vacancy_titles = []
        collection = self.db['vacancy-links-to-process']

        for item in collection.find({"category": category, "is_scrapped": False}):
            links_to_vacancies.append(item['link'])
            vacancy_titles.append(item['vacancy_title'])
        return links_to_vacancies, vacancy_titles

    def update_vacancy_scrap_status(self, vacancy_link, vacancy_title, category):
        collection = self.db['vacancy-links-to-process']

        query = {'link': vacancy_link, 'vacancy_title': vacancy_title, 'category': category}
        collection.update_one(query, {"$set": {"is_scrapped": True, "datetime_scrapped": datetime.utcnow()}})
        print("vacancy status set to scrapped = True")

    def update_category_scrap_status(self, category):
        collection = self.db['category-links-to-process']
        query = {"category_name": category}

        collection.update_one(query, {"$set": {"is_scrapped": True, "datetime_scrapped": datetime.utcnow()}})
        print("category status set to scrapped = True")

    def temp_store_category_links(self, links: List[str], categories_names: List[str]):
        """
        Inserts category links that should be scrapped in the future into the MongoDB database.

        @param links: links to categories that should be scrapped
        @param categories_names: names of categories
        """
        collection = self.db['category-links-to-process']
        links_to_insert = [{'link': item[0], 'category_name': item[1], 'is_scrapped': False,
                            'created_at': datetime.utcnow()} for item in zip(links, categories_names)]
        collection.insert_many(links_to_insert)

    def temp_store_vacancy_links(self, links: List[str], vacancy_titles: List[str], category_name: str):
        """
        Inserts vacancy links that should be scrapped in the future into the MongoDB database.

        @param links: links to vacancies that should be scrapped
        @param vacancy_titles: vacancies titles
        @param category_name: the name of category to which belongs given butch of vacancies
        """
        collection = self.db['vacancy-links-to-process']
        links_to_insert = [{'link': item[0], 'vacancy_title': item[1], 'is_scrapped': False, 'category': category_name,
                            'created_at': datetime.utcnow()} for item in zip(links, vacancy_titles)]
        collection.insert_many(links_to_insert)


class AdapterCSV:
    def __init__(self, filename=None):
        self.result_fieldnames = ['category', 'title', 'company', 'location', 'date', 'url']
        self.temp_category_fields = ['link', 'category_name', 'is_scrapped', 'created_at', 'scrapped_at']
        self.temp_vacancy_fields = ['link', 'vacancy_title', 'is_scrapped', 'category', 'created_at', 'scrapped_at']

        self.result_filename = filename
        self.temp_category_filename = 'category-links-to-process.csv'
        self.temp_vacancy_filename = 'vacancy-links-to-process.csv'

    def create_csv_headline(self, filename, fieldnames):
        if not os.path.isfile(filename):
            with open(filename, mode='a+') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()

    def flush_result(self, category, title, url, company=None, location=None, date=None):
        """
        Writes the scrapped data to CSV file.
        @param category: scrapped category of the vacancy
        @param title: scrapped title of the vacancy
        @param company: scrapped company name
        @param location: scrapped location of the job
        @param date: scrapped date of vacancy posting
        @param url: url of the vacancy
        """
        self.create_csv_headline(self.result_filename, self.result_fieldnames)

        with open(self.result_filename, mode='a+') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.result_fieldnames)
            writer.writerow({'category': category, 'title': title, 'company': company,
                            'location': location, 'date': date, 'url': url})

    def temp_store_category_links(self, links: List[str], categories_names: List[str]):
        """
        Inserts category links that should be scrapped in the future into the CSV file.

        @param links: links to categories that should be scrapped
        @param categories_names: names of categories
        """
        self.create_csv_headline(self.temp_category_filename, self.temp_category_fields)

        links_to_insert = [{'link': item[0], 'category_name': item[1], 'is_scrapped': False,
                            'created_at': datetime.utcnow()} for item in zip(links, categories_names)]

        with open(self.temp_category_filename, mode='a+') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.temp_category_fields)
            writer.writerows(links_to_insert)

    def temp_store_vacancy_links(self, links: List[str], vacancy_titles: List[str], category_name: str):
        """
        Inserts vacancy links that should be scrapped in the future into the CSV file.

        @param links: links to vacancies that should be scrapped
        @param vacancy_titles: vacancies titles
        @param category_name: the name of category to which belongs given butch of vacancies
        """
        self.create_csv_headline(self.temp_vacancy_filename, self.temp_vacancy_fields)

        links_to_insert = [{'link': item[0], 'vacancy_title': item[1], 'is_scrapped': False, 'category': category_name,
                            'created_at': datetime.utcnow()} for item in zip(links, vacancy_titles)]

        with open(self.temp_vacancy_filename, mode='a+') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.temp_vacancy_fields)
            writer.writerows(links_to_insert)

    def load_category_links(self):
        """
        Needed for further collection of links to vacancies
        """
        links_to_categories = []
        category_names = []

        with open(self.temp_category_filename, "r") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                links_to_categories.append(row['link'])
                category_names.append(row['category_name'])
        return links_to_categories, category_names

    def load_categories_to_parse(self):
        """
        Fetch categories that have more than 0 not-scrapped vacancies
        """
        categories_to_parse = []

        with open(self.temp_vacancy_filename, "r") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row['is_scrapped'] == 'False' and row['category'] not in categories_to_parse:
                    categories_to_parse.append(row['category'])
        return categories_to_parse

    def load_category_vacancies(self, category):
        """
        Fetch all not-scrapped vacancies links for the given category
        """
        links_to_vacancies = []
        vacancy_titles = []

        with open(self.temp_vacancy_filename, "r") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row['is_scrapped'] == 'False' and row['category'] == category:
                    links_to_vacancies.append(row['link'])
                    vacancy_titles.append(row['vacancy_title'])
        return links_to_vacancies, vacancy_titles

    def update_vacancy_scrap_status(self, vacancy_link, vacancy_title, category):
        temp_file = NamedTemporaryFile(mode='w', delete=False)

        with open(self.temp_vacancy_filename, 'r') as csv_file, temp_file:
            reader = csv.DictReader(csv_file, fieldnames=self.temp_vacancy_fields)
            writer = csv.DictWriter(temp_file, fieldnames=self.temp_vacancy_fields)

            for row in reader:
                if row['link'] == vacancy_link and row['vacancy_title'] == vacancy_title and row['category'] == category:
                    row['is_scrapped'] = 'True'
                    row['scrapped_at'] = datetime.utcnow().strftime("%Y-%m-%d, %H:%M:%S")

                row = {'link': row['link'], 'vacancy_title': row['vacancy_title'], 'category': row['category'],
                       'is_scrapped': row['is_scrapped'], 'created_at': row['created_at'],
                       'scrapped_at': row['scrapped_at']}

                writer.writerow(row)

        shutil.move(temp_file.name, self.temp_vacancy_filename)
        print("vacancy status set to scrapped = True")

    def update_category_scrap_status(self, category):
        temp_file = NamedTemporaryFile(mode='w', delete=False)

        with open(self.temp_category_filename, 'r') as csv_file, temp_file:
            reader = csv.DictReader(csv_file, fieldnames=self.temp_category_fields)
            writer = csv.DictWriter(temp_file, fieldnames=self.temp_category_fields)
            for row in reader:
                if row['category_name'] == category:
                    row['is_scrapped'] = 'True'
                    row['scrapped_at'] = datetime.utcnow().strftime("%Y-%m-%d, %H:%M:%S")
                row = {'link': row['link'], 'category_name': row['category_name'], 'is_scrapped': row['is_scrapped'],
                       'created_at': row['created_at'], 'scrapped_at': row['scrapped_at']}
                writer.writerow(row)

        shutil.move(temp_file.name, self.temp_category_filename)
        print("category status set to scrapped = True")
