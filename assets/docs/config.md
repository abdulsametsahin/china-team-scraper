# Config File Explained

## rabbitmq_config

- host: RabbitMQ host
- port: RabbitMQ port
- username: RabbitMQ username
- password: RabbitMQ password

## mysql_config

- host: MySQL host
- port: MySQL port
- username: MySQL username
- password: MySQL password
- database: MySQL database name
- save_workers: Number of save workers, 1 is enough

## gongsi_config

- province_count: Number of provinces in the website
- category_count: Number of categories in the website
- enterprise_type_count: Number of enterprise types in the website
- phone_number: Phone number to use for login
- password: Password to use for login

## exchange_rates

> These will be used to convert the currency of the company to yuan.

- usd_to_yuan: USD to CNY exchange rate
- eur_to_yuan: EUR to CNY exchange rate
