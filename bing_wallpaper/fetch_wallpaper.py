#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import requests
import datetime
import subprocess
import configparser
from lxml import etree
from tkinter import *
from tkinter import messagebox

ALARM_PASS = 0
ALARM_EXIT = 1

def alarm(msg, status=0):
    """
    打印消息，status ！= 0时打印消息后退出，默认打印后程序继续
    """

    print(msg)
    if status != 0:
        exit()

def window_alarm(msg, status=0):
    """
    弹出通知框，不打印到控制台
    """

    root = Tk()
    root.withdraw()
    messagebox.showinfo("提示", msg)

    if status != 0:
        exit()

def generate_path_dir(path):
    """
    如果文件夹不存在则创建
    """

    if not os.path.exists(path):
        os.mkdir(path)
    elif os.path.isfile(path):
        alarm(path + " exist and is file! Please Delete it or make it a directory!", ALARM_EXIT)

def get_base_path():
    """
    读取配置，目前仅一个：保存图片到的地址
    """

    conf = configparser.ConfigParser()
    if os.path.exists("base.conf"):
        conf.read("base.conf")
    else:
        alarm("配置文件(base.conf)不存在，请确认后重试!")

    base_dir = conf.get("common", "base_dir")

    return base_dir
    

def get_image_path(base_dir):

    generate_path_dir(base_dir)

    now_day = datetime.datetime.now().strftime("%Y%m%d")
    image_path = base_dir + "/" + now_day + ".jpg"
    return image_path

def download_image(image_path):
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
        bing_web = requests.get("https://cn.bing.com")
        image_url = "https://cn.bing.com" + etree.HTML(bing_web.content).xpath("//link[@id=\"bgLink\"]/@href")[0].split("&")[0]
        image_title = str(etree.HTML(bing_web.content).xpath("//a[@class=\"sc_light\"]/@title")[0])
        print(image_url, image_title, datetime.datetime.now().strftime("%Y%m%d"))
    except Exception as e:
        window_alarm("获取bing壁纸图片url时失败，原因：" + str(e), ALARM_EXIT)
        return None

    image_contents = requests.get(image_url, headers=header)
    with open(image_path, "wb") as fout:
        fout.write(image_contents.content)

    return image_title

def set_mac_wallpaper(image_title, image_path):
    set_wallpaper_script = "/usr/bin/osascript<<END\n" +\
    "tell application \"Finder\"\n" +\
    "set desktop picture to POSIX file \"%s\"\n" % str(image_path) +\
    "end tell\n" +\
    "END"
    ret = subprocess.Popen(set_wallpaper_script, shell=True)

    if image_title:
        window_alarm("今日壁纸设置成功！" + "\n\n" + image_title)
    else:
        window_alarm("今日壁纸设置成功！")

def run_all():
    base_path = get_base_path()
    image_path = get_image_path(base_path)
    if not os.path.exists(image_path):
        image_title = download_image(image_path)
    else:
        image_title = None
    set_mac_wallpaper(image_title, image_path)

if __name__ == "__main__":
    run_all()
