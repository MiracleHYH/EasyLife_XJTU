# Author: Miracle24
# Time: 2024/1/9
# Desc: XJTU研究生自动评教

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from utils.webvpn import WebVPN
from config import URLs
import time
from argparse import ArgumentParser


def get_column_items_from_table(table, column_idx):
    column = table.find_elements(By.XPATH, f"//div[@column='{column_idx}']")[0]
    return column.find_elements(By.TAG_NAME, "div")


def work(username, password):
    webvpn = WebVPN(debug=True)
    webvpn.login(username, password)
    webvpn.go(URLs.yjszhpjxt_url)
    table = webvpn.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[view_id='sshdMainTable']")))
    time.sleep(3)
    num_course = int(table.get_attribute("aria-rowcount"))
    table_content = table.find_element(By.CLASS_NAME, "webix_ss_center_scroll")
    semesters = get_column_items_from_table(table_content, 0)
    classes = get_column_items_from_table(table_content, 1)
    courses = get_column_items_from_table(table_content, 2)
    teachers = get_column_items_from_table(table_content, 3)
    buttons = get_column_items_from_table(table_content, 5)
    print(f"共有{num_course}门课程需要评教")
    for idx in range(num_course):
        print(
            f"开始评教第{idx + 1}门课程: {semesters[idx].text}-{courses[idx].text}-{classes[idx].text} ({teachers[idx].text})")
        button = buttons[idx].find_element(By.TAG_NAME, "button")
        button.click()
    input("Press any key to continue...")


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--username', type=str, required=True, help='账号')
    parser.add_argument('--password', type=str, required=True, help='密码')
    args = parser.parse_args()

    _username = args.username
    _password = args.password

    work(_username, _password)
