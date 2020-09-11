from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time, random

class TemplateBot(object):
    def __init__(self, show = False, debug = False) -> None:
        options = Options()
        if not show: options.add_argument("--headless")
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-logging') 
        self.driver = webdriver.Chrome(options = options)
        self.debug = debug

    def protected_sleep(self, time_to_sleep = None) -> None:
        if not time_to_sleep:
            list_of_seconds = [x / 10 for x in range(1,11)]
            time.sleep(random.choice(list_of_seconds))
        else:
            time.sleep(time_to_sleep)
    
    def login(self, username: str, password: str):
        self.username = username
        self.password = password

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.close()

    def __str__(self):
        return f'{self.driver.title}\n{self.driver.current_url}'
    
    def close(self):
        self.driver.close()
