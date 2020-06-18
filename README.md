# dou-scrap-selenium
The system for collection of jobs data 
from the https://jobs.dou.ua/ website (using Selenium).

## About
The system collects the following data about vacancies:

* Category of the job (for example, "Python", "Java", etc.)
* Job title
* Company name
* Location
* Date
* URL

It is possible to run the system in full mode or by steps:
1) Collect links to job categories available on the website.
2) Collect links to job openings for each category.
3) Collect vacancy data using the links collected on step 2.

There are two possible destinations for storing data: MongoDB 
database and CSV file. Users can choose the place where they want
to store temporary and final outputs of the system.

## Technologies
* Selenium 3.141.0
* MongoDB 4.2.7

## How to install
1. Clone the repo: 
`git clone https://github.com/dfesenko/dou-scrap-selenium.git`. 
Go inside the `dou-scrap-selenium` folder: `cd dou-scrap-selenium`.
2. Create a virtual environment: `python -m venv venv`.
3. Activate virtual environment: `source venv/bin/activate`.
4. Install dependencies into the virtual environment: 
`pip install -r requirements.txt`.
5. Provide the path to the WebDriver in `config.py` file (you should
install webdriver first). For example, you can download WebDriver for 
Chrome here - https://chromedriver.chromium.org/downloads .
6. Specify the type of temporary and destination storages in 
`config.py` file (variables TEMP_STORAGE and DESTINATION). There are 
two possible options: `mongo` and `csv`. 
7. Now the system is ready for using.

## How to run
To run in full mode, execute the file `run.py`:  
`python run.py`

You can also run the system by steps:
1. Collect links to categories:  
`python scrap_categories_links.py`

2. Collect links to vacancies:  
`python scrap_vacancies_links.py`

3. Collect vacancies data:  
`python scrap_vacancy_data.py`

`scrap_categories_links.py` and `python scrap_vacancies_links.py` 
scripts store temporary data in MongoDB or CSV file.

`run.py` and `scrap_vacancy_data.py` scripts store temporary and/or
final data in MongoDB or CSV file.

The type of storage can be set in `config.py` file.

