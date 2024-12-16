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
from exceptiongroup import catch

from config import URLs
from config import SportsArea
from utils.webvpn import WebVPN
import logging

logger = logging.getLogger("Task_AutoSports")
console = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)
logger.setLevel(logging.INFO)

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
    # ydxx_api = WebVPN.encrypt_url(URLs.tmlyglpt_ydxx_api.format(SportsCourseId=URLs.SportsCourseId, username=username), webvpn.wrdvpnKey, webvpn.wrdvpnIV)
    # response = requests.get(ydxx_api, headers=headers, cookies=cookies)
    # if response.status_code != 200:
    #     logger.warning("获取当日签到状态失败")
    #     return
    # response_text = json.loads(response.text)
    # if response_text['code'] != 200 or response_text['msg'] != '操作成功！':
    #     logger.warning("获取当日签到状态失败")
    #     return
    # if response_text['data']['total'] == 0:
    #     logger.info("无签到记录，开始签到")
    #     mode = 1
    # else:
    #     info = response_text['data']['rows'][0]
    #     if info['dayTime'] != datetime.now().strftime("%Y%m%d"):
    #         logger.info("无签到记录，开始签到")
    #         mode = 1
    #     else:
    #         if info['score'] == 1:
    #             logger.info("今日已完成，无需重复打卡")
    #             return
    #         start_time = datetime.strptime(info['startTime'], "%Y-%m-%d %H:%M:%S")
    #         end_time = datetime.strptime(info['endTime'], "%Y-%m-%d %H:%M:%S") if info['endTime'] else None
    #         if end_time and end_time > start_time:
    #             logger.info("已有记录签到时间不足未成功打卡，将重新签到")
    #             mode = 1
    #         else:
    #             duration = datetime.now() - start_time
    #             if duration.total_seconds() / 60 < 30:
    #                 logger.warning("间隔时间未到30分钟，请稍后再试")
    #                 return
    #             else:
    #                 logger.info("开始签退")
    #                 mode = 2

    latitude, longitude = random_point_nearby(sign_center[0], sign_center[1], 10)

    # if mode == 1:
    #     api = WebVPN.encrypt_url(URLs.tmlyglpt_ydqd_api, webvpn.wrdvpnKey, webvpn.wrdvpnIV)
    #     data = json.dumps({
    #         'courseInfoId': URLs.SportsCourseId,
    #         'latitude': latitude,
    #         'longitude': longitude,
    #         'sportType': '2',
    #     })
    # elif mode == 2:
    #     api = WebVPN.encrypt_url(URLs.tmlyglpt_ydqt_api, webvpn.wrdvpnKey, webvpn.wrdvpnIV)
    #     data = json.dumps({
    #         'latitude': f'{latitude: .6f}',
    #         'longitude': f'{longitude: .6f}',
    #     })
    # else:
    #     return
    #
    # response = requests.post(api, data=data, headers=headers, cookies=cookies)
    # msg = json.loads(response.text)['msg']
    #
    # logger.info(msg)


    api = WebVPN.encrypt_url(URLs.tmlyglpt_ydqt_api, webvpn.wrdvpnKey, webvpn.wrdvpnIV)
    data = json.dumps({
        'latitude': f'{latitude: .6f}',
        'longitude': f'{longitude: .6f}',
    })
    response = requests.post(api, data=data, headers=headers, cookies=cookies)
    if json.loads(response.text)['success']:
        logger.info("签退成功")
        return
    logger.info("开始签到")
    api = WebVPN.encrypt_url(URLs.tmlyglpt_ydqd_api, webvpn.wrdvpnKey, webvpn.wrdvpnIV)
    data = json.dumps({
        'courseInfoId': URLs.SportsCourseId,
        'latitude': latitude,
        'longitude': longitude,
        'sportType': '2',
    })
    response = requests.post(api, data=data, headers=headers, cookies=cookies)
    msg = json.loads(response.text)['msg']
    logger.info(msg)


if __name__ == '__main__':

    auths = os.environ.get('XJTU_AUTH').split('&')

    logger.info(f"开始批量执行【自动运动签到】任务")
    logger.info(f"共有{len(auths)}个账号")

    for auth in auths:
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
        time.sleep(10)
