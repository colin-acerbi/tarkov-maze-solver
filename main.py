import datetime
import json
from multiprocessing.connection import wait
from xml.dom.minidom import Attr
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from time import sleep
from random import choice

ARRS_URL = "https://arrs.host"   

INPUT_XPATH = '//input[@id="cmd_input"]'
TERMINAL_XPATH = '//*[@id="content"]'

WARDEN_USER = "warden"
WARDEN_PASSWORD = "O5SXIMZRO5QXIZLS"
DECRYPT_STRING = "decrypt /home/warden/private/d900a70d64.inf"
# start is used to start the maze loop, not a real output
EXPECTED_OUT = {"start", "true", "false", "you died", "blocked 30s"}

move_opposites = {
        "up": "down",
        "left": "right",
        "right": "left",
        "down": "up"
        }
move_strings = move_opposites.keys()

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

def move(move_text):
    if move_text not in move_strings:
        raise AttributeError(f"Invalid move: {move_text}")

    input_field = wait_until_available(INPUT_XPATH)
    input_field.send_keys(move_text)
    input_field.send_keys(Keys.RETURN)

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, INPUT_XPATH))).click()
    response = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, TERMINAL_XPATH))).text.split('\n')[-1]
    print(response)
    return response

def maze_run():

    move_coords = {
        "up": (0, 1),
        "right": (1, 0), 
        "down": (0, -1),
        "left": (-1, 0)
        }

    history = []
    opens = set()
    walls = set()
    unexpected = "Nothing unexpected"

    response = "start"
    # previous move is the text of the move, i.e "left"
    previous_move = "up"
    x, y = 0, 0

    running = True
    while running:
        print(f"(x, y): ({x}, {y}), response: {response}, previous_move: {previous_move}")
        if response not in EXPECTED_OUT:
            print(f"UNEXPECTED OUTPUT FOUND at ({x}, {y}): {response}")
            print(f"History: \n{history}")
            print('=' * 15)
            unexpected = response 
            running = False

        elif response == "true":
            history.append(previous_move)
            x += move_coords[previous_move][0]
            y += move_coords[previous_move][1]
            opens.add((x,y))
            # move anywhere that is not the previous move (i.e. don't backtrack)
            next_move = choice([m for m in move_strings if m not in move_opposites[previous_move]])
            response = move(next_move)
            previous_move = next_move

        elif response == "false":
            wall_x = x + move_coords[previous_move][0]
            wall_y = y + move_coords[previous_move][1]
            walls.add((wall_x, wall_y))

            # move anywhere that is not the move that just failed (i.e. don't move into a known wall)
            next_move = choice([m for m in move_strings if m not in previous_move])
            response = move(next_move)
            previous_move = next_move

        elif response == "blocked 30s":
            print(f"Waiting at f({x}, {y})")
            sleep(31)
            # move anywhere that is not the previous move (i.e. don't backtrack)
            next_move = choice([m for m in move_strings if m not in move_opposites[previous_move]])
            response = move(next_move)
            previous_move = next_move

        elif response == "you died":
            print(f"Dead after {len(history)} nodes")
            print('=' * 15)
            running = False
    
        elif response == "start":
            response = move(choice([m for m in move_strings]))

        

    
    with open('MazeRun' + datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p") + '.txt', 'w') as f:
        if unexpected != "Nothing unexpected":
            f.write(f"UNEXPECTED OUTPUT FOUND at ({x}, {y}): {response}")

        f.write(f"Result: {response}")

        f.write("Move history:\n")
        json.dump(history, f)

        f.write("Walls: \n")
        json.dump(list(walls), f)

        f.write("Open Squares: \n")
        json.dump(list(opens), f)


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

maze_run()