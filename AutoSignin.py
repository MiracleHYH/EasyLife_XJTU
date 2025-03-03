# Author: Miracle24
# Time: 2025/2/28
# Desc: XJTU_IAIR研究生自动签到

from argparse import ArgumentParser
from time import sleep

from config import URLs
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from utils.common import login, create_logger, create_browser

logger = create_logger("AutoSigninIAIR")


def work(username, password):
    driver, wait = create_browser()

    # logger.info(f"账号{username}设置地理位置")
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
        "latitude": 34.24764385304397,  # 纬度 (Latitude)
        "longitude": 108.98003946842356,  # 经度 (Longitude)
        "accuracy": 100  # 精度 (Accuracy)
    })

    login(driver, wait, URLs.iair_signin_home_url, username, password)

    location_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'ry-form__location-compact')]//button")))
    location_button.click()
    sleep(10)

    # logger.info(f"账号{username}点击获取地理位置")
    confirm_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//div[contains(@class, 'handle-btn') and normalize-space(text())='确定']")
    ))
    confirm_button.click()
    # logger.info(f"账号{username}确认地理位置")

    sleep(3)
    submit_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//div[contains(@class, 'only-btn') and normalize-space(text())='提交']")
    ))
    # logger.info(f"账号{username}点击提交按钮")
    submit_button.click()
    # driver.execute_script("arguments[0].click();", submit_button)
    # time.sleep(5)
    # logger.info(f"账号{username}提交成功,等待成功确认")
    wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//div[@class='van-toast__text' and normalize-space(text())='提交成功']")
    ))
    driver.quit()


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
