from actions.generate_search_result import GenerateSearchResult
from actions.generate_cookie import GenerateCookie
from actions.scrape_search_result import ScrapeSearchResult
from actions.save_company import SaveCompany
from multiprocessing import Process

from config import mysql_config, gongsi_config


def run():
    processes = [
        Process(target=GenerateSearchResult),
        Process(target=ScrapeSearchResult),
    ]

    if not gongsi_config['disable_login']:
        processes.append(Process(target=GenerateCookie))

    for i in range(mysql_config['save_workers']):
        processes.append(Process(target=SaveCompany))

    for process in processes:
        process.start()


if __name__ == '__main__':
    print("Starting processes")
    run()
