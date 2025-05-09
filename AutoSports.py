# Author: Miracle24
# Time: 2024/1/8
# Desc: XJTU研究生自动运动打卡

import json
import random
import math
import time
from argparse import ArgumentParser
from time import sleep

import requests
from datetime import datetime

from config import URLs
from config import SportsArea
from utils.common import login, create_logger, create_browser

logger = create_logger("AutoSports")

sign_center = SportsArea.cxg_tjc

def random_point_nearby(latitude, longitude, radius_meters=10):
    # 地球半径（米）
    earth_radius = 6378137.0

    # 随机方位角度和距离
    random_angle = random.uniform(0, 2 * math.pi)
    random_distance = random.uniform(0, radius_meters)

    # 分解随机距离为纬度和经度方向上的分量
    delta_lat = math.cos(random_angle) * random_distance
    delta_lon = math.sin(random_angle) * random_distance

    # 计算新纬度
    delta_lat_deg = delta_lat / earth_radius * 180.0 / math.pi
    new_latitude = latitude + delta_lat_deg

    # 计算新经度
    delta_lon_deg = delta_lon / (earth_radius * math.cos(math.pi * latitude / 180.0)) * 180.0 / math.pi
    new_longitude = longitude + delta_lon_deg

    return new_latitude, new_longitude


def work(username, password):
    driver, wait = create_browser()
    login(driver, wait, URLs.tmlyglpt_login_url, username, password)
    time.sleep(10)

    token = driver.execute_script("return localStorage.getItem('_token');")
    selenium_cookies = driver.get_cookies()
    cookies = {c['name']: c['value'] for c in selenium_cookies}

    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Token': token,
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
    }

    latitude, longitude = random_point_nearby(sign_center[0], sign_center[1], 10)

    data = json.dumps({
        'latitude': f'{latitude: .6f}',
        'longitude': f'{longitude: .6f}',
    })
    response = requests.post(URLs.tmlyglpt_ydqt_api, data=data, headers=headers, cookies=cookies)
    if json.loads(response.text)['success']:
        logger.info("签退成功")
        return
    logger.info("开始签到")
    data = json.dumps({
        'courseInfoId': URLs.SportsCourseId,
        'latitude': latitude,
        'longitude': longitude,
        'sportType': '2',
    })
    response = requests.post(URLs.tmlyglpt_ydqd_api, data=data, headers=headers, cookies=cookies)
    msg = json.loads(response.text)['msg']
    logger.info(msg)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-u', '--username', required=True, help='账号')
    parser.add_argument('-p', '--password', required=True, help='密码')

    args = parser.parse_args()

    _username = args.username
    _password = args.password

    try:
        logger.info("开始执行" + _username + "的任务")
        work(_username, _password)
        logger.info("执行" + _username + "的任务结束")
    except Exception as e:
        logger.warning("账号" + _username + "执行失败")
        logger.error(str(e))
