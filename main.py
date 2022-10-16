from multiprocessing.connection import wait
from xml.dom.minidom import Attr
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from time import sleep

ARRS_URL = "https://arrs.host"   

INPUT_XPATH = '//*[@id="cmd_input"]'
TERMINAL_XPATH = '//*[@id="content"]'

WARDEN_USER = "warden"
WARDEN_PASSWORD = "O5SXIMZRO5QXIZLS"
DECRYPT_STRING = "decrypt /home/warden/private/d900a70d64.inf"
# start is used to start the maze loop, not a real output
EXPECTED_OUT = {"start", "true", "false", "you died", "blocked 30s"}

# Open the ARRS website
driver = webdriver.Chrome()
driver.get(ARRS_URL)

def wait_until_available(xpath, timeout=15):
    try:
        field = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        return field
    except:
        print(f"Element at {xpath} not available after {timeout} seconds")


# Directions, 1-4 counter clockwise, starting with 1 UP
# i.e. 1 = up, 2 = right, 3 = down, 4 = left

def move(move_id):
    if move_id not in range(0,4):
        raise AttributeError(f"Invalid move id: {move_id}")

    move_text = ["up", "right", "down", "left"]

    input_field = wait_until_available(INPUT_XPATH)
    input_field.send_keys(move_text[move_id])
    input_field.send_keys(Keys.RETURN)

    sleep(5)
    response = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, TERMINAL_XPATH)))
    print('=' * 15)
    print(response.text)
    print('=' * 15)
    print(response.text.split('\n')[-1])

def maze_run():
    history = []
    previous = "start"
    previous_move = 1
    running = True
    while running:
        if previous not in EXPECTED_OUT:
            print(f"UNEXPECTED OUTPUT FOUND: {previous}")
            print(f"History: \n{history}")
            print('=' * 15)
            running = False
        if previous == "you died":
            print(f"Dead after {len(history)} nodes")
            print('=' * 15)
            Running = False
        if previous == "true":
            move(previous_move)
        if previous == "false":
            pass


# Login w/ username
input_field = wait_until_available(INPUT_XPATH)
input_field.send_keys(f"login {WARDEN_USER}")
input_field.send_keys(Keys.RETURN)

# Input warden password
input_field = wait_until_available(INPUT_XPATH)
input_field.send_keys(WARDEN_PASSWORD)
input_field.send_keys(Keys.RETURN)

# Open the maze
input_field = wait_until_available(INPUT_XPATH)
input_field.send_keys(DECRYPT_STRING)
input_field.send_keys(Keys.RETURN)

move(1)