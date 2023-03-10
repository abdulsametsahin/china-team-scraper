import json
import time

from actions.scrape_company import ScrapeCompany
from multiprocessing import Process

from config import rabbitmq_config
import pika


def worker():
    while True:
        try:
            credentials = pika.PlainCredentials(
                rabbitmq_config['user'], rabbitmq_config['password'])
            parameters = pika.ConnectionParameters(
                host=rabbitmq_config['host'], port=rabbitmq_config['port'], credentials=credentials, heartbeat=120)
            connection = pika.BlockingConnection(parameters)
            consumer_channel = connection.channel()
            publisher_channel = connection.channel()

            queue_arguments = {
                'x-queue-mode': 'lazy', 'x-max-length': 100000, 'x-overflow': 'reject-publish'}
            consume_queue = consumer_channel.queue_declare(queue='company_link', durable=True,
                                                           arguments=queue_arguments)

            queue_arguments = {'x-queue-mode': 'lazy'}
            publish_queue = publisher_channel.queue_declare(queue='company_data', durable=True,
                                                            arguments=queue_arguments)

            consumer_channel.basic_qos(prefetch_count=1)
            for method_frame, properties, body in consumer_channel.consume(consume_queue.method.queue):
                url = f"https://www.gongsi.com.cn/detail/{body.decode('utf-8')}"
                scraper = ScrapeCompany(url)
                company_data = scraper.scrape()
                if company_data == 500:
                    company_data = None

                if company_data is not None:
                    publisher_channel.basic_publish(exchange='', routing_key=publish_queue.method.queue,
                                                    body=json.dumps(company_data))

                consumer_channel.basic_ack(
                    delivery_tag=method_frame.delivery_tag)

        except KeyboardInterrupt:
            print("[x] [ScrapeCompany] Closing connection")
            break
        except Exception as e:
            print(f"[x] [ScrapeCompany] Error: {e}")
            print("[x] [ScrapeCompany] Sleeping for 1 minute")
            time.sleep(60)


def run(workers):
    processes = []

    for i in range(workers):
        processes.append(Process(target=worker))

    for process in processes:
        process.start()


if __name__ == '__main__':
    # ask for the number of workers
    worker_count = int(input("How many workers do you want to run? "))
    print(
        f"[x] [ScrapeCompany] Running {worker_count} workers. Press CTRL+C to stop.")
    run(worker_count)
