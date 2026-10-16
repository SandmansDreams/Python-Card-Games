import re
import time



DARK_GREY = "\033[90m"
RED = "\033[31m"
BOLD = '\033[1m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
STRIKETHROUGH = '\033[9m'
RESET = '\033[0m'

# Matches the hidden color/style codes above so they can be ignored when measuring text
ANSI_CODE = re.compile(r"\033\[[0-9;]*m")



def print_style(string, styles):
    print(f"{"".join(styles)}{string}{RESET}")
    time.sleep(0.5)

# Gets how many characters wide a string looks on screen, ignoring color codes
def visible_length(string):
    return len(ANSI_CODE.sub("", string))
