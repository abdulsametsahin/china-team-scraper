from actions.generate_search_result import GenerateSearchResult
from actions.generate_cookie import GenerateCookie
from actions.scrape_search_result import ScrapeSearchResult
from actions.save_company import SaveCompany
from multiprocessing import Process


def run():
    processes = [
        Process(target=GenerateSearchResult),
        Process(target=GenerateCookie),
        Process(target=ScrapeSearchResult),
        Process(target=SaveCompany),
    ]

    for process in processes:
        process.start()


if __name__ == '__main__':
    print("Starting processes")
    run()
