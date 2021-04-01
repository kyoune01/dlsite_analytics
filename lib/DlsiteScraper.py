#!/usr/bin/env python
# -*- coding: utf-8 -*-


import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
import bs4
import json


class DlsiteScraper():
    """
    参考：https://qiita.com/meznat/items/b9eee3c2700731855f10
    """

    def __init__(self):
        self.url_top = "https://login.dlsite.com/guide/welcome"
        self.url_login = "https://login.dlsite.com/login"
        self.url_count = "https://www.dlsite.com/maniax/mypage/userbuy/=/type/all/start/all/sort/1/order/1/page/"
        self.is_loging = False
        # chrome driver -headless mode
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(options=options)
        # if you want debug
        # self.driver = webdriver.Chrome()

        self.driver.get(self.url_top)
        self.driver.add_cookie(
            {"name": 'adultchecked', "value": '1', "domain": ".dlsite.com"})

    # destractor
    def __del__(self):
        print("del:driver")
        self.driver.quit()

    def login(self, username, password):
        self.username = username
        self.password = password
        driver = self.driver
        # Login window
        print("login window open")
        driver.get(self.url_login)
        username_box = driver.find_element_by_id("form_id")
        username_box.send_keys(self.username)
        password_box = driver.find_element_by_id("form_password")
        password_box.send_keys(self.password)
        submit_button = driver.find_element_by_xpath("//*[@type='submit']")
        print("try login")
        submit_button.submit()
        # Mypage window
        if self.url_top in driver.current_url:
            print("success login and open Mypage")
            self.driver = driver
            self.is_loging = True
        return self.is_loging

    def scrape_purchase_history(self):
        if not self.is_loging:
            print('not login: please self.login')
            return []

        driver = self.driver
        page = 1
        work_list = []

        while True:
            url = self.url_count + str(page)
            print(url)

            driver.get(url)
            WebDriverWait(driver, 100000).until(
                EC.presence_of_element_located((By.CLASS_NAME, "work_name"))
            )

            work_list.extend(self.__formatPurchaseWebElemntToList(driver))

            # 最後のページかチェック
            is_last_link = driver.find_element_by_class_name(
                "page_no").find_elements_by_xpath("//a[text()=\"最後へ\"]")
            if len(is_last_link) == 0:
                print("load finish")
                break
            else:
                page += 1

        return work_list

    def __formatPurchaseWebElemntToList(self, driver):
        result = []
        item_table = driver.find_element_by_id("buy_history_this")
        item_elements = item_table.find_elements_by_tag_name("tr")

        if item_elements[0].get_attribute("class") == "item_name":
            item_elements = item_elements[1:]

        for item_element in item_elements:
            item = self.__getItemData(item_element)
            print(item["work_name"]["text"])
            result.append(item)

        return result

    def __getItemData(self, item_element):
        item = {}

        buy_date_element = item_element.find_element_by_class_name("buy_date")
        item.update({"buy_date": buy_date_element.text})

        work_genre_element = item_element.find_element_by_class_name(
            "work_genre")
        item.update(
            {"work_genre": work_genre_element.find_element_by_tag_name("span").text})

        payment_method_element = item_element.find_element_by_class_name(
            "payment_method")
        item.update({"payment_method": payment_method_element.text})

        work_price_element = item_element.find_element_by_class_name(
            "work_price")
        if work_price_element.text == '':
            raise ValueError(
                "load error, help: is_load 'adultchecked' cookie?")
        item.update({"work_price": work_price_element.text})

        work_name_element = item_element.find_element_by_class_name(
            "work_name")
        is_link = work_name_element.find_elements_by_tag_name("a")
        work_href = work_name_element.find_element_by_tag_name(
            "a").get_attribute("href") if len(is_link) == 1 else ''
        work_text = work_name_element.find_element_by_tag_name(
            "a").text if len(is_link) == 1 else work_name_element.text
        item.update({"work_name": {
            "url": work_href,
            "text": work_text,
        }})

        maker_name_element = item_element.find_element_by_class_name(
            "maker_name")
        is_link = maker_name_element.find_elements_by_tag_name("a")
        maker_href = maker_name_element.find_element_by_tag_name(
            "a").get_attribute("href") if len(is_link) == 1 else ''
        maker_text = maker_name_element.find_element_by_tag_name(
            "a").text if len(is_link) == 1 else maker_name_element.text
        item.update({"maker_name": {
            "url": maker_href,
            "text": maker_text,
        }})

        return item

    @staticmethod
    def scrape_work_detail(url):
        """作品詳細をスクレイピング

        Args:
            urls (str): スクレイピング対象作品URL

        Returns:
            list: スクレイピング結果 {'genre': [genre1, genre2, ...]}
        """
        result = {'genre': []}
        tmp = []

        if url == '':
            return result

        response = requests.get(url)
        bs4Obj = bs4.BeautifulSoup(response.text, 'html.parser')
        elements = bs4Obj.select('#work_outline .main_genre a')
        for element in elements:
            tmp.append(element.get_text())
        elements = bs4Obj.select('.reviewer_most_genre td a')
        for element in elements:
            tmp.append(element.get_text().split("（")[0])
        result['genre'] = list(set(tmp))

        return result

    @staticmethod
    def fetch_workcount():
        """登録済総作品のジャンルカウントをAPIから取得

        Returns:
            list: ジャンル数カウント
                [{
                    'id': ジャンルの内部ID,
                    'all_count' 登録数,
                    'text', ジャンル名
                }, {}, ...]
        """
        url_workcount = 'https://www.dlsite.com/maniax/api/fs/summary/workcount'
        print(url_workcount)
        response = requests.get(url_workcount)
        tmp = json.loads(response.text)
        workcount = tmp['genre_work_count_list']

        url_file_serch = 'https://www.dlsite.com/maniax/fs/'
        print(url_file_serch)
        response = requests.get(url_file_serch)
        bs4Obj = bs4.BeautifulSoup(response.text, 'html.parser')

        tmp = []
        elements = bs4Obj.select('label[for^="genre"]')
        for element in elements:
            if 'and' in element['for']:
                continue

            for work in workcount:
                if work['genre_value'] == element['for'][6:]:
                    genre_id = work['genre_value']
                    genre_count = work['work_count']
                    genre_text = element.get_text()
                    break

            tmp.append([int(genre_count), genre_id, genre_text])

        tmp.sort(reverse=True)

        result = []
        for item in tmp:
            if result == [] or result[-1]['id'] != item[1]:
                result.append({
                    'id': item[1],
                    'all_count': item[0],
                    'text': item[2],
                })

        return result
