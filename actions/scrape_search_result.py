import json
import os
import time

import requests

from config import rabbitmq_config
import pika
from multiprocessing import Process
from bs4 import BeautifulSoup


class ScrapeSearchResult:
    def __init__(self):
        self.worker_count = 3
        self.max_message_count = 30000
        self.execute()

    def execute(self):
        processes = []
        for i in range(self.worker_count):
            processes.append(Process(target=self.worker))

        for process in processes:
            process.start()

    def get_with_cookie(self, url):
        session = requests.session()
        cookie_file = './storage/cookies.txt'

        if not os.path.exists(cookie_file):
            print("Cookie file not found, waiting for 5 seconds")
            time.sleep(5)

        with open(cookie_file, 'r') as f:
            cookie = json.load(f)

        session.cookies = requests.utils.cookiejar_from_dict(cookie)
        return session.get(url)

    def worker(self):
        while True:
            try:
                credentials = pika.PlainCredentials(rabbitmq_config['user'], rabbitmq_config['password'])
                parameters = pika.ConnectionParameters(
                    host=rabbitmq_config['host'], port=rabbitmq_config['port'], credentials=credentials, heartbeat=5)
                connection = pika.BlockingConnection(parameters)
                consumer_channel = connection.channel()
                publisher_channel = connection.channel()
                self.scrape(consumer_channel, publisher_channel)
                consumer_channel.close()
                publisher_channel.close()
                connection.close()
                print("[x] [ScrapeSearchResult] Sleeping for 15 minutes")
                time.sleep(60 * 15)
            except Exception as e:
                print(f"[x] [ScrapeSearchResult] Error: {e}")
                print("[x] [ScrapeSearchResult] Sleeping for 1 minute")
                time.sleep(60)

    def scrape(self, consumer_channel, publisher_channel):
        print("[x] [ScrapeSearchResult] Checking tasks queue")
        queue_arguments = {'x-queue-mode': 'lazy'}
        consumer_channel.queue_declare(queue='search_page', durable=True, arguments=queue_arguments)
        publisher_queue = publisher_channel.queue_declare(queue='company_link', durable=True, arguments=queue_arguments)

        if publisher_queue.method.message_count > self.max_message_count:
            print(f"[x] [ScrapeSearchResult] Message count is too large, stop consuming")
            return

        consumer_channel.basic_qos(prefetch_count=1)

        print("[x] [ScrapeSearchResult] Consuming tasks")
        for method_frame, properties, body in consumer_channel.consume('search_page', auto_ack=False):
            print(f"[x] [ScrapeSearchResult] Consumed task: {body}")
            url = f"https://www.gongsi.com.cn/search/{body.decode('utf-8')}"

            response = self.get_with_cookie(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            result_count = soup.select_one('.select-result span')
            if result_count is None or int(result_count.text.replace('+', '')) == 0:
                print("[x] [ScrapeSearchResult] No result")
                return

            page_count = soup.select_one('.page-count')
            if page_count:
                page_count = int(page_count.text.split(' ')[1].split(' ')[0])
                if page_count > 200:
                    print(f"[x] [ScrapeSearchResult] Page count is too large ({page_count}), set to 200")
                    page_count = 200
            else:
                page_count = 1

            print(f"[x] [ScrapeSearchResult] Page count: {page_count}")

            current_page = 1
            while current_page <= page_count:
                for company in soup.select('.list-body-title a'):
                    uuid = company['href'].split('/')[-1]
                    publisher_channel.basic_publish(exchange='', routing_key='company_link',
                                                    body=uuid.encode('utf-8'),
                                                    properties=pika.BasicProperties(delivery_mode=2))
                current_page += 1
                response = self.get_with_cookie(f"{url}pg{current_page}")
                soup = BeautifulSoup(response.text, 'html.parser')

            consumer_channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            print(f"[x] [ScrapeSearchResult] Task completed: {body}")

            if publisher_queue.method.message_count > self.max_message_count:
                print(f"[x] [ScrapeSearchResult] Message count is too large, stop consuming")
                consumer_channel.stop_consuming()