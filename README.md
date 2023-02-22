# Gongsi.com.cn Scraper


This scraper was built by **China Team** for the Innoscripta Data Competition. Its purpose is to scrape data of Chinese companies from [https://www.gongsi.com.cn](https://gongsi.com.cn/).

## How it works?

Here is a detailed flow

![image.png](assets/flow.png)




This scraper utilizes RabbitMQ for communication between the master and workers, enabling it to be highly scalable.

The system is comprised of four different types of workers:

* Search page generator
* Search page scraper
* Company scraper
* Company save worker.

#### Search page generator

There is a pagiation limit in place for this system. Non-registered users have a limit of 100 pages, while registered users have a limit of 200 pages. Given that there are more than 200 pages of search results, filters must be applied to generate search results with fewer pages.

The search page generator is responsible for generating search pages and writing the links to the "**search\_page**" queue, which is then scraped by the "Search page scraper" worker.


#### Search page scraper

This scraper, scrapes though all pages of the search result and writes company links onto "**company_link**" queue so that "Company scraper" can scrape them. We are not able to scrape more than 200 pages for every search result. This is the only scraper which needs authectication. Therefore there is another worker to generate valid cookies.


#### Company scraper

The scraper is designed to scrape through all pages of the search results and write the company links onto the "**company\_link**" queue, which are then scraped by the "Company scraper" worker. However, it is not possible to scrape more than 200 pages for each search result. Additionally, this is the only scraper that requires authentication, which is why there is another worker responsible for generating valid cookies.


#### Company saver

To prevent simultaneous queries, the scraper utilizes queues to store data in the database. If a company already exists in the database, it will be updated.


## Installation

Running the scraper requires both RabbitMQ and MySQL. You can use existing installations or run them using Docker and the `docker-compose.yml` file provided in this repository.


## Requirements

* Pyhton3+ (Tested with 3.10)
* Docker


## How to run?

1. Clone the repository
2. To run the Docker Compose file, navigate to the root folder of the project in your terminal and use the command `docker-compose up -d`. This will start the RabbitMQ and MySQL services in detached mode.
3. To configure the scraper, copy the `config.example.py` file to `config.py` using the command `cp config.example.py config.py`. Then, edit the contents of the `config.py` file to reflect your MySQL and RabbitMQ configurations.
4. To run the master script, use the command `python master.py` in your terminal. This will initiate the scraping process and coordinate communication between the various workers.
5. To run the worker script, use the command `python worker.py` in your terminal. This will start the worker process and enable it to receive and process tasks from the RabbitMQ message queue.

**You can run as many workers as you need to scale the scraper. Once you have initiated the master script, you can run workers from any server and they will be able to communicate with the master process through the RabbitMQ message queue. This enables you to easily scale the scraper to handle larger workloads.**
