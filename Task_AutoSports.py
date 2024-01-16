# Author: Miracle24
# Time: 2024/1/8
# Desc: XJTU研究生自动运动打卡
"""
new Env('XJTU_研究生自动运动打卡');
# cron: 0 19,20 * * *
"""
from datetime import datetime
import json
import os
import random
import math
import time
import requests
from config import URLs
from utils.webvpn import WebVPN
import logging

logger = logging.getLogger("Task_AutoSports")
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

    info = None

    # 获取当日签到状态
    logger.info("获取当日签到状态")
    ydxx_api = WebVPN.encrypt_url(URLs.tmlyglpt_ydxx_api.format(username=username), webvpn.wrdvpnKey, webvpn.wrdvpnIV)
    response = requests.get(ydxx_api, headers=headers, cookies=cookies)
    if response.status_code != 200:
        logger.warning("获取当日签到状态失败")
        return
    response_text = json.loads(response.text)
    if response_text['code'] != 200 or response_text['msg'] != '操作成功！':
        logger.warning("获取当日签到状态失败")
        return
    if response_text['data']['total'] == 0:
        logger.info("无签到记录，开始签到")
        mode = 1
    else:
        info = response_text['data']['rows'][0]
        if info['dayTime'] != datetime.now().strftime("%Y%m%d"):
            logger.info("无签到记录，开始签到")
            mode = 1
        else:
            if info['score'] == 1:
                logger.info("今日已完成，无需重复打卡")
                return
            start_time = datetime.strptime(info['startTime'], "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(info['endTime'], "%Y-%m-%d %H:%M:%S") if info['endTime'] else None
            if end_time and end_time > start_time:
                logger.info("已有记录签到时间不足未成功打卡，将重新签到")
                mode = 1
            else:
                duration = start_time - datetime.now()
                if duration.total_seconds() / 60 < 30:
                    logger.warning("间隔时间未到30分钟，请稍后再试")
                    return
                else:
                    logger.info("开始签退")
                    mode = 2

    if mode == 1:
        api = WebVPN.encrypt_url(URLs.tmlyglpt_ydqd_api, webvpn.wrdvpnKey, webvpn.wrdvpnIV)
        latitude, longitude = generate_random_point_in_rectangle(ll_map_rect)
        data = json.dumps({
            'courseInfoId': '1698877075970076673',
            'latitude': latitude,
            'longitude': longitude,
            'sportType': '2',
        })
    elif mode == 2:
        api = WebVPN.encrypt_url(URLs.tmlyglpt_ydqt_api, webvpn.wrdvpnKey, webvpn.wrdvpnIV)
        assert info is not None
        latitude, longitude = random_point_nearby(float(info['latitude']), float(info['longitude']), 10)
        data = json.dumps({
            'latitude': f'{latitude: .6f}',
            'longitude': f'{longitude: .6f}',
        })
    else:
        return

    response = requests.post(api, data=data, headers=headers, cookies=cookies)
    msg = json.loads(response.text)['msg']

    logger.info(msg)


if __name__ == '__main__':

    auths = os.environ.get('XJTU_AUTH').split('&')

    logger.info(f"开始批量执行【自动运动签到】任务")
    logger.info(f"共有{len(auths)}个账号")

    for auth in auths:
        time.sleep(10 + 20 * random.random())
        print("-------------------------------------")
        try:
            _username, _password = auth.split('$$')
            logger.info(f"开始执行账号: {_username}")
            work(_username, _password)
            logger.info("执行结束")
        except Exception as e:
            logger.warning("执行失败")
            logger.error(str(e))
        print("-------------------------------------")
