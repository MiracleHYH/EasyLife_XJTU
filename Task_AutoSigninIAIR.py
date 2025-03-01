# Author: Miracle24
# Time: 2025/2/28
# Desc: XJTU_IAIR研究生自动签到
"""
new Env('XJTU_IAIR研究生自动签到');
# cron: 50 7,13 * * *
"""

import os
import time
from random import random
from time import sleep
from config import URLs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import datetime

import logging

logger = logging.getLogger("Task_AutoSigninIAIR")
console = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)
logger.setLevel(logging.INFO)


def work(username, password):
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    # options.add_experimental_option("mobileEmulation", {"deviceName": "iPhone 14 Pro Max"})
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.geolocation": 1  # 允许地理位置 (Allow geolocation)
    })
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    driver.get(URLs.iair_signin_home_url)
    username_input = wait.until(EC.presence_of_element_located((By.NAME, 'username')))
    password_input = wait.until(EC.presence_of_element_located((By.NAME, 'pwd')))

    username_input.send_keys(username)
    password_input.send_keys(password)

    password_input.send_keys(Keys.RETURN)

    # logger.info(f"账号{username}登录成功")

    # signin_tab = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='treeitem' and .//div[contains(@class, 'content-title') and text()='打卡']]")))
    # signin_tab.click()
    sleep(10)


    driver.get(URLs.iair_signin_form_url)
    sleep(10)
    # logger.info(f"账号{username}进入打卡页面")
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
        "latitude": 34.24764385304397,  # 纬度 (Latitude)
        "longitude": 108.98003946842356,  # 经度 (Longitude)
        "accuracy": 100  # 精度 (Accuracy)
    })
    # logger.info(f"账号{username}设置地理位置")
    location_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'location-btn')))
    location_button.click()
    # logger.info(f"账号{username}点击获取地理位置")
    sleep(10)
    confirm_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//div[contains(@class, 'handle-btn') and normalize-space(text())='确定']")
    ))
    confirm_button.click()
    # logger.info(f"账号{username}确认地理位置")

    sleep(10)
    submit_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//div[contains(@class, 'ry-form__fill-show-btn') and contains(normalize-space(.), '提交')]")
    ))
    # logger.info(f"账号{username}点击提交按钮")
    driver.execute_script("arguments[0].click();", submit_button)
    # time.sleep(5)
    # logger.info(f"账号{username}提交成功,等待成功确认")
    sleep(10)
    wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//div[@role='alert' and contains(normalize-space(.), '提交成功')]")
    ))

    # time.sleep(30000)
    # driver.execute_script("arguments[0].scrollIntoView();", submit_button)
    # sleep(3)
    # submit_button.click()
    # time.sleep(3)


if __name__ == '__main__':
    today = datetime.date.today()
    weekday_num = today.weekday()
    if weekday_num == 6:
        logger.info("周日不需要签到")
        exit(0)


    auths = os.environ.get('XJTU_IAIR_AUTH').split('&')

    logger.info(f"开始批量执行【IAIR自动签到】任务")
    logger.info(f"共有{len(auths)}个账号")

    # 在9~600秒内随机等待
    # sleep(int(9 + 591 * random()))

    for auth in auths:
        max_trial = 3
        while max_trial > 0:
            max_trial -= 1
            try:
                _username, _password = auth.split('$$')
                logger.info(f"开始执行{_username}的任务, 剩余尝试次数{max_trial}")
                work(_username, _password)
                logger.info(f"账号{_username}执行成功")
                break
            except Exception as e:
                logger.warning(f"执行失败")
                logger.error(str(e))
                sleep(10)
        sleep(int(9 + 10 * random()))