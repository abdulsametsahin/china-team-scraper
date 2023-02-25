from flask import Flask, render_template
from config import mysql_config
import pymysql

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/api/company/<uuid>')
def get_company(uuid):
    conn = pymysql.connect(host=mysql_config['host'], user=mysql_config['user'], password=mysql_config['password'],
                           database=mysql_config['database'], port=mysql_config['port'], charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

    with conn.cursor() as cursor:
        sql = "SELECT * FROM companies WHERE id=%s"
        cursor.execute(sql, uuid)
        result = cursor.fetchone()

        if result is None:
            return {
                'error': 'No such company',
            }

        data = {
            'company_data': result,
        }

        sql = "SELECT * FROM branches WHERE company=%s"
        cursor.execute(sql, (uuid))
        result = cursor.fetchall()

        data['branches'] = result

        sql = "SELECT * FROM main_staff WHERE company=%s"
        cursor.execute(sql, (uuid))
        result = cursor.fetchall()

        data['main_staff'] = result

        sql = "SELECT * FROM shareholders WHERE company=%s"
        cursor.execute(sql, (uuid))
        result = cursor.fetchall()

        data['shareholders'] = result

        sql = "SELECT * FROM changes WHERE company=%s"
        cursor.execute(sql, (uuid))
        result = cursor.fetchall()

        data['changes'] = result

        sql = "SELECT * FROM foreign_investments WHERE company=%s"
        cursor.execute(sql, (uuid))
        result = cursor.fetchall()

        data['foreign_investments'] = result

        sql = "SELECT * FROM annual_reports WHERE company=%s"
        cursor.execute(sql, (uuid))
        result = cursor.fetchall()

        data['annual_reports'] = result

        return data


if __name__ == '__main__':
    app.run()
