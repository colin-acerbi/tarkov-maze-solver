from time import sleep
from datetime import datetime

from json import dump

from random import choice

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException


ARRS_URL = "https://arrs.host"

INPUT_XPATH = '//input[@id="cmd_input"]'
TERMINAL_XPATH = '//*[@id="content"]'

WARDEN_USER = "warden"
WARDEN_PASSWORD = "O5SXIMZRO5QXIZLS"
DECRYPT_STRING = "decrypt /home/warden/private/d900a70d64.inf"

# start is used to start the maze loop, not a real output
EXPECTED_OUT = {
    "start",
    "true",
    "false",
    "you died",
    "blocked 30s",
    "teleported",
    "disconnected",
}

MOVE_STRINGS = ["up", "right", "down", "left"]
MOVE_COORDS = {
    "up": (0, 1),
    "right": (1, 0),
    "down": (0, -1),
    "left": (-1, 0),
}
# open the ARRS website
driver = webdriver.Chrome()
driver.get(ARRS_URL)


def wait_until_available(xpath, timeout=15) -> WebElement:
    """Waits until an element specified by an xpath is clickable and then returns that element"""
    try:
        field = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        return field
    except TimeoutException:
        print(f"Element at {xpath} not available after {timeout} seconds")


def login_flow():
    """Navigates to the maze game from the initial arrs page"""
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


class MazeRunner:
    """A class that will handle exactly one maze run. Will write the result of the maze run to a corresponding .txt file"""

    def __init__(self):

        self.move_coords = {
            "up": (0, 1),
            "right": (1, 0),
            "down": (0, -1),
            "left": (-1, 0),
        }

        self.move_count = 0

        self.opens = set()
        self.opens.add((0, 0))

        self.walls = set()
        self.blocks = set()
        self.kills = set()
        self.teleports = set()

        self.unexpected = False
        self.teleported = False
        self.response = "start"

        # previous move is the text of the move, i.e "left"
        self.previous_move = "up"
        self.x, self.y = 0, 0

        self.running = True

        print("New MazeRunner created")

    def calc_move_coords(self):
        """Returns a list of all possible next move coordinates"""
        # [up, right, down, left]
        return [
            (self.x, self.y + 1),
            (self.x + 1, self.y),
            (self.x, self.y - 1),
            (self.x - 1, self.y),
        ]

    def get_preferred_move(self) -> str:
        """Returns a move string that leads to a random adjacent non-visited, non-wall node. If there are no adjacent non-visited nodes, a move to a visited node will be returned"""
        available_moves = self.calc_move_coords()
        preferred_moves = []

        # check for non-visited nodes first
        for i, move in enumerate(available_moves):
            if (
                move not in self.opens
                and move not in self.walls
                and move not in self.blocks
            ):
                preferred_moves.append(MOVE_STRINGS[i])

        if preferred_moves:
            return choice(preferred_moves)

        # if there are no non-visited nodes, start backtracking
        for i, move in enumerate(available_moves):
            if move not in self.walls:
                preferred_moves.append(MOVE_STRINGS[i])

        return choice(preferred_moves)

    def move(self, move_text):
        """Executes a given move and updates the MazeRunner.response property"""

        if move_text not in MOVE_STRINGS:
            raise AttributeError(f"Invalid move: {move_text}")

        input_field = wait_until_available(INPUT_XPATH)
        input_field.send_keys(move_text)
        input_field.send_keys(Keys.RETURN)

        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, INPUT_XPATH))
        ).click()

        self.response = (
            WebDriverWait(driver, 20)
            .until(EC.visibility_of_element_located((By.XPATH, TERMINAL_XPATH)))
            .text.split("\n")[-1]
        )

        self.move_count += 1

    def run(self):
        while self.running:
            print(
                f"(x, y): ({self.x}, {self.y}), response: {self.response}, previous_move: {self.previous_move}"
            )

            if self.response not in EXPECTED_OUT:
                print(
                    f"UNEXPECTED OUTPUT FOUND at ({self.x}, {self.y}): {self.response}"
                )
                print("=" * 15)

                # get a bigger response from the terminal since a key or link might be multiple lines
                self.large_response = (
                    WebDriverWait(driver, 20)
                    .until(EC.visibility_of_element_located((By.XPATH, TERMINAL_XPATH)))
                    .text.split("\n")[-20:]
                )
                self.unexpected = self.large_response
                self.running = False

            elif self.response == "true":
                self.x += MOVE_COORDS[self.previous_move][0]
                self.y += MOVE_COORDS[self.previous_move][1]
                self.opens.add((self.x, self.y))

                next_move = self.get_preferred_move()
                self.move(next_move)
                self.previous_move = next_move

            elif self.response == "false":
                wall_x = self.x + MOVE_COORDS[self.previous_move][0]
                wall_y = self.y + MOVE_COORDS[self.previous_move][1]
                self.walls.add((wall_x, wall_y))

                next_move = self.get_preferred_move()
                self.move(next_move)
                self.previous_move = next_move

            elif self.response == "blocked 30s":
                print(f"Waiting at square ({self.x}, {self.y})")
                sleep(31)

                self.x += MOVE_COORDS[self.previous_move][0]
                self.y += MOVE_COORDS[self.previous_move][1]
                self.blocks.add((self.x, self.y))

                next_move = self.get_preferred_move()
                self.move(next_move)
                self.previous_move = next_move

            elif self.response == "you died":
                self.x += self.move_coords[self.previous_move][0]
                self.y += self.move_coords[self.previous_move][1]
                self.kills.add((self.x, self.y))

                print(f"Dead after {self.move_count} nodes")
                print("=" * 15)
                self.running = False

            elif self.response == "teleported":
                self.teleported = True
                self.x += MOVE_COORDS[self.previous_move][0]
                self.y += MOVE_COORDS[self.previous_move][1]
                self.teleports.add((self.x, self.y))
                print("=" * 15)
                self.running = False

            elif self.response == "start":
                next_move = choice(MOVE_STRINGS)
                self.move(next_move)
                self.previous_move = next_move

            elif self.response == "disconnected":
                self.running = False
                sleep(20)
                # need to sign back in since the disconncted response logs out
                login_flow()

        self.write_result()

    def write_result(self):
        """Writes the details of the maze run to a .txt file. Should only be used at the end of a maze run"""
        if self.unexpected:
            result_prefix = "Unexpected"
        elif self.teleported:
            result_prefix = "Teleported"
        else:
            result_prefix = "Died"

        with open(
            result_prefix
            + "_MazeRun"
            + datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
            + ".txt",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(f"{result_prefix} at ({self.x}, {self.y}): {self.response}\n")

            f.write(f"Result: {result_prefix}\n")

            if self.unexpected:
                f.write("Last 20 lines before unexpected response:\n")
                dump(self.large_response, f, indent=2)
                f.write("\n\n")

            f.write("Walls: \n")
            dump(list(self.walls), f)
            f.write("\n\n")

            f.write("Open Squares: \n")
            dump(list(self.opens), f)
            f.write("\n\n")

            f.write("Block (Delay) Squares: \n")
            dump(list(self.blocks), f)
            f.write("\n\n")

            f.write("Kill Squares (if applicable): \n")
            dump(list(self.kills), f)
            f.write("\n\n")

            f.write("Teleport Squares (if applicable): \n")
            dump(list(self.teleports), f)


login_flow()

searching = True
while searching:
    maze_run = MazeRunner()
    maze_run.run()
