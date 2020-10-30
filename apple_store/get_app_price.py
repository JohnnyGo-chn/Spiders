#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import requests
import datetime
from lxml import etree
from tkinter import *
from tkinter import messagebox

class AppleStorePriceFetcher():

    def __init__(self):
        self.ALARM_CONTINUE = 0
        self.ALARM_EXIT = 1
        self.hist_data = None
        self.hist_data_path = "/Users/dengyuting/Documents/Projects/Spider/apple_store/hist_price"

    # 弹出消息
    def __window_alarm(self, msg, status=0):
        """
        弹出通知框，不打印到控制台
        """

        root = Tk()
        root.withdraw()
        messagebox.showinfo("提示", msg)

        if status != 0:
            exit()

    # 读取已有的数据
    def __read_history(self):
        if not os.path.exists(self.hist_data_path):
            self.hist_data = {}
        else:
            self.hist_data = json.loads(open(self.hist_data_path, "r").read())

    # 写入历史数据，此时历史数据中必须有值
    def __write_history(self):
        if self.hist_data == None:
            return

        with open(self.hist_data_path, "w") as fout:
            fout.write(json.dumps(self.hist_data, indent=4, ensure_ascii=False))

    def compare_price(self, app_name, price):
        if self.hist_data == None:
            self.__read_history()

        now_day = datetime.datetime.now().strftime("%Y%m%d")
        if app_name not in self.hist_data:
            self.hist_data[app_name] = {}
            self.hist_data[app_name]["lowest"] = price
            self.hist_data[app_name]["hist_price"] = {}
            self.hist_data[app_name]["hist_price"][now_day] = price
        else:
            if "lowest" in self.hist_data[app_name] and price < self.hist_data[app_name]["lowest"]:
                self.__window_alarm("应用[%s]当前最低价[%f]" % (app_name, price))
                self.hist_data[app_name]["lowest"] = price
                self.hist_data[app_name]["hist_price"][now_day] = price
            else:
                self.hist_data[app_name]["hist_price"][now_day] = price
            
    # 获取软件价格
    def get_item_price(self, app_url):
        header = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
        }

        try:
            apple_web_content = requests.get(app_url)
            etree_formated_content = etree.HTML(apple_web_content.content)
            # 应用名称
            app_name = app_url.split("/")[-2]
            # 价格
            app_price_tag = etree_formated_content.xpath("//li[@class=\"inline-list__item inline-list__item--bulleted app-header__list__item--price\"]/text()")[0]
            price = float(str(app_price_tag.split("¥")[1]))
            # 比价
            self.compare_price(app_name, price)
        except Exception as e:
            print("获取应用[" + app_name + "]价格失败，原因：" + str(e), self.ALARM_EXIT)

    def run(self):
        self.__read_history()
        self.get_item_price("https://apps.apple.com/cn/app/goodnotes-5/id1444383602")
        self.get_item_price("https://apps.apple.com/cn/app/notability/id360593530")
        self.__write_history()

fetcher = AppleStorePriceFetcher()
fetcher.run()
