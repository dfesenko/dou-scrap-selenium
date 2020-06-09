import csv

from pymongo import MongoClient
from typing import List
from datetime import datetime


def write_result_to_csv(is_headline=False, category=None, title=None, company=None, location=None, date=None, url=None):
    """
    Writes the scrapped data to CSV file
    @param is_headline: If the CSV file is new and empty - write the first row with the names of columns.
                        In this case all other parameters shouldn't be passed to the function.
    @param category: scrapped category of the vacancy
    @param title: scrapped title of the vacancy
    @param company: scrapped company name
    @param location: scrapped location of the job
    @param date: scrapped date of vacancy posting
    @param url: url to the vacancy
    """
    fieldnames = ['category', 'title', 'company', 'location', 'date', 'url']
    with open('jobs2.csv', mode='a+') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if is_headline:
            writer.writeheader()
        else:
            writer.writerow({'category': category, 'title': title, 'company': company,
                             'location': location, 'date': date, 'url': url})


def write_result_to_mongo(category, title, company, location, date, url):
    """
    Writes the scrapped data to MongoDB database collection.
    @param category: scrapped category of the vacancy
    @param title: scrapped title of the vacancy
    @param company: scrapped company name
    @param location: scrapped location of the job
    @param date: scrapped date of vacancy posting
    @param url: url to the vacancy
    """
    client = MongoClient('localhost', 27017)
    db = client['dou-scrapping-db']

    collection = db['dou-jobs-data']
    doc_to_insert = {'category': category, 'title': title, 'company': company,
                     'location': location, 'date': date, 'url': url}
    collection.insert_one(doc_to_insert)


def insert_plan_into_csv(links: List[str], links_info: List[str], iteration,
                         is_categories=None, is_vacancies=None, category_name=None):
    """
    Inserts items that should be scrapped in the future to the CSV file.

    @param links: links to items that should be scrapped
    @param links_info: description of an item (name of category or vacancy title, for example)
    @param iteration: the num of time the function is called (0, 1, 2, 3, ..., N)
    @param is_categories: flag for categories
    @param is_vacancies: flag for vacancies
    @param category_name: the name of category (if is_vacancies = True)
    """
    if is_categories and is_vacancies:
        raise Exception("insert_plan_into_csv() function can insert just 1 type of content at a time")
    elif not is_categories and not is_vacancies:
        raise Exception("insert_plan_into_csv() function expects a flag of what is the kind of the content to insert")
    elif is_vacancies and not category_name:
        raise Exception("The name of category the vacancies belongs to should be passed")

    kind = 'category' if is_categories else 'vacancy'

    if is_vacancies:
        fieldnames = ['category', 'vacancy_title', 'is_scrapped', 'created_at', 'link']
        links_to_insert = [{'link': item[0], 'vacancy_title': item[1], 'is_scrapped': False, 'category': category_name,
                            'created_at': datetime.utcnow()} for item in zip(links, links_info)]
    elif is_categories:
        fieldnames = ['category_name', 'is_scrapped', 'created_at', 'link']
        links_to_insert = [{'link': item[0], 'category_name': item[1], 'is_scrapped': False,
                            'created_at': datetime.utcnow()} for item in zip(links, links_info)]

    with open(f'{kind}-links-to-process.csv', mode='a+') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if iteration == 0:
            writer.writeheader()
            writer.writerows(links_to_insert)
        else:
            writer.writerows(links_to_insert)


def insert_plan_into_mongodb(links: List[str], links_info: List[str],
                             is_categories=None, is_vacancies=None, category_name=None):
    """
    Inserts items that should be scrapped in the future into the MongoDB database.

    @param links: links to items that should be scrapped
    @param links_info: description of an item (name of category or vacancy title, for example)
    @param is_categories: flag for categories
    @param is_vacancies: flag for vacancies
    @param category_name: the name of category (if is_vacancies = True)
    """
    if is_categories and is_vacancies:
        raise Exception("insert_plan_into_mongodb() function can insert just 1 type of content at a time")
    elif not is_categories and not is_vacancies:
        raise Exception("insert_plan_into_mongodb() function expects a flag of what is the kind of "
                        "the content to insert")
    elif is_vacancies and not category_name:
        raise Exception("The name of category the vacancies belongs to should be passed")

    client = MongoClient('localhost', 27017)
    db = client['dou-scrapping-db']

    kind = 'category' if is_categories else 'vacancy'
    collection = db[f'{kind}-links-to-process']

    if is_vacancies:
        links_to_insert = [{'link': item[0], 'vacancy_title': item[1], 'is_scrapped': False, 'category': category_name,
                            'created_at': datetime.utcnow()} for item in zip(links, links_info)]
    elif is_categories:
        links_to_insert = [{'link': item[0], 'category_name': item[1], 'is_scrapped': False,
                            'created_at': datetime.utcnow()} for item in zip(links, links_info)]

    collection.insert_many(links_to_insert)


def store_temp_data(temp_storage_type, links, links_info, iteration,
                    is_categories=None, is_vacancies=None, category_name=None):
    """
    Decides which storage platform to choose (csv file or MongoDB) and whether it is category or vacancy data
    """
    if is_categories and is_vacancies:
        raise Exception("store_temp_data() function can process just 1 type of content at a time")

    if is_vacancies and not category_name:
        raise Exception("Specify the name of the category")

    if temp_storage_type == 'csv' and is_categories:
        insert_plan_into_csv(links=links, links_info=links_info, iteration=0, is_categories=True)

    elif temp_storage_type == 'csv' and is_vacancies:
        insert_plan_into_csv(links=links, links_info=links_info, iteration=iteration, is_vacancies=True,
                             category_name=category_name)

    elif temp_storage_type == 'mongo' and is_categories:
        insert_plan_into_mongodb(links=links, links_info=links_info, is_categories=True)

    elif temp_storage_type == 'mongo' and is_vacancies:
        insert_plan_into_mongodb(links=links, links_info=links_info, is_vacancies=True, category_name=category_name)


def load_category_links(storage_type):
    links_to_categories = []
    category_names = []

    if storage_type == 'csv':
        with open('category-links-to-process.csv', "r") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                links_to_categories.append(row['link'])
                category_names.append(row['category_name'])

    elif storage_type == 'mongo':
        client = MongoClient('localhost', 27017)
        db = client['dou-scrapping-db']
        collection = db['category-links-to-process']

        for item in collection.find({"is_scrapped": False}):
            links_to_categories.append(item['link'])
            category_names.append(item['category_name'])

    return links_to_categories, category_names


def update_scrap_status(vacancy_link, vacancy_title, storage_type):
    if storage_type == 'mongo':
        client = MongoClient('localhost', 27017)
        db = client['dou-scrapping-db']
        collection = db['vacancy-links-to-process']

        query = {'link': vacancy_link, 'vacancy_title': vacancy_title}

        collection.update_one(query, {"$set": {"is_scrapped": True}})


def load_categories_to_parse():
    client = MongoClient('localhost', 27017)
    db = client['dou-scrapping-db']
    collection = db['vacancy-links-to-process']
    return collection.distinct("category", {"is_scrapped": False})


def load_category_vacancies(category):
    client = MongoClient('localhost', 27017)
    db = client['dou-scrapping-db']
    collection = db['vacancy-links-to-process']

    links_to_vacancies = []
    vacancy_titles = []

    for item in collection.find({"category": category, "is_scrapped": False}):
        links_to_vacancies.append(item['link'])
        vacancy_titles.append(item['vacancy_title'])

    return links_to_vacancies, vacancy_titles


def update_category_scrap_status(category):
    client = MongoClient('localhost', 27017)
    db = client['dou-scrapping-db']
    collection = db['category-links-to-process']
    query = {"category_name": category}

    collection.update_one(query, {"$set": {"is_scrapped": True, "datetime_scrapped": datetime.utcnow()}})
