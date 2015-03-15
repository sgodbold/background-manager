import os
import subprocess
import random
from collections import deque
import sys
import select
import time

WALLPAPER_DIR = "/home/raelon/.wallpaper/"
TIMEOUT = 15
history = deque([], maxlen=5)
current_pic = None


def main():
    options = {
        'help': print_menu,
        'next': next_image,
        'previous': prev_image,
        'delete': delete_image,
        'history': print_history,
        'current': print_current
    }

    while(True):
        command = rotate_n_wait()
        if command:
            if any(command in l for l in list(options.keys())):
                options[command]()
            else:
                print("ERROR: Command '" + command + "' not found")
                print("type 'help' for a list of commands")

def rotate_n_wait():
    last_time = time.time()

    print("bg$ ", end="", flush=True)

    while(True):
        # Waits for input. Returns a string if the input wasn't empty.
        ready, _, _ = select.select([sys.stdin], [], [], TIMEOUT)
        if ready:
            text = sys.stdin.readline().rstrip('\n')
            if text:
                return text

        # Prevent rotating images by typing commands.
        if (time.time() - last_time) > TIMEOUT:
            # BUG: prints a new line every wallpaper switch
            print("")
            next_image()
            last_time = time.time()

        print("bg$ ", end="", flush=True)

# Insecurely allows for a bash command to be executed because I'm lazy.
# Returns the bash commands output.
def bash(command):
    """ Insecurely allows for a bash command to be executed because I'm lazy.
    Returns the bash commands output. """

    output = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE).communicate()[0]
    return output

def print_menu():
    """ Prints a menu of commands """
    print("help\t\t|\tprints this menu")
    print("next\t\t|\tskip to the next wallpaper")
    print("previous\t|\tgo back to the last wallpaper")
    print("delete\t\t|\tdelete the current wallpaper and skip to the next one")
    print("history\t\t|\tprint a list of previously viewed images.")
    print("current\t\t|\tprint the filename of the current image.")

def next_image():
    """ Skips to the next image, and updates history """
    global history
    global current_pic

    if(current_pic):
        history.append(current_pic)
    current_pic = random.choice(os.listdir(WALLPAPER_DIR))
    bash("feh --bg-max " + WALLPAPER_DIR + current_pic)

def prev_image():
    """ Moves back to the last image, and updates history """ 
    global history
    global current_pic

    if len(history) > 0:
        current_pic = history.pop()
        bash("feh --bg-max " + WALLPAPER_DIR + current_pic)
    else:
        print("No history!")

def delete_image():
    """ Removes the current wallpaper and skips to the next one """
    global history
    global current_pic

    confirm = input("delete image '" + current_pic + "' ?[y/n]")
    if confirm == "y":
        name = current_pic
        current_pic = None #prevent removed file being added to history
        next_image()

        os.remove(WALLPAPER_DIR + name)
        print("deleted '" + name + "'")
    else:
        print("no pictures deleted")

def print_history():
    global history

    print(history)

def print_current():
    global current_pic
    print(current_pic)

if __name__ == "__main__":
    main()
