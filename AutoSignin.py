# Author: Miracle24
# Time: 2025/2/28
# Desc: XJTU_IAIR研究生自动签到

from argparse import ArgumentParser
from time import sleep

from config import URLs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import logging

logger = logging.getLogger("AutoSports")
console = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)
logger.setLevel(logging.INFO)


def work(username, password):
    options = Options()
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

    # signin_tab = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='treeitem' and .//div[contains(@class, 'content-title') and text()='打卡']]")))
    # signin_tab.click()
    sleep(5)
    driver.get(URLs.iair_signin_form_url)
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
        "latitude": 34.24764385304397,   # 纬度 (Latitude)
        "longitude": 108.98003946842356, # 经度 (Longitude)
        "accuracy": 100        # 精度 (Accuracy)
    })
    location_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'location-btn')))
    location_button.click()
    confirm_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//div[contains(@class, 'handle-btn') and normalize-space(text())='确定']")
    ))
    sleep(3)
    confirm_button.click()

    sleep(3)
    submit_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//div[contains(@class, 'ry-form__fill-show-btn') and contains(normalize-space(.), '提交')]")
    ))
    submit_button.click()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-u', '--username', required=True, help='账号')
    parser.add_argument('-p', '--password', required=True, help='密码')

    args = parser.parse_args()

    _username = args.username
    _password = args.password

    max_trial = 3
    while max_trial > 0:
        try:
            logger.info(f"开始执行{_username}的任务, 剩余尝试次数{max_trial}")
            work(_username, _password)
            logger.info(f"账号{_username}执行成功")
            break
        except Exception as e:
            logger.warning(f"账号{_username}执行失败")
            logger.error(str(e))
            max_trial -= 1
            sleep(10)