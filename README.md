# Gongsi.com.cn Scraper


This scraper has been built by China team for Innoscripta Data Competition. It aims to scrape company data of Chinese companies through https://gongsi.com.tr


## How it works?

Here is a detailed flow

![image.png](assets/flow.png)


This scraper uses RabbitMQ to comminicate with master and workers. Thanks to RabbitMQ, **the scraper is highly scalable**.


There are 4 types of workers in this system.

* Search page generator
* Search page scraper
* Company scraper
* Company save

### Search page generator

There is a limit for the pagination. For non-registered users pagination limit is 100 and for registered users limit is 200. Since there are more than 200 pages of search result, we need to use filters to generate search result with less pages.

This generator is responsible for generating search pages. It generates search page and write link to "**search_page**" queue so that "Search page scraper" can scrape it.


### Search page scraper

This scraper, scrapes though all pages of the search result and writes company links onto "**company_link**" queue so that "Company scraper" can scrape them. We are not able to scrape more than 200 pages for every search result. This is the only scraper which needs authectication. Therefore there is another worker to generate valid cookies.


### Company scraper

This scraper comsumes company links from "company_link" queue. After scraping the company data, it writes the data as json onto "company_data" queue. More scraper, more data. Therefore its highly recommended to run many workers on each server. You are able to select number of workers for this scraper. Recommended number of workers are 15 for each server.


### Company saver

To avoid making queries at the same time, scraper uses queues to save data to database. If the company exists, it updates it.



## Installation

You need RabbitMQ and MySQL to run the scraper. You can use existing ones or you can run them by using docker and docker-compose.yml file in this repository.


## Requirements

* Pyhton3+ (Tested with 3.10)
* Docker


# How to run?

1. Clone the repository
2. Run docker-compose file by using `docker-compose up -d` command in the root folder.
3. copy config.example.py file to config.py with `cp config.example.py config.py` and edit content of the config file based on your MySQL and RabbitMQ configuration.
4. run master script with `python master.py`
5. run worker script with `python worker.py`

**You can run workers as many as you want. Once you have run master script, you can run workers from any server to scale the scraper**
