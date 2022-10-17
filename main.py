from re import I
from time import sleep
from datetime import datetime

from json import dump

from random import choice

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys



ARRS_URL = "https://arrs.host"   

INPUT_XPATH = '//input[@id="cmd_input"]'
TERMINAL_XPATH = '//*[@id="content"]'

WARDEN_USER = "warden"
WARDEN_PASSWORD = "O5SXIMZRO5QXIZLS"
DECRYPT_STRING = "decrypt /home/warden/private/d900a70d64.inf"
# start is used to start the maze loop, not a real output
EXPECTED_OUT = {"start", "true", "false", "you died", "blocked 30s", "teleported"}
move_strings = ["up", "right", "down", "left"]

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


def calc_available_moves(x,y):
    # up, right, down, left
    return [(x, y+1), (x+1, y), (x, y-1), (x-1, y)]

def get_preferred_move(x, y, opens, walls, blocks):

    move_strings = ["up", "right", "down", "left"]

    available_moves = calc_available_moves(x, y)
    preferred_moves = []

    # check for non-visited nodes first
    for i, move in enumerate(available_moves):
        if move not in opens and move not in walls and move not in blocks:
            preferred_moves.append(move_strings[i]) 
        
    if preferred_moves:
        return choice(preferred_moves)

    # if there are no non-visited nodes, start backtracking
    for i, move in enumerate(available_moves):
        if move not in walls:
            preferred_moves.append(move_strings[i])

    return choice(preferred_moves)

def maze_run():

    move_coords = {
        "up": (0, 1),
        "right": (1, 0), 
        "down": (0, -1),
        "left": (-1, 0)
        }

    history = []

    opens = set()
    opens.add((0,0))

    walls = set()
    blocks = set()
    kills = set()
    teleports = set()

    unexpected = False
    teleported = False
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
            # get a bigger response from the terminal since a key or link might be multiple lines
            large_response = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, TERMINAL_XPATH))).text.split('\n')[-20:]
            unexpected = large_response
            running = False

        elif response == "true":
            history.append(previous_move)
            x += move_coords[previous_move][0]
            y += move_coords[previous_move][1]
            opens.add((x,y))

            next_move = get_preferred_move(x, y, opens, walls, blocks)
            response = move(next_move)
            previous_move = next_move

        elif response == "false":
            wall_x = x + move_coords[previous_move][0]
            wall_y = y + move_coords[previous_move][1]
            walls.add((wall_x, wall_y))

            next_move = next_move = get_preferred_move(x, y, opens, walls, blocks)
            response = move(next_move)
            previous_move = next_move

        elif response == "blocked 30s":
            print(f"Waiting at square ({x}, {y})")
            sleep(31)
            
            x += move_coords[previous_move][0]
            y += move_coords[previous_move][1]
            blocks.add((x, y))

            next_move = get_preferred_move(x, y, opens, walls, blocks)
            response = move(next_move)
            previous_move = next_move

        elif response == "you died":
            x += move_coords[previous_move][0]
            y += move_coords[previous_move][1]
            print(f"Dead after {len(history)} nodes")
            print('=' * 15)
            running = False
        
        elif response == "teleported":
            teleported = True
            x += move_coords[previous_move][0]
            y += move_coords[previous_move][1]
            teleports.add((x,y))

            running = False

        elif response == "start":
            next_move = choice(move_strings)
            response = move(next_move)
            previous_move = next_move

    if unexpected:
        result_prefix = "Unexpected"
    elif teleported:
        result_prefix = "Teleported"
    else:
        result_prefix = "Died"

    with open(result_prefix + '_MazeRun' + datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p") + '.txt', 'w') as f:
        f.write(f"{result_prefix} at ({x}, {y}): {response}\n")
    
        f.write(f"Result: {result_prefix}\n")

        if unexpected:
            f.write(f"Last 20 lines before unexpected response:\n")
            dump(large_response, f, indent=2)
            f.write("\n\n")

        f.write("Move history:\n")
        dump(history, f)
        f.write("\n\n")

        f.write("Walls: \n")
        dump(list(walls), f)
        f.write("\n\n")

        f.write("Open Squares: \n")
        dump(list(opens), f)
        f.write("\n\n") 

        f.write("Block (Delay) Squares: \n")
        dump(list(opens), f)
        f.write("\n\n")

        f.write("Kill Squares (if applicable): \n")
        dump(list(kills), f)
        f.write("\n\n") 

        f.write("Teleport Squares (if applicable): \n")
        dump(list(teleports), f)


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

searching = True
while searching:
    maze_run()
