# Config File Explained

## rabbitmq_config
> Simple RabbitMQ configuration
- host: RabbitMQ host
- port: RabbitMQ port
- username: RabbitMQ username
- password: RabbitMQ password

## mysql_config
> Simple MySQL configuration
- host: MySQL host
- port: MySQL port
- username: MySQL username
- password: MySQL password
- database: MySQL database name
- save_workers: Number of save workers, 1 is enough
> Note: The number of save workers can be increased to speed up the saving process. However, this will increase the load on the database.

## gongsi_config
> province_count, category_count, enterprise_type_count are used to generate search pages. You can find them in the website.
- province_count: Number of provinces in the website
- category_count: Number of categories in the website
- enterprise_type_count: Number of enterprise types in the website
- phone_number: Phone number to use for login
- password: Password to use for login

## exchange_rates

> These will be used to convert the currency of the company to yuan.

- usd_to_yuan: USD to CNY exchange rate
- eur_to_yuan: EUR to CNY exchange rate
