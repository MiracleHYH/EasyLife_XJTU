from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import logging


def create_logger(logger_name):
    logger = logging.getLogger(logger_name)
    console = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)
    logger.setLevel(logging.INFO)
    return logger


def create_browser():
    options = Options()
    # options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    # options.add_argument("--incognito")
    options.add_experimental_option("prefs", {"profile.default_content_setting_values.geolocation": 1})
    options.add_experimental_option("mobileEmulation", {"deviceName": "iPhone 14 Pro Max"})
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    return driver, wait


def login(driver, wait, url, username, password):
    driver.get(url)

    username_input = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='isMObil']//input[@class='username']")))
    password_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='isMObil']//input[@class='pwd']")))

    username_input.send_keys(username)
    password_input.send_keys(password)

    password_input.send_keys(Keys.RETURN)