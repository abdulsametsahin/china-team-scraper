import time

import pika

from config import rabbitmq_config, gongsi_config


class GenerateSearchResult:
    def __init__(self):
        self.execute()

    def execute(self):
        while True:
            print(rabbitmq_config)
            try:
                credentials = pika.PlainCredentials(rabbitmq_config['user'], rabbitmq_config['password'])
                parameters = pika.ConnectionParameters(
                    host=rabbitmq_config['host'], port=rabbitmq_config['port'], credentials=credentials, heartbeat=5)
                connection = pika.BlockingConnection(parameters)
                channel = connection.channel()
                self.generate(channel)
                channel.close()
                connection.close()
                print("[x] [GenerateSearchResult] Sleeping for 1 hour")
                time.sleep(60 * 60)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)

    def generate(self, channel):
        print("[x] [GenerateSearchResult] Checking tasks queue")
        queue_arguments = {'x-queue-mode': 'lazy'}
        queue = channel.queue_declare(queue='search_page', durable=True, arguments=queue_arguments)

        if queue.method.message_count > 0:
            print("[x] [GenerateSearchResult] Tasks queue is not empty")
            return

        province_count = gongsi_config['province_count']
        category_count = gongsi_config['category_count']
        enterprise_type_count = gongsi_config['enterprise_type_count']

        established_year_ranges = [
            "0-1",
            "1-2",
            "2-3",
            "3-5",
            "5-7",
            "7-10",
            "10-13",
            "13-16",
            "16-19",
            "19-22",
            "22-30",
            "30-45",
            "45-70",
            "70-100",
        ]

        print("[x] [GenerateSearchResult] Generating search results pages")
        for province_id in range(1, province_count + 1):
            for category_id in range(1, category_count + 1):
                for eyr_id in range(len(established_year_ranges)):
                    eyr = established_year_ranges[eyr_id].split("-")
                    url = f"bs{province_id}in{category_id}eyg{eyr[0]}eyl{eyr[1]}st1"
                    try:
                        channel.basic_publish(
                            exchange='', routing_key='search_page', body=url,
                            properties=pika.BasicProperties(delivery_mode=2))
                    except Exception as e:
                        print(f"Error: {e}")
                        pass

        print("[x] [GenerateSearchResult] Done")
