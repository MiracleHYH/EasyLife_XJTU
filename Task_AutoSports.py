import json
import os
import random
import time
from argparse import ArgumentParser

import requests

from config import URLs
from utils.webvpn import WebVPN

# import logging
#
# logger = logging.getLogger(__name__)
# console = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# console.setFormatter(formatter)
# logger.addHandler(console)

ll_map_rect = [
    [34.257162, 108.650036],
    [34.262517, 108.660423],
    [34.257704, 108.666624],
    [34.257704, 108.666624]
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
    try:
        webvpn = WebVPN()
        webvpn.login(username, password)
        webvpn.go(URLs.tmlyglpt_login_url)
        time.sleep(3)

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
            data = json.dumps({})

        response = requests.post(api, data=data, headers=headers, cookies=cookies)
        msg = json.loads(response.text)['msg']

        # logger.info("执行结果:" + msg)
        print("执行结果:" + msg)
    except Exception as e:
        # logger.info("执行失败:" + str(e))
        print("执行失败:" + str(e))

if __name__ == '__main__':
    parser = ArgumentParser()
    # parser.add_argument('-u', '--username', required=True, help='账号')
    # parser.add_argument('-p', '--password', required=True, help='密码')
    parser.add_argument('-m', '--mode', required=True, type=int, choices=[1, 2],
                        help='运行模式.1为运动签到;2为运动签退')
    args = parser.parse_args()
    #
    # username = args.username
    # password = args.password
    _mode = args.mode

    auths = os.environ.get('XJTU_AUTH').split('&')

    # logger.info("开始批量执行" + "签到" if _mode == 1 else "签退" + "任务")
    # logger.info("共有" + str(len(auths)) + "个账号")

    print("开始批量执行" + "签到" if _mode == 1 else "签退" + "任务")
    print("共有" + str(len(auths)) + "个账号")

    for auth in auths:
        time.sleep(10 + 20 * random.random())
        _username, _password = auth.split('$$')
        # 打印每个信息并分割
        # logger.info("开始执行" + _username + "的任务")
        print("开始执行" + _username + "的任务")
        work(_username, _password, _mode)
        # logger.info("执行" + _username + "的任务结束")
        print("执行" + _username + "的任务结束")