import json
import sys
import time
from urllib.parse import urlparse

import pika
import pymysql.cursors
import uuid
import datetime

from config import mysql_config, rabbitmq_config


class SaveCompany:
    def __init__(self):
        self.cnx = None
        self.company_data = None

        while True:
            try:
                self.work()
            except Exception as e:
                print(f"[x] [SaveCompany] Error: {e}")
                print("[x] [SaveCompany] Sleeping for 1 minute")
                time.sleep(60)

    def work(self):
        credentials = pika.PlainCredentials(
            rabbitmq_config['user'], rabbitmq_config['password'])
        parameters = pika.ConnectionParameters(
            host=rabbitmq_config['host'], port=rabbitmq_config['port'], credentials=credentials, heartbeat=5)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='company_data', durable=True, arguments={
                              'x-queue-mode': 'lazy'})

        print("[x] [SaveCompany] Waiting for messages")

        channel.basic_qos(prefetch_count=1)

        for method_frame, properties, body in channel.consume('company_data'):
            # print(f"[x] [SaveCompany] Received message {method_frame.delivery_tag}")
            self.cnx = pymysql.connect(
                user=mysql_config['user'], password=mysql_config['password'], host=mysql_config['host'],
                port=int(mysql_config['port']), database=mysql_config['database'], charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
            self.company_data = json.loads(body.decode('utf-8'))
            self.clean_data()
            self.save()
            channel.basic_ack(method_frame.delivery_tag)

    def clean_data(self):
        for key in self.company_data['basic_info']:
            if self.company_data['basic_info'][key] == '-':
                self.company_data['basic_info'][key] = None

        for key in self.company_data['details']:
            if self.company_data['details'][key] == '-':
                self.company_data['details'][key] = None

        for i in range(len(self.company_data['changes'])):
            for key in self.company_data['changes'][i]:
                if self.company_data['changes'][i][key] == '-':
                    self.company_data['changes'][i][key] = None

        for year in self.company_data['annual_reports']:
            for key in self.company_data['annual_reports'][year]:
                if self.company_data['annual_reports'][year][key] in ['-', '无', '企业选择不公示', '个体户选择不公示',
                                                                      '个体工商户选择不公示']:
                    self.company_data['annual_reports'][year][key] = None
                if self.company_data['annual_reports'][year][key] == '无':
                    self.company_data['annual_reports'][year][key] = None

    def doesnt_contain_numbers(self, string):
        if string is None:
            return True

        for char in string:
            if char.isdigit():
                return False

        return True

    def get_money(self, string):
        if self.doesnt_contain_numbers(string):
            return None

        is_eur = False
        is_usd = False

        if '欧元' in string:
            is_eur = True

        if '美元' in string:
            is_usd = True

        string = string.strip()
        string = string.replace('元', '')
        multiplier = 1

        if '万' in string:
            multiplier = 10000

        if '亿' in string:
            multiplier = 100000000

        if '千' in string:
            multiplier = 1000

        string = string.replace('万', '')
        string = string.replace('亿', '')
        string = string.replace('千', '')

        string = string.split('（')[0]
        string = ''.join([c for c in string if c.isdigit() or c == '.'])

        amount = float(string) * multiplier

        currency = 'CNY'
        if is_eur:
            currency = 'EUR'
        if is_usd:
            currency = 'USD'

        return (amount, currency)

    def get_num(self, string):
        if self.doesnt_contain_numbers(string):
            return None

        # remove all non-numeric characters
        string = ''.join([char for char in string if char.isdigit()])

        return float(string)

    def get_provice(self, address):
        if address is None:
            return None

        provinces = ["北京市", "天津市", "河北省", "山西省", "内蒙古自治区", "辽宁省", "吉林省", "黑龙江省", "上海市", "江苏省", "浙江省", "安徽省", "福建省", "江西省", "山东省", "河南省", "湖北省", "湖南省",
                     "广东省", "广西壮族自治区", "海南省", "重庆市", "四川省", "贵州省", "云南省", "西藏自治区", "陕西省", "甘肃省", "青海省", "宁夏回族自治区", "新疆维吾尔自治区", "台湾省", "香港特别行政区", "澳门特别行政区"]

        for province in provinces:
            if province in address:
                return province

        return None

    def get_host(self, url):
        if url is None:
            return None

        return urlparse(url).netloc

    def save(self, retry=0):
        # update if exists, insert if not
        try:
            phone = self.company_data['basic_info']['phone']

            registered_capital = self.get_money(
                self.company_data['details']['注册资本'])

            paid_in_capital = self.get_money(
                self.company_data['details']['实缴资本'])

            if phone is not None:
                phone = phone.split(';')[0]
            company = {
                'id': self.company_data['basic_info']['uuid'],
                'title': self.company_data['basic_info']['title'],
                'phone': phone,
                'email': self.company_data['basic_info']['email'],
                'website': self.get_host(self.company_data['basic_info']['website'][:99]) if self.company_data['basic_info']['website'] is not None else None,
                'ceo': self.company_data['details']['法定代表人'],
                'registered_capital': registered_capital[0] if registered_capital is not None else None,
                'registered_capital_currency': registered_capital[1] if registered_capital is not None else None,
                'date_of_establishment': None if self.company_data['details']['成立日期'] == '-' else
                self.company_data['details']['成立日期'],
                'operating_status': self.company_data['details']['经营状态'],
                'registration_number': self.company_data['details']['工商注册号'],
                'social_credit_code': self.company_data['details']['统一社会信用代码'],
                'organization_code': self.company_data['details']['组织机构代码'],
                'tax_registration_number': self.company_data['details']['纳税人识别号'],
                'company_type': self.company_data['details']['公司类型'],
                'operating_period': self.company_data['details']['营业期限'],
                'industry': self.company_data['details']['行业'],
                'taxpayer_qualification': self.company_data['details']['纳税人资质'],
                'approval_date': None if self.company_data['details']['核准日期'] == '-' else
                self.company_data['details']['核准日期'],
                'paid_in_capital': paid_in_capital[0] if paid_in_capital is not None else None,
                'paid_in_capital_currency': paid_in_capital[1] if paid_in_capital is not None else None,
                'staff_size': self.company_data['details']['人员规模'],
                'insured_staff_size': self.company_data['details']['参保人数'],
                'registration_authority': self.company_data['details']['登记机关'],
                'english_name': self.company_data['details']['英文名称'],
                'registered_address': self.company_data['details']['注册地址'],
                'province': self.get_provice(self.company_data['details']['注册地址']),
                'business_scope': self.company_data['details']['经营范围'],
                'updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # update if exists, insert if not
            with self.cnx:
                with self.cnx.cursor() as cursor:
                    sql = "SELECT * FROM companies WHERE id = '%s'" % (
                        company['id'])
                    cursor.execute(sql)
                    result = cursor.fetchone()
                    if not result:
                        # print(f"[x] [SaveCompany] Inserting {company['id']} into database")
                        query = """
                            INSERT INTO companies(id, title, phone, email, website, ceo, registered_capital, registered_capital_currency, date_of_establishment, operating_status, registration_number, social_credit_code, organization_code, tax_registration_number, company_type, operating_period, industry, taxpayer_qualification, approval_date, paid_in_capital,paid_in_capital_currency, staff_size, insured_staff_size, registration_authority, english_name, registered_address, province, business_scope, updated_at)
                            VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s, %s, %s, %s,%s, %s,%s, %s, %s, %s, %s, %s)
                        """
                        try:
                            cursor.execute(query, (
                                company['id'], company['title'], company['phone'], company['email'], company['website'],
                                company['ceo'], company['registered_capital'], company[
                                    'registered_capital_currency'], company['date_of_establishment'],
                                company['operating_status'], company['registration_number'], company['social_credit_code'],
                                company['organization_code'], company['tax_registration_number'],
                                company['company_type'], company['operating_period'], company['industry'],
                                company['taxpayer_qualification'], company['approval_date'], company[
                                    'paid_in_capital'], company['paid_in_capital_currency'],
                                company['staff_size'], company['insured_staff_size'], company['registration_authority'],
                                company['english_name'], company['registered_address'], company['province'],
                                company['business_scope'], company['updated_at']))
                        except Exception as e:
                            time.sleep(1)
                            if retry < 2:
                                self.save(retry=retry+1)
                                return
                            else:
                                print(f"[x] [SaveCompany] Error: {e}")

                    else:
                        # print(f"[x] [SaveCompany] Updating {company['id']} in database")
                        query = """
                            UPDATE companies SET title = %s, phone = %s, email = %s, website = %s, ceo = %s, registered_capital = %s, registered_capital_currency = %s, date_of_establishment = %s, operating_status = %s, registration_number = %s, social_credit_code = %s, organization_code = %s, tax_registration_number = %s, company_type = %s, operating_period = %s, industry = %s, taxpayer_qualification = %s, approval_date = %s, paid_in_capital = %s,paid_in_capital_currency = %s, staff_size = %s, insured_staff_size = %s, registration_authority = %s, english_name = %s, registered_address = %s, province = %s, business_scope = %s, updated_at = %s
                            WHERE id = %s
                        """
                        cursor.execute(query, (
                            company['title'], company['phone'], company['email'], company['website'], company['ceo'],
                            company['registered_capital'], company['registered_capital_currency'], company['date_of_establishment'],
                            company['operating_status'],
                            company['registration_number'], company['social_credit_code'], company['organization_code'],
                            company['tax_registration_number'],
                            company['company_type'], company['operating_period'], company['industry'],
                            company['taxpayer_qualification'], company['approval_date'], company['paid_in_capital'],
                            company['paid_in_capital_currency'],
                            company['staff_size'], company['insured_staff_size'], company['registration_authority'],
                            company['english_name'], company['registered_address'], company['province'],
                            company['business_scope'], company['id'], company['updated_at']))

                    for table in ['annual_reports', 'branches', 'shareholders', 'main_staff', 'foreign_investments',
                                  'changes']:
                        sql = "DELETE FROM %s WHERE company = '%s'" % (
                            table, company['id'])
                        cursor.execute(sql)

                    for year in self.company_data['annual_reports']:
                        report = self.company_data['annual_reports'][year]

                        total_assets = self.get_money(report['资产总额'])
                        total_owner_equity = self.get_money(report['所有者权益合计'])
                        total_sales = self.get_money(report['销售总额'])
                        total_profit = self.get_money(report['利润总额'])
                        income_in_total = self.get_money(
                            report['营业总收入中主营业务收入'])
                        net_profit = self.get_money(report['利润总额'])
                        total_tax = self.get_money(report['纳税总额'])
                        total_liabilities = self.get_money(report['负债总额'])

                        annual_report = {
                            'id': uuid.uuid4(),
                            'year': int(year),
                            'business_status': report['企业经营状态'],
                            'number_of_employees': self.get_num(report['从业人数'].split(' ')[0]) if report['从业人数'] else None,
                            'email': report['电子邮箱'],
                            'zip_code': report['邮政编码'],
                            'address': report['企业通信地址'],
                            'email': report['电子邮箱'],
                            'total_assets': total_assets[0] if total_assets else None,
                            'total_assets_currency': total_assets[1] if total_assets else None,
                            'total_owner_equity': total_owner_equity[0] if total_owner_equity else None,
                            'total_owner_equity_currency': total_owner_equity[1] if total_owner_equity else None,
                            'total_sales': total_sales[0] if total_sales else None,
                            'total_sales_currency': total_sales[1] if total_sales else None,
                            'total_profit': total_profit[0] if total_profit else None,
                            'total_profit_currency': total_profit[1] if total_profit else None,
                            'income_in_total': income_in_total[0] if income_in_total else None,
                            'income_in_total_currency': income_in_total[1] if income_in_total else None,
                            'net_profit': net_profit[0] if net_profit else None,
                            'net_profit_currency': net_profit[1] if net_profit else None,
                            'total_tax': total_tax[0] if total_tax else None,
                            'total_tax_currency': total_tax[1] if total_tax else None,
                            'total_liabilities': total_liabilities[0] if total_liabilities else None,
                            'total_liabilities_currency': total_liabilities[1] if total_liabilities else None,
                            'company': company['id'],
                        }

                        query = """
                            INSERT INTO annual_reports (id, year, business_status, number_of_employees, email, zip_code, address, total_assets, total_assets_currency, total_owner_equity, total_owner_equity_currency, total_sales, total_sales_currency, total_profit, total_profit_currency, income_in_total, income_in_total_currency, net_profit, net_profit_currency, total_tax, total_tax_currency, total_liabilities, total_liabilities_currency, company)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """
                        cursor.execute(query, (
                            annual_report['id'], annual_report['year'], annual_report['business_status'],
                            annual_report['number_of_employees'], annual_report['email'], annual_report['zip_code'],
                            annual_report['address'], annual_report['total_assets'], annual_report['total_assets_currency'],
                            annual_report['total_owner_equity'], annual_report['total_owner_equity_currency'],
                            annual_report['total_sales'], annual_report['total_sales_currency'],
                            annual_report['total_profit'], annual_report['total_profit_currency'],
                            annual_report['income_in_total'], annual_report['income_in_total_currency'],
                            annual_report['net_profit'], annual_report['net_profit_currency'],
                            annual_report['total_tax'], annual_report['total_tax_currency'],
                            annual_report['total_liabilities'], annual_report['total_liabilities_currency'],
                            annual_report['company']))

                    for branch in self.company_data['branches']:
                        branch = {
                            'id': uuid.uuid4(),
                            'company': company['id'],
                            'name': branch['name'],
                            'person': None if branch['person'] == "-" else branch['person'],
                            'date': None if branch['date'] == "-" else branch['date'],
                            'status': None if branch['status'] == "-" else branch['status'],
                        }

                        query = """
                            INSERT INTO branches(id, company, name, person, date, status)
                            VALUES (%s,%s,%s,%s,%s,%s)
                        """
                        cursor.execute(query, (branch['id'], branch['company'], branch['name'],
                                               branch['person'], branch['date'], branch['status']))

                    for shareholder in self.company_data['shareholders']:
                        if shareholder['ratio'] == '-':
                            shareholder['ratio'] = None

                        ratio = float(shareholder['ratio'].replace(
                            '%', '')) if shareholder['ratio'] else None
                        capital = self.get_money(shareholder['capital'].split(' ')[
                                                 0]) if shareholder['capital'] else None
                        shareholder = {
                            'id': uuid.uuid4(),
                            'company': company['id'],
                            'name': shareholder['name'],
                            'ratio': ratio,
                            'capital': capital[0] if capital else None,
                            'capital_currency': capital[1] if capital else None,
                            'date': None if shareholder['date'] == "-" or len(shareholder['date']) < 1 else shareholder[
                                'date'],
                        }

                        query = """
                            INSERT INTO shareholders(id, company, name, ratio, capital, capital_currency, date)
                            VALUES (%s,%s,%s,%s,%s,%s,%s)
                        """
                        cursor.execute(query, (shareholder['id'], shareholder['company'], shareholder['name'],
                                               shareholder['ratio'], shareholder['capital'], shareholder['capital_currency'], shareholder['date']))

                    for staff in self.company_data['main_staff']:
                        positions = staff['position'].split(',')
                        for position in positions:
                            position_sql = "SELECT id FROM positions WHERE name = '%s'" % position
                            cursor.execute(position_sql)
                            position_id = cursor.fetchone()
                            if not position_id:
                                position_id = uuid.uuid4()
                                position_sql = "INSERT INTO positions(id, name) VALUES ('%s', '%s')" % (
                                    position_id, position)
                                cursor.execute(position_sql)
                            else:
                                position_id = position_id['id']
                            staff = {
                                'id': uuid.uuid4(),
                                'company': company['id'],
                                'name': staff['name'],
                                'position': position_id
                            }

                            query = """
                                INSERT INTO main_staff(id, company, name, position)
                                VALUES (%s,%s,%s,%s)
                            """
                            cursor.execute(query, (staff['id'], staff['company'], staff['name'],
                                                   staff['position']))

                    for investment in self.company_data['foreign_investments']:
                        registered_capital = self.get_money(
                            investment['registered_capital'])
                        investment = {
                            'id': uuid.uuid4(),
                            'company': company['id'],
                            'name': investment['name'],
                            'person': None if investment['person'] == "-" else investment['person'],
                            'registered_capital': registered_capital[0] if registered_capital else None,
                            'registered_capital_currency': registered_capital[1] if registered_capital else None,
                            'ratio': self.get_num(
                                investment['ratio'].replace('%', '') if investment['ratio'] else None),
                            'date': None if investment['date'] == "-" or len(investment['date']) < 1 else investment[
                                'date'],
                            'status': None if investment['status'] == "-" else investment['status'],
                        }

                        query = """
                            INSERT INTO foreign_investments(id, company, name, person, registered_capital,registered_capital_currency, ratio, date, status)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """
                        cursor.execute(query, (investment['id'], investment['company'], investment['name'],
                                               investment['person'], investment['registered_capital'], investment['registered_capital_currency'],
                                               investment['ratio'], investment['date'], investment['status']))

                    for change in self.company_data['changes']:
                        change_data = {
                            'id': uuid.uuid4(),
                            'company': company['id'],
                            'change_type': change['change_type'],
                            'date': change['date'] if len(change['date']) > 0 else None,
                            'before': change['before'],
                            'after': change['after'],
                        }

                        if change_data['before'] == None and change_data['after'] == None:
                            continue

                        query = """
                            INSERT INTO changes(id, company, date, change_type, before_c, after_c)
                            VALUES (%s,%s,%s,%s,%s,%s)
                        """
                        cursor.execute(query, (change_data['id'], change_data['company'], change_data['date'],
                                               change_data['change_type'], change_data['before'], change_data['after']))
                    try:
                        self.cnx.commit()
                    except pymysql.err.OperationError as e:
                        print(
                            f"[X] [SaveCompany] Error for while committing {self.company_data['basic_info']['uuid']} on line {sys.exc_info()[-1].tb_lineno}: {e}")
                        print(f"Will retry in 2 seconds...")
                        time.sleep(2)
                        self.cnx.commit()

        except Exception as e:
            print(
                f"[X] [SaveCompany] Error for {self.company_data['basic_info']['uuid']} on line {sys.exc_info()[-1].tb_lineno}: {e}")
