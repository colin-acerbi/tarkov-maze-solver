from multiprocessing.connection import wait
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

ARRS_URL = "https://arrs.host"   

INPUT_XPATH = '//*[@id="cmd_input"]'

WARDEN_USER = "warden"
WARDEN_PASSWORD = "O5SXIMZRO5QXIZLS"
DECRYPT_STRING = "decrypt /home/warden/private/d900a70d64.inf"

driver = webdriver.Chrome()
driver.get(ARRS_URL)

def wait_until_available(xpath, timeout=15):
    try:
        field = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        return field
    except:
        print(f"Element at {xpath} not available after {timeout} seconds")

def next_input(xpath, input, timeout=15):
    input_field = wait_until_available(INPUT_XPATH)
    input_field.send_keys(input)
    input_field.send_keys(Keys.RETURN)
    return input_field

input_field = wait_until_available(INPUT_XPATH)
input_field.send_keys(f"login {WARDEN_USER}")
input_field.send_keys(Keys.RETURN)

input_field = wait_until_available(INPUT_XPATH)
input_field.send_keys(WARDEN_PASSWORD)
input_field.send_keys(Keys.RETURN)

input_field = wait_until_available(INPUT_XPATH)
input_field.send_keys(DECRYPT_STRING)
input_field.send_keys(Keys.RETURN)






