import time

from config import gongsi_config
import requests
import json
import os


class GenerateCookie:
    def __init__(self):
        self.cookie_file = 'storage/cookies.txt'
        while True:
            try:
                self.test_cookie()
                print("[x] [GenerateCookie] Sleeping for 1 hour")
                time.sleep(60 * 60)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)

    def login(self):
        url = "https://www.gongsi.com.cn/user/login-pwd"
        payload = f"phone={gongsi_config['phone_number']}&password={gongsi_config['password']}&checkStatusFirst=false"

        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        # write cookies to file, create file if not exists

        with open(self.cookie_file, 'w') as f:
            json.dump(requests.utils.dict_from_cookiejar(response.cookies), f)

    def test_cookie(self):
        if not os.path.exists(self.cookie_file):
            print("[x] [GenerateCookie] Cookie file not found, login")
            self.login()
            self.test_cookie()
            return

        print("[x] [GenerateCookie] Testing cookie")
        url = "https://www.gongsi.com.cn/search/bs1pg220"
        session = requests.session()
        try:
            with open(self.cookie_file, 'r') as f:
                cookies = json.load(f)
                session.cookies = requests.utils.cookiejar_from_dict(cookies)
        except Exception as e:
            print(f"Error: {e}")
            self.login()
            self.test_cookie()

        response = session.get(url)

        if "登录-满商公司网-企业信息查询" in response.text:
            print("[x] [GenerateCookie] Cookie expired, re-login")
            self.login()
            self.test_cookie()
        else:
            print("[x] [GenerateCookie] Cookie is valid")
