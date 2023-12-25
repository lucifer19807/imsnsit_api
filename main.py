from bs4 import BeautifulSoup as bs4
import requests
from os import environ
from urllib.parse import urljoin
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env', override=True)

class Ims():
    def __init__(self):
        self.username = environ['imsUsername']
        self.password = environ['imsPassword']

        self.session = requests.Session()

        self.baseHeaders = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.119 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
        }

        self.baseUrl = 'https://www.imsnsit.org/imsnsit/'

        self.initialCookes = self.getInitialCookies()
        self.captchaImage, self.hrandNum = self.getLoginCaptcha()

    def getInitialCookies(self):
        response = requests.get('https://www.imsnsit.org/imsnsit/', headers=self.baseHeaders)
        return response.cookies.get_dict()

    def getLoginCaptcha(self):
        
        headers = self.baseHeaders.copy()
        headers['Referer'] = 'https://www.imsnsit.org/imsnsit/'
        headers['Sec-Fetch-User'] = '?1'
        
        response = requests.get('https://www.imsnsit.org/imsnsit/student_login110.php', cookies=self.initialCookes, headers=headers)
        
        soup = bs4(response.content, 'html.parser')
        
        captcha = urljoin(self.baseUrl, soup.select_one('#captchaimg')['src'])
        hrand_num = soup.select_one("#HRAND_NUM")['value']
        
        return captcha, hrand_num

    def loginToIms(self):

        headers = self.baseHeaders.copy()
        headers['Referer'] = 'https://www.imsnsit.org/imsnsit/student_login.php'
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers['Origin'] = 'https://www.imsnsit.org'
        headers['Upgrade-Insecure-Requests'] = '1'
        headers['Sec-Fetch-Dest'] = 'frame'

        cap = input(f"Enter The Captch {self.captchaImage}: ")
        
        data = {
            'f': '',
            'uid': self.username,
            'pwd': self.password,
            'HRAND_NUM': self.hrandNum,
            'fy': '2023-24',
            'comp': 'NETAJI SUBHAS UNIVERSITY OF TECHNOLOGY',
            'cap': cap,
            'logintype': 'student',
        }

        response = requests.post('https://www.imsnsit.org/imsnsit/student_login.php', cookies=self.initialCookes, headers=headers, data=data)
        print(response.content)
        print(response.cookies.get_dict())

ims = Ims()
ims.loginToIms()
