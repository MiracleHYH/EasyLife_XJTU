# Author: Miracle24
# Time: 2024/1/9
# Desc: XJTU研究生自动评教

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from utils.webvpn import WebVPN
from config import URLs
import time

def get_column_items_from_table(table, column_idx):
    column = table.find_elements(By.XPATH, f"//div[@column='{column_idx}']")[0]
    return column.find_elements(By.TAG_NAME, "div")

webvpn = WebVPN(debug=True)
webvpn.login("4123155021", "Zgyfjch111024!")
webvpn.go(URLs.yjszhpjxt_url)
table = webvpn.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[view_id='sshdMainTable']")))
time.sleep(3)
num_course = int(table.get_attribute("aria-rowcount"))
table_content = table.find_element(By.CLASS_NAME, "webix_ss_center_scroll")
semester_list = get_column_items_from_table(table_content, 0)
class_list = get_column_items_from_table(table_content, 1)
course_list = get_column_items_from_table(table_content, 2)
teacher_list = get_column_items_from_table(table_content, 3)
button_list = get_column_items_from_table(table_content, 5)
print(f"共有{num_course}门课程需要评教")
for idx in range(num_course):
    print(f"开始评教第{idx + 1}门课程: {semester_list[idx].text}-{course_list[idx].text}-{class_list[idx].text} ({teacher_list[idx].text})")
input("Press any key to continue...")