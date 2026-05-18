# -*- coding:utf-8 -*-
"""
Author: BigCat
"""
import argparse
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from loguru import logger
from config import name_path, data_file_name

parser = argparse.ArgumentParser()
parser.add_argument('--name', default="ssq", type=str, help="选择爬取数据: 双色球/大乐透")
args = parser.parse_args()

no_proxy = {"http": None, "https": None}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_url(name):
    """
    :param name: 玩法名称
    :return:
    """
    base_url = "https://datachart.500.com/{}/history/"
    return base_url.format(name)


def get_current_number(name):
    """ 获取最新一期数字
    :return: int
    """
    url = get_url(name)
    r = requests.get("{}newinc/history.php".format(url), verify=False, proxies=no_proxy, headers=headers)
    r.encoding = "gb2312"
    soup = BeautifulSoup(r.text, "lxml")
    tbody = soup.find("tbody", attrs={"id": "tdata"})
    if tbody is None:
        logger.error("无法获取数据，网站结构可能已变化。返回内容: {}".format(r.text[:500]))
        raise Exception("获取数据失败: tbody#tdata 未找到")
    trs = tbody.find_all("tr")
    current_num = trs[0].find_all("td")[0].get_text().strip()
    return current_num


def spider(name, start, end, mode):
    """ 爬取历史数据
    :param name 玩法
    :param start 开始一期
    :param end 最近一期
    :param mode 模式，train：训练模式，predict：预测模式（训练模式会保持文件）
    :return:
    """
    url = get_url(name)
    full_url = "{}newinc/history.php?start={}&end={}".format(url, start, end)
    r = requests.get(url=full_url, verify=False, proxies=no_proxy, headers=headers)
    r.encoding = "gb2312"
    soup = BeautifulSoup(r.text, "lxml")
    tbody = soup.find("tbody", attrs={"id": "tdata"})
    if tbody is None:
        logger.error("无法获取数据，网站结构可能已变化")
        return pd.DataFrame()
    trs = tbody.find_all("tr")
    data = []
    for tr in trs:
        item = dict()
        if name == "ssq":
            item[u"期数"] = tr.find_all("td")[0].get_text().strip()
            for i in range(6):
                item[u"红球_{}".format(i+1)] = tr.find_all("td")[i+1].get_text().strip()
            item[u"蓝球"] = tr.find_all("td")[7].get_text().strip()
            data.append(item)
        elif name == "dlt":
            item[u"期数"] = tr.find_all("td")[0].get_text().strip()
            for i in range(5):
                item[u"红球_{}".format(i+1)] = tr.find_all("td")[i+1].get_text().strip()
            for j in range(2):
                item[u"蓝球_{}".format(j+1)] = tr.find_all("td")[6+j].get_text().strip()
            data.append(item)
        else:
            logger.warning("抱歉，没有找到数据源！")

    if mode == "train":
        df = pd.DataFrame(data)
        df.to_csv("{}{}".format(name_path[name]["path"], data_file_name), encoding="utf-8")
        return pd.DataFrame(data)
    elif mode == "predict":
        return pd.DataFrame(data)


def run(name):
    """
    :param name: 玩法名称
    :return:
    """
    current_number = get_current_number(name)
    logger.info("【{}】最新一期期号：{}".format(name_path[name]["name"], current_number))
    logger.info("正在获取【{}】数据。。。".format(name_path[name]["name"]))
    if not os.path.exists(name_path[name]["path"]):
        os.makedirs(name_path[name]["path"])
    data = spider(name, 1, current_number, "train")
    if "data" in os.listdir(os.getcwd()):
        logger.info("【{}】数据准备就绪，共{}期, 下一步可训练模型...".format(name_path[name]["name"], len(data)))
    else:
        logger.error("数据文件不存在！")


if __name__ == "__main__":
    if not args.name:
        raise Exception("玩法名称不能为空！")
    else:
        run(name=args.name)