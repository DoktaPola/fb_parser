import json
import os
import random
import re
import time
from queue import Queue

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.convertor import create_csv


class FacebookCrawler:
    LOGIN_URL = 'https://www.facebook.com/login.php?login_attempt=1&lwv=111'  # login page

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()

        prefs = {"profile.default_content_setting_values.notifications": 2}  # chrome settings
        chrome_options.add_experimental_option("prefs", prefs)

        chrome_options.add_argument("--disable-blink-features")  # попытка избежать блока
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        self.driver = webdriver.Chrome(options=chrome_options,
                                       executable_path=r'C:\chromedriver_win32\chromedriver.exe')
        self.wait = WebDriverWait(self.driver,
                                  10)  # дает драйверу подождать несколько секунд, перед следующим действием

        self.page_link = ''

        self.links = None

        self.links_items = None

        self.str = ''

        self.storage = {}

        self.id = ''

        self.counter = 0

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

        self.page_link = self.driver.current_url  # get link of initial page

        self.driver.get(self.page_link)  # open initial page
        time.sleep(random.randrange(1, 5, 1))

    def write_in_json(self):
        # TODO
        f = open('friends.json', 'w', encoding="utf-8")
        f.write(json.dumps(self.storage, indent=4, ensure_ascii=False, sort_keys=False))
        f.close()

        # create_csv()  # создаю DataFrame

        self.driver.close()

    def to_parse_job(self, job: str):
        _job = re.search(r'Работа*', job)
        if _job:
            job_now = job.split('Работа')[1]  # job now
            _job_past = re.search(r'Работал[а]*', job)
            if _job_past:
                job_past = re.split(r'Работал[а]?', job)[1]  # prev job
                return job_now, job_past
            elif job_now == 'Нет рабочих мест для показа':  # no job note
                return '-', '-'
            else:
                return job_now, '-'

    def to_parse_study(self, study: str):
        pass
        # _job = re.search(r'Работа*', job)
        # if _job:
        #     job_now = job.split('Работа')[1]  # job now
        #     _job_past = re.search(r'Работал[а]*', job)
        #     if _job_past:
        #         job_past = re.split(r'Работал[а]?', job)[1]  # prev job
        #         return job_now, job_past
        #     elif job_now == 'Нет рабочих мест для показа':  # no job note
        #         return '-', '-'
        #     else:
        #         return job_now, '-'

    def get_info(self, link) -> dict:
        try:
            d_info = dict()

            self.driver.get(link)  # open user page
            time.sleep(random.randrange(1, 5, 1))

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            links = soup.find_all(
                class_='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9'
                       ' pq6dq46d p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a'
                       ' qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl l9j0dhe7 abiwlrkh'
                       ' p8dawk7l dwo3fsh8 ow4ym5g4 auili1gw mf7ej076 gmql0nx0 tkr6xdv7 bzsjyuwj '
                       'cb02d2ww j1lvzwm4')  # get class with info link

            info_link = str(links[1]['href'])

            # info_link = 'https://www.facebook.com/daria.smirnova.944/about'  ######################
            # info_link = 'https://www.facebook.com/elisaveta.lobanova/about'  ######################
            info_link = 'https://www.facebook.com/ivan.khvorov/about'  ###################### работал
            # info_link = 'https://www.facebook.com/profile.php?id=100027683190771&sk=about'  ###################### пустая
            self.driver.get(info_link)  # open page with info
            time.sleep(random.randrange(1, 4, 1))

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            link = soup.find_all('a', {'class': 'oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz '
                                                'rq0escxv nhd2j8a9 a8c37x1j p7hjln8o kvgmc6g5 cxmmr5t8 '
                                                'tvmbv18p hcukyx3x pybr56ya rv4hoivh f10w8fjw h4z51re5 '
                                                'i1ao9s8h esuyzwwr f1sip0of lzcic4wl l9j0dhe7 abiwlrkh '
                                                'p8dawk7l beltcj47 p86d2i9g aot14ch1 kzx2olss'})
            info_link = str(link[0].get('href'))
            self.driver.get(info_link)  # open page with study & job
            time.sleep(random.randrange(1, 5, 1))

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            job_study = soup.find_all('div', {'class': 'tu1s4ah4'})
            job = job_study[1].get_text()
            study = job_study[2].get_text()
            t = 0

            self.to_parse_job(job)
            self.to_parse_study(study)

            # ПРОВЕРКА НА ВЫШКУ ВШЭ

            # if self.links is None:  # ЕСЛИ НЕТ ИНФЫ О job, education, city
            #     d_info['NO_info'] = '-'
            # else:
            #     for word in self.links:
            # soup_2 = BeautifulSoup(str(word), 'html.parser')
            # text = soup_2.get_text('\t')
            # sep_text = text.strip().split('\t')
            # if len(sep_text) == 1:
            #     d_info['some_info'] = sep_text[0]
            # else:
            #     _study = re.search(r'Учи[а-я]*', sep_text[0])  # parse
            # _study_2 = re.search(r'Изуча[а-я]*', sep_text[0])  # parse
            #
            # if (_study_2 is not None) or (_study is not None):
            #     d_info['study'] = sep_text[1]
            # elif sep_text[0].find('Живет') != -1:
            #     d_info['live_in'] = sep_text[1]
            #
            # self.links = soup.find_all(class_='_c24 _2ieq')  # get num, vk (or other social net), b-day
            # if self.links is None:  # ЕСЛИ НЕТ ИНФЫ О job, education, city
            #     d_info['NO_info'] = '-'
            # else:
            #     for
            # link in self.links:
            # soup_3 = BeautifulSoup(str(link), 'html.parser')
            # text = soup_3.get_text('\t')
            # sep_text = text.strip().split('\t')
            #
            # if sep_text[0].find('Телефоны') != -1:
            #     d_info['phone'] = sep_text[1]
            # elif sep_text[0].find('Дата рождения') != -1:
            #     d_info['b-day'] = sep_text[1]
            # elif sep_text[0].find('Ссылки на профили в Сети') != -1:
            #     d_info['links'] = sep_text[1]
            # elif sep_text[0].find('Электронный адрес') != -1:
            #     d_info['email'] = sep_text[1]
            #
            # return d_info
        except:
            self.write_in_json()

            # time.sleep(random.randrange(6, 10))  # to load all elems

    def set_data(self):
        """

        :return:
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

    def fill_storage(self, user_id: str, user_name: str, d_information: dict):
        # TODO
        pass

        # d_information['name'] = user_name
        #
        # d_friends_list = dict()
        # d_friends_list['friends'] = friends
        #
        # d_user = dict()
        # d_user['general_info'] = d_information
        # d_user['friends_list'] = d_friends_list
        # self.storage[user_id] = d_user

    def bfs(self):
        visited = set()  # LINKS of visited people

        while not self.users_pages.empty():
            arr = self.users_pages.get()
            id_usr = arr[0]
            name_usr = arr[1]
            link_usr = arr[2]

            if link_usr not in visited:
                visited.add(link_usr)  # add link in visited
                try:
                    user_information = self.get_info(link_usr)

                    self.fill_storage(id_usr, name_usr, user_information)  # add new person in stor

                except TimeoutException:
                    self.write_in_json()
            # else:
            #     self.users_pages.get()  # удаляю ссыдку на стр, если уже смотрели такого Пользователя


def main():
    login='79037332943'
    password='мщшц38епцщг'

    # login = 'irkaxortiza@mail.ru'
    # password = '17YouWannaBeOnTop1995'

    crawler = FacebookCrawler()
    crawler.set_data()
    crawler.login(login=login, password=password)
    crawler.bfs()
    # INITIAL ADDING
    # id = crawler.get_id(crawler.page_link)  # only main user id
    #
    # user_name = crawler.get_init_name()
    #
    # arr_links_inf_fr = crawler.get_links_info_friends()  # return 2 links to open inf and fr pages
    # arr_info = crawler.get_info(arr_links_inf_fr[0])  # call method to get info from page
    # arr_friends = crawler.get_friends(arr_links_inf_fr[1])  # call method to get list of friends from page
    #
    # fill_storage(crawler, id, user_name, arr_info, arr_friends)

    # bfs(crawler)  # call bfs from my friends


if __name__ == '__main__':
    main()
