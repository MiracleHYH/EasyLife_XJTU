from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import URLs


def login(driver, wait, username, password):
    payload = {
        'username': username,
        'password': password,
    }
    
    driver.get(URLs.webvpn_login_url)
    
    username = wait.until(EC.presence_of_element_located((By.NAME, 'username')))
    password = wait.until(EC.presence_of_element_located((By.NAME, 'pwd')))

    username.send_keys(payload['username'])
    password.send_keys(payload['password'])

    password.send_keys(Keys.RETURN)
