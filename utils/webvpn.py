from config import URLs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class WebVPN:
    def __init__(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def __del__(self):
        self.driver.quit()
        
    def login(self, username, password):
        self.driver.get(URLs.webvpn_login_url)
        
        username_input = self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))
        password_input = self.wait.until(EC.presence_of_element_located((By.NAME, 'pwd')))

        username_input.send_keys(username)
        password_input.send_keys(password)

        password_input.send_keys(Keys.RETURN)
        
        self.wait.until(EC.presence_of_element_located((By.ID, 'go')))
        self.wrdvpnKey = self.driver.execute_script("return wrdvpnKey;")
        self.wrdvpnIV = self.driver.execute_script("return wrdvpnIV;")

    def go(self, url):
        try:
            self.driver.get(WebVPN.encrypt_url(url, self.wrdvpnKey, self.wrdvpnIV))
        except ValueError:
            print('Invalid URL')
        
    @staticmethod
    def encrypt_url(url, key, iv):
        parsed_url = urlparse(url)
        if parsed_url.scheme == '' or parsed_url.netloc == '':
            raise ValueError('Invalid URL')
        
        scheme = parsed_url.scheme
        hostname = parsed_url.hostname
        port = parsed_url.port
        
        prefix = f'/{scheme}-{port}/' if port else f'/{scheme}/'
        
        s = url.split(parsed_url.netloc)
        suffix = s[1] if len(s) > 1 else ''
        
        return f'{URLs.webvpn_url}{prefix}{WebVPN.encrypt(hostname, key, iv)}{suffix}'
        
    @staticmethod
    def encrypt(text, key, iv):
        text_length = len(text)
        text = WebVPN.__text_right_append(text, 'utf8')
        key_bytes = key.encode('utf-8')
        iv_bytes = iv.encode('utf-8')
        text_bytes = text.encode('utf-8')

        cipher = Cipher(algorithms.AES(key_bytes), modes.CFB(iv_bytes), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypt_bytes = encryptor.update(text_bytes) + encryptor.finalize()

        return iv_bytes.hex() + encrypt_bytes.hex()[:text_length * 2]
    
    @staticmethod
    def __text_right_append(text, mode):
        segment_byte_size = 16 if mode == 'utf8' else 32

        if len(text) % segment_byte_size == 0:
            return text

        append_length = segment_byte_size - len(text) % segment_byte_size
        text += '0' * append_length
        return text