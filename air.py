# -*- coding: utf-8 -*-

import requests
import os
import sys
import re
from bs4 import BeautifulSoup
import time
import random
import threading
import Queue

# reload(sys)
# sys.setdefaultencoding('utf-8')

headers = {'Host': 'www.aqistudy.cn',
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

base_url = 'https://www.aqistudy.cn/historydata/daydata.php?city='
output_file = open("AQI.txt", "w")
all_res = Queue.Queue()

def test():
    url = 'https://www.aqistudy.cn/historydata/daydata.php?city=宝鸡&month=2015-08'
    r = requests.get(url, headers=headers)
    print r.status_code
    soup = BeautifulSoup(r.text)
    count = 0
    for i in range(3, len(soup.table.contents), 2):
        tr = soup.table.contents[i]
        print t.contents[1].string, tr.contents[3].string


def get_city_list():
    r = requests.get('https://www.aqistudy.cn/historydata/', headers=headers)
    # print r.status_code
    city_parttern = re.compile(u"city=([\u4e00-\u9fa5]+)\W{2,5}")
    cities = re.findall(city_parttern, unicode(r.text))
    if cities:
        for x in cities:
            if cities.count(x) > 1:
                cities.remove(x)
    print cities
    return cities


def sleep_random_time():
    time.sleep(random.randint(1, 5))


def get_month_list(city):
    url_city = base_url + city
    try:
        r = requests.get(url_city, headers=headers)
    except:
        return
    pattern = r"month\=(\d{6})"
    month_list = re.findall(pattern, r.text)
    # print month_list
    return month_list


def get_AQI(city, month, url_city):
    try:
        url_month = url_city + '&month=' + month[0:4] + month[4:6]
        r = requests.get(url_month, headers=headers)
        soup = BeautifulSoup(r.text)
        for i in range(3, len(soup.table.contents), 2):
            tr = soup.table.contents[i]
            # print city+','+tr.contents[1].string+','+tr.contents[3].string
            res = city + ',' + tr.contents[1].string + ',' + tr.contents[3].string + '\n'
            all_res.put(res.encode('utf-8'))

    except:
        return


class Get_AQI_thread(threading.Thread):
    def __init__(self, city_list, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.city_list = city_list

    def run(self):
        for city in self.city_list:
            try:
                url_city = base_url + city
                month_list = get_month_list(city)
                for month in month_list:
                    print 'Processing %s in %s in thread %d' % (city, month, self.thread_id)
                    sleep_random_time()
                    get_AQI(city, month, url_city)
                    print 'Finish %s in %s in thread %d' % (city, month, self.thread_id)
            except:
                continue

def main():
    try:
        city_list = get_city_list()
        # city_list = [u'成都', u'重庆', u'北京', u'上海', u'深圳']
        thread_num = 10
        all_threads = []
        for i in range(thread_num):
            city_list_thread = []
            for j in range(i, len(city_list), thread_num):
                city_list_thread.append(city_list[j])
            cur_thread = Get_AQI_thread(city_list_thread, i)
            cur_thread.start()
            all_threads.append(cur_thread)
        for thread in all_threads:
            thread.join()
    except:
        pass
    finally:
        while not all_res.empty():
            res = all_res.get()
            output_file.write(res)
        output_file.close()

if __name__ == '__main__':
    main()