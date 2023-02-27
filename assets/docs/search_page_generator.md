# Search Page Generator Explained

This worker is running on master script. It is responsible for extrating company link from the search page and then passing it to the rabbitmq queue. There are 3 workers hard coded and you can change it [here](../actions/search_page_generator.py#L13).

## How it works

- If login is enabled, it will wait for a valid cookie stored in the storage/cookies.txt file. If the cookie is not valid, it will sleep for 5 secs and try again.
- It will then get task from the "search_page" queue. The task is a slug of the search page. For example, "bs1in52eyg5eyl6".
- If there are more than 200 pages, it will try to apply another filter and send it back to queue to reduce the number of pages.
- If there are less than 200 pages, it will extract the company links from the search page and send it to the "company_link" queue.
- To prevent overloading the queue, if number of tasks in "company_link" queue is more than 100k, it will sleep for 15 mins and continue when the number of tasks decreases to a safe level.
