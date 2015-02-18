import os
import subprocess
import time
import random
from collections import deque
from threading import Timer
import sys
import select

WALLPAPER_DIR = "/home/raelon/.wallpaper/"
TIMEOUT = 15
#history = deque('end').maxlen(5)
history = deque(['1'], maxlen=5)
current_pic = None

def main():
    options = {
        'next': 'next_image',
        'previous': 'prev_image',
        'history': 'print_history'
    }

    while(True):
        command = rotate_and_wait()
        print("command = " + command)

def rotate_and_wait():
    while(True):
        next_image()
        print("bg$ ", end="", flush=True)
        ready, _, _ = select.select([sys.stdin], [], [], TIMEOUT)
        if ready:
            return sys.stdin.readline().rstrip('\n')

# Insecurely allows for a bash command to be executed because I'm lazy.
# Returns the bash commands output.
def bash(command):
    """ Insecurely allows for a bash command to be executed because I'm laze.
    Returns the bash commands output. """

    output = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE).communicate()[0]
    return output

def print_menu():
    """ Prints a menu of commands """
    print("next\t|\tskip to the next wallpaper")
    print("previous\t|\tgo back to the last wallpaper")
    print("delete\t|\tdelete the current wallpaper and skip to the next one")

def next_image():
    global history
    global current_pic

    history.append(current_pic)
    current_pic = random.choice(os.listdir(WALLPAPER_DIR))
    bash("feh --bg-max " + WALLPAPER_DIR + current_pic)

def prev_image():
    global history

    current_pic =history.pop()
    bash("feh --bg-max " + WALLPAPER_DIR + current_pic)

def print_history():
    global history

    print(history)

if __name__ == "__main__":
    main()
