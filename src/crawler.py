import os
import random
import re
import time
from queue import Queue

import pandas as pd
import selenium
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.convertor import create_csv


class FacebookCrawler:
    # login page
    LOGIN_URL = 'https://www.facebook.com/login.php?login_attempt=1&lwv=111'

    def __init__(self):
        # chrome settings
        chrome_options = webdriver.ChromeOptions()

        prefs = {"profile.default_content_setting_values.notifications": 2}
        chrome_options.add_experimental_option("prefs", prefs)

        chrome_options.add_argument("--disable-blink-features")  # попытка избежать блока
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        self.driver = webdriver.Chrome(options=chrome_options,
                                       executable_path=r'C:\chromedriver_win32\chromedriver.exe')
        # gives driver wait time and then
        self.wait = WebDriverWait(self.driver, 10)

        self.page_link = ''

        self.counter = 1

        self.d_info = dict()

        self.visited = set()

        self.storage = list()  # LINKS of visited people

        self.users_pages = Queue()

    def login(self, login, password):
        self.driver.get(self.LOGIN_URL)

        # wait for the login page to load
        self.wait.until(EC.visibility_of_element_located((By.ID, "email")))

        self.driver.find_element_by_id('email').send_keys(login)
        self.driver.find_element_by_id('pass').send_keys(password)
        self.driver.find_element_by_id('loginbutton').click()

        # wait for the main page to load
        time.sleep(random.randrange(1, 5, 1))
        # get link of initial page
        self.page_link = self.driver.current_url
        # open initial page
        self.driver.get(self.page_link)
        time.sleep(random.randrange(1, 5, 1))

    def write_in_json(self):
        """
        Add parsed data from storage to .json file.
        """
        df = pd.DataFrame(self.d_info, index=[self.counter])
        self.counter += 1
        self.d_info = dict()
        df.to_csv('../output/fb_hse_usr_jobs.csv',
                  mode='a',
                  index=False,
                  header=False)

    def to_parse_job(self, job: str):
        """
        Get job name info.
        :param job: string with info about jobs
        :return: current job name & prev job name
        """
        try:
            _job = re.search(r'Работа*', job)
            if _job:
                job_now = job.split('Работа')[1]  # job now
                _job_past = re.search(r'Работал[а]*', job)
                if _job_past:
                    job_past = re.split(r'Работал[а]?', job)[1]  # prev job
                    return job_now, job_past
                # no job note
                elif job_now == 'Нет рабочих мест для показа':
                    return '-', '-'
                else:
                    return job_now, '-'
        except TimeoutException:
            self.write_in_json()
            time.sleep(random.choice([10800, 12600, 11700, 11400]))
            self.to_parse()

    def to_parse_study(self, study: str) -> bool:
        """
        Get university name info.
        :param study: string with info about uni-s
        :return: (bool) whether user studies or studied in HSE
        """
        try:
            _study = re.search(r'Вуз*', study)
            if _study:
                study_name = study.split('Вуз')[1]  # study name
                # try find ВШЭ, Вышка, HSE
                hse_study = re.search(r'[a-zA-Zа-яА-Я ]*HSE[a-zA-Zа-яА-Я ]*', study) or \
                            re.search(r'[a-zA-Zа-яА-Я ]*вшэ[a-zA-Zа-яА-Я ]*', study) or \
                            re.search(r'[a-zA-Zа-яА-Я ]*ВШЭ[a-zA-Zа-яА-Я ]*', study) or \
                            re.search(r'[a-zA-Zа-яА-Я ]*Вышка[a-zA-Zа-яА-Я ]*', study) or \
                            re.search(r'[a-zA-Zа-яА-Я ]*Higher School of Economics[a-zA-Zа-яА-Я ]*', study) or \
                            re.search(r'[a-zA-Zа-яА-Я ]*Высшая школа экономики[a-zA-Zа-яА-Я ]*', study)
                if hse_study:
                    return True
                elif study_name == 'Нет школ для показа':  # no uni note
                    return False
                else:
                    return False
        except TimeoutException:
            self.write_in_json()
            time.sleep(random.choice([10800, 12600, 11700, 11400]))
            self.to_parse()

    def get_info_link(self, info_links: list) -> str:
        """
        Parse link with information about person.
        :param info_links: different links
        """
        for link in info_links:
            if re.search(r'[a-zA-Zа-яА-Я ]*about', link):
                return link

    def error_processing(self, id_usr, name_usr, link):
        """
        If can't open html m do it later & add link to queue.
        """
        arr = [id_usr, name_usr, link]
        self.users_pages.put(arr)
        if link in self.visited:
            self.visited.remove(link)

    def get_info(self, id_usr, name_usr, link) -> dict:
        """
        Link by link go to usr info about job & study.
        :param link: main user's fb page
        :return: dict with parsed info about job & study
        """
        try:
            self.driver.get(link)  # open user page
            time.sleep(random.randrange(3, 5, 1))

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # if "Этот контент сейчас недоступен"
            if soup.find_all('span', {'class': 'd2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh a8c37x1j keod5gw0 '
                                               'nxhoafnm aigsh9s9 ns63r2gh fe6kdd0r mau55g9w c8b282yb iv3no6db '
                                               'o3w64lxj b2s5l15y hnhda86s m9osqain oqcyycmt'}):
                return self.d_info

            info_links = []
            for i in soup.find_all(class_='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9'
                                          ' pq6dq46d p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a'
                                          ' qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl l9j0dhe7 abiwlrkh'
                                          ' p8dawk7l dwo3fsh8 ow4ym5g4 auili1gw mf7ej076 gmql0nx0 tkr6xdv7 bzsjyuwj '
                                          'cb02d2ww j1lvzwm4', href=True):
                info_links.append(str(i['href']))

            info_link = self.get_info_link(info_links)

            
            self.driver.get(info_link)  # open page with info
            time.sleep(random.randrange(2, 4, 1))

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            link = soup.find_all('a', {'class': 'oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz '
                                                'rq0escxv nhd2j8a9 a8c37x1j p7hjln8o kvgmc6g5 cxmmr5t8 '
                                                'tvmbv18p hcukyx3x pybr56ya rv4hoivh f10w8fjw h4z51re5 '
                                                'i1ao9s8h esuyzwwr f1sip0of lzcic4wl l9j0dhe7 abiwlrkh '
                                                'p8dawk7l beltcj47 p86d2i9g aot14ch1 kzx2olss'}, href=True)
            info_link = str(link[0].get('href'))
            self.driver.get(info_link)  # open page with study & job
            time.sleep(random.randrange(1, 5, 1))

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            # if page is private
            if soup.find_all('span', {'class': 'd2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh a8c37x1j '
                                               'keod5gw0 nxhoafnm aigsh9s9 ns63r2gh fe6kdd0r mau55g9w '
                                               'c8b282yb iv3no6db o3w64lxj b2s5l15y hnhda86s pipptul6 '
                                               'oqcyycmt'}):
                return self.d_info

            job_study = soup.find_all('div', {'class': 'tu1s4ah4'})
            job = job_study[1].get_text()
            study = job_study[2].get_text()

            if self.to_parse_study(study):  # is user from HSE
                job_now, job_past = self.to_parse_job(job)

                if job_now == job_past == '-':
                    self.d_info['job_now'] = '-'
                    self.d_info['job_past'] = '-'
                elif job_past == '-':
                    self.d_info['job_now'] = job_now
                    self.d_info['job_past'] = '-'
                else:
                    self.d_info['job_now'] = job_now
                    self.d_info['job_past'] = job_past
            return self.d_info
        except selenium.common.exceptions.InvalidArgumentException:
            self.error_processing(id_usr, name_usr, link)
            time.sleep(random.randrange(2, 4, 1))
            self.to_parse()
        except IndexError:
            self.error_processing(id_usr, name_usr, link)
            time.sleep(random.randrange(2, 4, 1))
            self.to_parse()
        except TimeoutException:
            self.error_processing(id_usr, name_usr, link)
            time.sleep(random.choice([10800, 12600, 11700, 11400]))
            self.to_parse()

    def set_data(self):
        """
        Fill in given data about HSE likers & subscribers.
        """
        create_csv()  # from .xlsx to .csv

        file_name = '../data/fb_data.csv'
        f = os.path.abspath(file_name)
        data = pd.read_csv(f)

        row_count = len(data['name'])  # amount of rows
        ids = data['id']
        names = data['name']
        links = data['link']

        for i in range(row_count):
            arr = [ids[i], names[i], links[i]]
            self.users_pages.put(arr)

        df = pd.DataFrame(columns=["id", "name", "job_now", "job_past"])
        df.to_csv(r'../output/fb_hse_usr_jobs.csv', index=False, header=True)

    def fill_storage(self, user_id: str, user_name: str, d_information: dict):
        """
        Save all parsed usr info into self.storage(list).
        :param user_id: id is just a num in queue
        :param user_name: name+surname from fb
        :param d_information: current job, prev job
        """
        d_info = dict()

        d_info['id'] = int(user_id)
        d_info['name'] = user_name

        d_info.update(d_information)

        self.storage.append(d_info)
        self.d_info = d_info
        self.write_in_json()

    def to_parse(self):
        """
        Check if link was visited, otherwise start to parse it.
        """
        while not self.users_pages.empty():
            arr = self.users_pages.get()
            id_usr = arr[0]
            name_usr = arr[1]
            link_usr = arr[2]

            if link_usr not in self.visited:
                self.visited.add(link_usr)  # add link in visited
                try:
                    user_information = self.get_info(id_usr, name_usr, link_usr)
                    if bool(user_information):
                        # add parsed user into storage
                        self.fill_storage(id_usr, name_usr, user_information)
                except TimeoutException:
                    self.write_in_json()
                    time.sleep(random.choice([10800, 12600, 11700, 11400]))
                    self.to_parse()


def main():
    now = time.time()
    login = '79037332943'
    password = 'мщшц38епцщг'

    # init class instance
    crawler = FacebookCrawler()
    # add data to class
    crawler.set_data()
    # dive into fb
    crawler.login(login=login, password=password)
    # start of parsing users
    crawler.to_parse()
    # close browser windows
    crawler.driver.quit()
    # output
    df = pd.DataFrame(crawler.storage, index=[0])
    df.to_csv('output_duplication.csv', mode='w', index=False, header=False)
    # time
    end = time.time() - now
    print(end)


if __name__ == '__main__':
    main()
