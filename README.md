# Tarkov ARG Maze Solver

## Description
This script uses Selenium to search the Escape From Tarkov arrs.host ARG maze in an attempt to find any hints or encryption keys.
The script will create .txt files that contain the outcome of each run, as well as a list of open squares and walls that can be used to make a visual map of the maze.
Each maze run will have the following results:
- Died
- Teleported
- Found unexpected response

In each case, a .txt file is created with the the result of the run. Any encryption keys or solutions to the maze will fall under the unexpected response category, and the txt file will look like `Unexpected_MazeRun[timestamp].txt`
After each run, a new one will start until the script is stopped (`CRTL + C`) or errors out for some reason

## Getting Started
### Installing

- Install [Python](https://www.python.org/downloads/)
- [Clone this repo](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)
- In the cloned directory, [create a virtual env](https://docs.python.org/3/library/venv.html). In short, run `python -m venv /path/to/new/virtual/environment`
- Run `pip install -r requirements.txt`
- [Download a chromedriver](https://chromedriver.chromium.org/downloads) based on your version of Chrome (Go to chrome://version/ to find your major version, i.e. 106)
- Move the chromedriver to the same directory as main.py file
- Activate the venv, using `path\to\venv\Scripts\Activate.ps1` on Windows or `source path\to\venv\Scripts\activate` on MacOS or Linux

### Executing program

- `python main.py`

The script will generate txt files that contain the result of each maze run and a coordinate map of open squares and walls.
The script will terminate if the the maze dies. It also terminates after being teleported since the coordinate map will not be correct after a teleport.

## Help

ButterflyEnthusiast#8276 on Discord

## Authors

ButterflyEnthusiast

## Acknowledgments

Thanks to the NoiceGuy SoS for help and suggestions
