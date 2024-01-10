# Author: Miracle24
# Time: 2024/1/9
# Desc: XJTU研究生自动评教

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from utils.webvpn import WebVPN
from config import URLs
from utils.language import detect_language
import time
import os
import random


szkc_list = [
    "工程伦理",
    "中国特色社会主义",
    "自然辩证法",
    "马克思主义"
]

def is_szkc(course_name):
    for szkc in szkc_list:
        if szkc in course_name:
            return True
    return False


def get_column_items_from_table(table, column_idx):
    column = table.find_element(By.XPATH, f"./div[@column='{column_idx}']")
    return column.find_elements(By.TAG_NAME, "div")


def get_course_info(webvpn, pj_courses):
    pj_courses_rearranged = {}
    en_course_name = ""
    full_en_course_name = ""
    for (course_name, course_year) in pj_courses:
        if "学术英语" in course_name or "专业英语" in course_name:
            en_course_name = course_name.split("-")[-1]
            full_en_course_name = course_name
        if course_name not in pj_courses_rearranged:
            pj_courses_rearranged[course_name] = []
        if course_year not in pj_courses_rearranged.get(course_name):
            pj_courses_rearranged[course_name].append(course_year)
    
    course_info = {}
    course_list = []

    src_window = webvpn.driver.current_window_handle
    new_window = webvpn.open(URLs.yjsglxxxt_url)
    webvpn.switch_to_window(new_window)
    time.sleep(5)
    webvpn.go(URLs.yjsglxxxt_wdpyjh_url)
    time.sleep(5)

    pyjh_table = webvpn.driver.find_element(By.ID, "sample-table-1")
    pyjh_rows = pyjh_table.find_elements(By.XPATH, "./tbody/tr")
    for row in pyjh_rows:
        cols = row.find_elements(By.XPATH, "./td")
        course_code = cols[2].text
        course_name = cols[4].text
        course_type = cols[5].text
        if course_name in pj_courses_rearranged:
            for course_year in pj_courses_rearranged.get(course_name):
                course_list.append((course_code, course_name, course_type, course_year))
        elif course_name == en_course_name:
            course_list.append((course_code, full_en_course_name, course_type, course_year))
    
    # 枚举每门课程
    
    for (course_code, course_name, course_type, course_year) in course_list:
        print(f"开始获取课程: {course_name}-{course_year} 的信息")
        info = {}
        webvpn.go(URLs.yjsglxxxt_kckk_url.format(code=course_code, year=course_year))
        time.sleep(5)
        course_table = webvpn.driver.find_element(By.CLASS_NAME, "tblMain")
        if course_table is None:
            print(f"课程: {course_name}-{course_year} 的信息获取失败")
            continue
        course_cols = course_table.find_elements(By.XPATH, "./tbody/tr/td")
        for idx in range(0, len(course_cols), 2):
            if course_cols[idx].text == "课程简介:" or course_cols[idx].text == "教学日历:":
                continue
            if course_cols[idx].text == "课程教材" or course_cols[idx].text == "主要参考书:":
                books = []
                book_rows = course_cols[idx + 1].find_elements(By.XPATH, "./tbody/tr")
                for book_row in book_rows:
                    book_cols = book_row.find_elements(By.XPATH, "./td")
                    if book_cols[1].text != "无指定书籍":
                        books.append(book_cols[1].text)
                info[course_cols[idx].text] = books
                continue
            info[course_cols[idx].text] = course_cols[idx + 1].text
            info["课程类别"] = course_type
        course_info[(course_name, course_year)] = info
        print(f"课程: {course_name}-{course_year} 的信息获取完毕")
        
    webvpn.close_current_window()
    webvpn.switch_to_window(src_window)
    
    print("所有课程信息获取完毕")

    return course_info


def extract_text_from_column(column):
    return [item.text for item in column]


def work(username, password):
    webvpn = WebVPN(debug=True)
    webvpn.login(username, password)

    webvpn.go(URLs.yjszhpjxt_url)
    time.sleep(5)

    pj_list = []
    pj_columns = webvpn.driver.find_elements(By.XPATH, "//div[@view_id='sshdMainTable']/div[2]/div[2]/div/div")
    num_pj = len(pj_columns[0].find_elements(By.XPATH, "./div"))
    for row_idx in range(num_pj):
        task = {
            'semester': pj_columns[0].find_element(By.XPATH, f"./div[{row_idx + 1}]").text,
            'class': pj_columns[1].find_element(By.XPATH, f"./div[{row_idx + 1}]").text,
            'name': pj_columns[2].find_element(By.XPATH, f"./div[{row_idx + 1}]").text,
            'teacher': pj_columns[3].find_element(By.XPATH, f"./div[{row_idx + 1}]").text
        }
        pj_list.append(task)

    print(f"总计{num_pj}个评教任务")
    
    course_info = get_course_info(webvpn, [(item.get('name'), item.get('semester')[:4]) for item in pj_list])

    for (row_idx, pj) in enumerate(pj_list):
        print(f"开始评教: {pj.get('semester')}-{pj.get('name')}-{pj.get('class')} ({pj.get('teacher')})")
        webvpn.refresh()
        time.sleep(5)
        
        
        pj_button = webvpn.driver.find_element(By.XPATH, f"//div[@view_id='sshdMainTable']/div[2]/div[2]/div/div[6]/div[{row_idx + 1}]//button")
        if pj_button.text == "修改":
            print("已评教，跳过")
            continue
        webvpn.move_to_element(pj_button)
        pj_button.click()
        src_window = webvpn.current_window()
        webvpn.switch_to_window(webvpn.window_handles()[-1])
        time.sleep(5)
        
        info = course_info.get((pj.get('name'), pj.get('semester')[:4]))
        
        submit_button = webvpn.driver.find_element(By.XPATH, "//div[@view_id='submitButton']/div/button")
        comment_table = webvpn.driver.find_element(By.XPATH, "//div[@view_id='zbForm']/div/div")
        comment_rows = comment_table.find_elements(By.XPATH, "./div")
        # row 0: 课程名称,上课教师 (会自动填充，不用填写)
        
        # row 1: 教材情况 (根据课程信息填充)
        # row 2: 教材名称, 教材使用语言 (根据课程信息填充)
        webvpn.move_to_element(comment_rows[1])
        if not info or not info.get("课程教材") or len(info.get("课程教材")) == 0:
            comment_rows[1].find_element(By.XPATH, "./div/div/div/div[1]").click()
        else:
            jc = info.get("课程教材")
            comment_rows[1].find_element(By.XPATH, "./div/div/div/div[3]").click()
            webvpn.move_to_element(comment_rows[2])
            comment_rows[2].find_element(By.XPATH, "./div[1]/div/input").send_keys(jc.join(","))
            comment_rows[2].find_element(By.XPATH, "./div[2]/div/input").send_keys([detect_language(jc_item) for jc_item in jc].join(","))
            
        # row 3: 授课语言, 选修情况 (根据课程信息填充)
        webvpn.move_to_element(comment_rows[3])
        if not info or not info.get("授课语言"):
            comment_rows[3].find_element(By.XPATH, "./div[1]/div/div/div[3]").click()
        else:
            skyy = info.get("授课语言")
            if "全英文" in skyy:
                comment_rows[3].find_element(By.XPATH, "./div[1]/div/div/div[1]").click()
            elif "中英文" in skyy:
                comment_rows[3].find_element(By.XPATH, "./div[1]/div/div/div[2]").click()
            elif "全中文" in skyy:
                comment_rows[3].find_element(By.XPATH, "./div[1]/div/div/div[3]").click()
            else:
                comment_rows[3].find_element(By.XPATH, "./div[1]/div/div/div[3]").click()
        if not info or not info.get("课程类别"):
            comment_rows[3].find_element(By.XPATH, "./div[2]/div/div/div[2]").click()
        else:
            kclb = info.get("课程类别")
            if "学位课" in kclb:
                comment_rows[3].find_element(By.XPATH, "./div[2]/div/div/div[1]").click()
            else:
                comment_rows[3].find_element(By.XPATH, "./div[2]/div/div/div[2]").click()
                
        # row 4 Header: 评价指标 指标描述 评价等级
        
        # row 5 教学态度
        webvpn.move_to_element(comment_rows[5])
        comment_rows[5].find_element(By.XPATH, "./div[3]/div/div/div[1]").click()
        
        # row 6 教学内容
        webvpn.move_to_element(comment_rows[6])
        comment_rows[6].find_element(By.XPATH, "./div[3]/div/div/div[1]").click()
        
        # row 7 教学方法
        webvpn.move_to_element(comment_rows[7])
        comment_rows[7].find_element(By.XPATH, "./div[3]/div/div/div[1]").click()
        
        # row 8 教学效果 (系统不能都选优秀, 教学效果选良好)
        webvpn.move_to_element(comment_rows[8])
        comment_rows[8].find_element(By.XPATH, "./div[3]/div/div/div[2]").click()
        
        # row 9 任课教师给我的总体印象是
        webvpn.move_to_element(comment_rows[9])
        comment_rows[9].find_element(By.XPATH, "./div[2]/div/textarea").send_keys("老师认真负责，教学内容充实，教学方法多样，教学效果良好。")
        
        # row 10 对本门课程我有一些建议供任课教师参考
        webvpn.move_to_element(comment_rows[10])
        comment_rows[10].find_element(By.XPATH, "./div[2]/div/textarea").send_keys("无")
        
        # row 11 对教学资源（教室、设备等）我有一些改进建议供相关部门参考（对课程采集）
        webvpn.move_to_element(comment_rows[11])
        comment_rows[11].find_element(By.XPATH, "./div[2]/div/textarea").send_keys("无")
        
        # row 12 该门课程是否在教学中融入了思想政治教育内容 (对	包含szkc列表关键字的课程 选是，其他选否)
        webvpn.move_to_element(comment_rows[12])
        if is_szkc(pj.get('name')):
            comment_rows[12].find_element(By.XPATH, "./div[2]/div/div/div[1]").click()
        else:
            comment_rows[12].find_element(By.XPATH, "./div[2]/div/div/div[2]").click()
        webvpn.close_current_window()
        webvpn.switch_to_window(src_window)
    input("Press any key to continue...")


if __name__ == '__main__':
    auths = os.environ.get('XJTU_AUTH').split('&')

    for auth in auths:
        try:
            time.sleep(10 + 20 * random.random())
            _username, _password = auth.split('$$')
            # 打印每个信息并分割
            print("-------------------------------------")
            print("开始执行" + _username + "的任务")
            work(_username, _password)
            print("执行" + _username + "的任务结束")
        except Exception as e:
            print("账号" + _username + "执行失败")
            print(e)