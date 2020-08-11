#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib.DlsiteScraper import DlsiteScraper
from lib.JsonFile import JsonFile
import lib.setting as setting

# main
import traceback

# extract_genre_count
import collections
import itertools

# calculate_inclination
# sanpu
import matplotlib.pyplot as plt
import numpy as np


def merge_works_detail(purchase_history, works_detail):
    result = []
    for (purchase, detail) in zip(purchase_history, works_detail):
        purchase.update({'genre': detail['genre']})
        result.append(purchase)
    return result


def extract_genre_count(purchase_history):
    items = list(itertools.chain.from_iterable(
        [item.get('genre', []) for item in purchase_history]
    ))
    genre_count = collections.OrderedDict(
        collections.Counter(items).most_common()
    )
    return genre_count


def count_genre(genres_count, workcount):
    result = []

    for genre in workcount:
        purchase_count = (
            genres_count[genre['text']]
            if genre['text'] in genres_count
            else 0
        )
        genre['purchase_count'] = purchase_count

        result.append(genre)

    return result


def calculate_inclination(items):
    text = np.array([])
    all_count = np.array([])
    purchase_count = np.array([])
    for item in items:
        text = np.append(text, [item['text']])
        all_count = np.append(all_count, [item['all_count']])
        purchase_count = np.append(purchase_count, [item['purchase_count']])

    ab1 = np.polyfit(all_count, purchase_count, 3)
    all_C = np.poly1d(ab1)(all_count)
    plt.plot(all_count, all_C)

    aaa = []
    for (j, t) in zip(purchase_count, all_C):
        aaa.append(j - t)

    max_list = sorted(aaa, reverse=True)
    min_list = sorted(aaa)

    result = ''
    hr = '======================'
    lf = "\n"
    result = result + hr + lf

    for index in range(10):
        result = result + (
            '性癖：' +
            text[aaa.index(max_list[index])] +
            '、' +
            str(np.round(max_list[index]))
        ) + lf

    result = result + hr + lf

    for index in range(10):
        result = result + (
            '地雷：' +
            text[aaa.index(min_list[index])] +
            '、' +
            str(np.round(min_list[index]))
        ) + lf

    result = result + hr + lf

    return result


def sanpu(items, label=True):
    text = np.array([])
    all_count = np.array([])
    purchase_count = np.array([])
    for item in items:
        text = np.append(text, [item['text']])
        all_count = np.append(all_count, [item['all_count']])
        purchase_count = np.append(purchase_count, [item['purchase_count']])

    # print(np.corrcoef(np.array([all_count, purchase_count])))
    ab1 = np.polyfit(all_count, purchase_count, 3)
    all_C = np.poly1d(ab1)(all_count)
    plt.plot(all_count, all_C)

    for (i, j, k) in zip(all_count, purchase_count, text):
        plt.plot(i, j, 'o')
        if label:
            plt.annotate(k, xy=(i, j))

    plt.xlabel('総販売作品のジャンル登録数')
    plt.ylabel('購入済作品のジャンル登録数')
    # plt.show()
    plt.savefig('_figure.png')


def main():
    # input user_code and password
    login_id = setting.USER
    login_pass = setting.PASS
    purchase_works_json_path = '_purchase_works.json'
    count_genre_json_path = '_count_genre_dict.json'
    result_path = '_result.txt'

    site = DlsiteScraper()

    purchase_history = []
    try:
        # login dlsite
        if site.login(login_id, login_pass):
            print("login success")
            # scrape purchase_history
            purchase_history = site.scrape_purchase_history()
            print("scrape purchase_history success")
        else:
            print("login failed")
    except BaseException:
        traceback.print_exc()
    finally:
        del site

    if purchase_history == []:
        print("scrape purchase_history failed")
        exit()

    # scrape works_detail and workcount
    print("scrape works_detail and workcount")
    work_url_list = [x['work_name']['url'] for x in purchase_history]
    works = []
    for work_url in work_url_list:
        print(work_url)
        works.append(DlsiteScraper.scrape_work_detail(work_url))
    workcount = DlsiteScraper.fetch_workcount()
    print("scrape works_detail and workcount success")

    # merge purchase_history and works
    print("merge purchase_history and works")
    purchase_works = merge_works_detail(purchase_history, works,)
    JsonFile.save(purchase_works_json_path, purchase_works)
    print("merge purchase_history and works success")

    # count genre
    print("count genre")
    genres_count = extract_genre_count(purchase_works)
    count_genre_dict = count_genre(genres_count, workcount)
    JsonFile.save(count_genre_json_path, count_genre_dict)
    print("count genre success")

    # calculate inclination
    print("calculate inclination")
    result = calculate_inclination(count_genre_dict)
    with open(result_path, 'w', encoding='utf_8') as f:
        f.write(result)
    print("calculate inclination success")

    # drawing graph
    print("drawing graph")
    sanpu(count_genre_dict, label=True)
    print("drawing graph success")


if __name__ == "__main__":
    main()
