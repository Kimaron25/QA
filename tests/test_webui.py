"""Selenium-тесты Web UI OpenBMC (ЛР4)."""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

BASE_URL = "https://localhost:2443"
USERNAME = "root"
PASSWORD = "0penBmc"


def test_webui_login():
    """Тест: успешная авторизация в Web UI."""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--headless=new')
    chrome_options.binary_location = "/usr/bin/google-chrome"

    service = Service(executable_path='/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(f"{BASE_URL}/#/login")
    time.sleep(2)
    driver.find_element(By.ID, "username").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//*[@data-test-id='login-button-submit']").click()
    time.sleep(4)
    assert "/#/login" not in driver.current_url
    print(f"\n[ТЕСТ WebUI] Вход выполнен, URL: {driver.current_url}")
    driver.quit()
