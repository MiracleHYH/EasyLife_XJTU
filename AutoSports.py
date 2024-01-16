# Author: Miracle24
# Time: 2024/1/8
# Desc: XJTU研究生自动运动打卡

import json
import random
import time
from argparse import ArgumentParser

import requests

from config import URLs
from utils.webvpn import WebVPN

import logging

logger = logging.getLogger("AutoSports")
console = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)
logger.setLevel(logging.INFO)

ll_map_rect = [
    [34.25701, 108.652818],
    [34.25822, 108.655327],
    [34.257277, 108.656004],
    [34.256025, 108.653533]
]


def generate_random_point_in_rectangle(rect):
    # Generate two random weights
    r1, r2 = random.random(), random.random()

    # Linearly interpolate between top-left and top-right for the first point
    top_x = rect[0][1] * (1 - r1) + rect[1][1] * r1
    top_y = rect[0][0] * (1 - r1) + rect[1][0] * r1

    # Linearly interpolate between bottom-left and bottom-right for the second point
    bottom_x = rect[3][1] * (1 - r1) + rect[2][1] * r1
    bottom_y = rect[3][0] * (1 - r1) + rect[2][0] * r1

    # Finally, linearly interpolate between the two points to get the random point inside the rectangle
    final_x = top_x * (1 - r2) + bottom_x * r2
    final_y = top_y * (1 - r2) + bottom_y * r2

    return f'{final_y:.6f}', f'{final_x:.6f}'


def work(username, password, mode):
    webvpn = WebVPN()
    webvpn.login(username, password)
    webvpn.go(URLs.tmlyglpt_login_url)
    time.sleep(10)

    token = webvpn.driver.execute_script("return localStorage.getItem('__1__token');")
    selenium_cookies = webvpn.driver.get_cookies()
    cookies = {c['name']: c['value'] for c in selenium_cookies}

    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        # 'Host': 'webvpn.xjtu.edu.cn',
        # 'Origin': 'https://webvpn.xjtu.edu.cn',
        # 'Referer': WebVPN.encrypt_url(WebVPN.encrypt_url(URLs.tmlyglpt_ydqd_url), webvpn.wrdvpnKey, webvpn.wrdvpnIV),
        'Token': token,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    if mode == 1:
        api = WebVPN.encrypt_url(URLs.tmlyglpt_ydqd_api, webvpn.wrdvpnKey, webvpn.wrdvpnIV)
        latitude, longitude = generate_random_point_in_rectangle(ll_map_rect)
        data = json.dumps({
            'courseInfoId': '1698877075970076673',
            'latitude': latitude,
            'longitude': longitude,
            'sportType': '2',
        })
    else:
        api = WebVPN.encrypt_url(URLs.tmlyglpt_ydqt_api, webvpn.wrdvpnKey, webvpn.wrdvpnIV)
        latitude, longitude = generate_random_point_in_rectangle(ll_map_rect)
        data = json.dumps({
            'latitude': latitude,
            'longitude': longitude,
        })

    response = requests.post(api, data=data, headers=headers, cookies=cookies)
    msg = json.loads(response.text)['msg']

    logger.info("执行结果:" + msg)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-u', '--username', required=True, help='账号')
    parser.add_argument('-p', '--password', required=True, help='密码')
    parser.add_argument('-m', '--mode', required=True, type=int, choices=[1, 2],
                        help='运行模式.1为运动签到;2为运动签退')
    args = parser.parse_args()

    _username = args.username
    _password = args.password
    _mode = args.mode

    try:
        logger.info("开始执行" + _username + "的任务")
        work(_username, _password, _mode)
        logger.info("执行" + _username + "的任务结束")
    except Exception as e:
        logger.warning("账号" + _username + "执行失败")
        logger.error(str(e))
