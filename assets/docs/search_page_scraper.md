# Search Page Scraper Explained

This worker is a part of the master script and is responsible for extracting company links from search pages and passing them to the rabbitmq queue. The number of workers is currently set to 3, but this value can be modified in the "scrape_search_results.py" file on line 16.

If the login feature is enabled, the worker will wait for a valid cookie stored in the "storage/cookies.txt" file. If the cookie is not valid, the worker will sleep for 5 seconds and try again.

Next, the worker will retrieve a task from the "search_page" queue, which is a unique identifier for a particular search page, such as "bs1in52eyg5eyl6".

If there are more than 200 pages in the search results, the worker will attempt to apply additional filters and send the task back to the queue to reduce the number of pages. If there are less than 200 pages, the worker will extract the company links from the search page and send them to the "company_link" queue.

To avoid overwhelming the queue, the worker will check if the number of tasks in the "company_link" queue exceeds 100,000. If it does, the worker will sleep for 15 minutes before resuming its work once the number of tasks in the queue has decreased to a safe level.
