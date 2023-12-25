from bs4 import BeautifulSoup as bs4
import requests
from os import environ
from urllib.parse import urljoin
from dotenv import load_dotenv
import shelve
from parse_data import ParseData
from operator import itemgetter

load_dotenv(dotenv_path='.env', override=True)

class Ims():
    def __init__(self, persistentSession):
        self.username = environ['imsUsername']
        self.password = environ['imsPassword']

        if not persistentSession:

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

            self.session = requests.Session()
            self.session.headers.update(self.baseHeaders)

            self.baseUrl = 'https://www.imsnsit.org/imsnsit/'

            self.initialCookes = self.getInitialCookies()
            self.captchaImage, self.hrandNum = self.getLoginCaptcha()

            self.profileUrl = ''
            self.myActivitiesUrl = ''
        
        else:
            file = shelve.open('session_object')
            self.session = file['session']
            self.profileUrl = file['profile_url']
            self.myActivitiesUrl = file['activities_url']

            print(self.profileUrl)

    def getInitialCookies(self):
        self.session.get('https://www.imsnsit.org/imsnsit/', headers=self.baseHeaders)

    def getLoginCaptcha(self):
        self.session.headers.update(
            {
            'Referer': 'https://www.imsnsit.org/imsnsit/',
            'Sec-Fetch-User': '?1'
            }
        )

        response = self.session.get('https://www.imsnsit.org/imsnsit/student_login110.php')
        soup = bs4(response.content, 'html.parser')
        
        captcha = urljoin(self.baseUrl, soup.select_one('#captchaimg')['src'])
        hrand_num = soup.select_one("#HRAND_NUM")['value']
        
        return captcha, hrand_num

    def loginToIms(self):

        self.session.headers.update(
            {
                'Referer': 'https://www.imsnsit.org/imsnsit/student_login.php',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://www.imsnsit.org',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'frame',
            }
        )
        
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

        response = self.session.post('https://www.imsnsit.org/imsnsit/student_login.php', data=data)
        
        if 'Please try again' in str(response.content):
            print("Login Failed....")

        soup = bs4(response.content, 'html.parser')
        links = soup.find_all('a')

        for link in links:
            if link.get_text() == 'Profile':
                self.profileUrl = link['href']
            
            if link.get_text() == 'My Activities':
                self.myActivitiesUrl = link['href']

        file = shelve.open('session_object')
        file['session'] = self.session
        file['profile_url'] = self.profileUrl
        file['activities_url'] = self.myActivitiesUrl
        file.close()
    
    def getProfileData(self):
        response = self.session.get(self.profileUrl)
        
        profileData = ParseData.parseProfile(response.content)

        return profileData
    
    def getAttandanceData(self, rollNo='', dept='', degree=''):
        response = self.session.get(self.myActivitiesUrl)

        soup = bs4(response.content, 'html.parser')
        attandancePage = ''

        for link in soup.find_all('a', {'target': 'data'}):
            if link.text == 'Attendance Report':
                attandancePage = link['href']
                break
        else:
            print('Attandance Page not Found')
            return

        response = self.session.get(attandancePage)
        soup = bs4(response.content, 'html.parser')

        enc_year = soup.find_all('input', {'id': 'enc_year'})[0]['value']
        enc_sem = soup.find_all('input', {'id': 'enc_sem'})[0]['value']

        if not (rollNo or dept or degree):
            rollNo = soup.find_all('input', {'name': 'recentitycode'})[0]['value']
            dept = soup.find_all('input', {'name': 'dept'})[0]['value']
            degree = soup.find_all('input', {'name': 'degree'})[0]['value']


        data = {
            'year': '2023-24',
            'enc_year': enc_year,
            'sem': '1',
            'enc_sem': enc_sem,
            'submit': 'Submit',
            'recentitycode': rollNo,
            'dept': dept,
            'degree': degree,
            'ename': '',
            'ecode': '',
        }

        response = self.session.post(attandancePage, data=data)
        
        attandanceData = ParseData.parseAttandance(response.content)
        
        return attandanceData


class User():
    def __init__(self):
        self.ims = Ims(persistentSession=True)

        profileData = self.ims.getProfileData()

        self.roll, self.name, self.dob, self.gender, self.category, self.branch, self.degree, self.section \
            = itemgetter('Student ID', 'Student Name', 'DOB', 'Gender', 'Category', 'Branch Name', 'Degree', 'Section')\
                (profileData)
        
        self.attandances = self.ims.getAttandanceData()

user = User()
import pdb
pdb.set_trace()