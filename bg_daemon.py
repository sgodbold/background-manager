from multiprocessing.connection import Listener
from multiprocessing import Process, Queue
from collections import deque
import configparser
import subprocess
import random
import select
import time
import sys
import os

# Global settings
_config_path = '/home/raelon/.config/bg/settings.conf'
_wallpaper_path = None
_history_size = None
_authkey = None
_timeout = None
_port = None

# Global values
_prev_rotate = 0
_images = None # index 0 is current img

def bash(command):
    """ Insecurely allows for a bash command to be executed because I'm lazy.
        Returns stdout from the command. """

    return subprocess.Popen([command], shell=True, stdout=subprocess.PIPE)\
            .communicate()[0]

def client_conn(q):
    """ Listens for commands sent from the client. """
    global _authkey
    global _port

    address = ('localhost', _port)

    while(True):
        with Listener(address, authkey=_authkey) as listener:
            try:
                with listener.accept() as conn:
                    while(True):
                        msg = conn.recv()
                        q.put(msg)
            # Catch errors when connection is unexectedly closed
            except Exception as e:
                print("Caught exception at listener")

def load_config():
    global _wallpaper_path
    global _config_path
    global _history_size
    global _authkey
    global _timeout
    global _images
    global _port

    config = configparser.ConfigParser()
    config.read(_config_path)

    _authkey = config['daemon']['authkey'].encode('utf-8')
    _history_size = int(config['daemon']['history_size'])
    _wallpaper_path = config['daemon']['wallpaper_path']
    _timeout = int(config['daemon']['timeout'])
    _port = int(config['daemon']['port'])

    # Initialize deque
    _images = deque([], maxlen=_history_size)

    return

def main():
    load_config()

    queue = Queue()
    p = Process(target=client_conn, args=(queue,))


    try:
        p.start()
        while True:
            msg = rotate_n_wait(queue)
            print("got message: " + msg)
    except Exception as e:
        p.join()
        print("Caught exception at main")

    return 0

def next_img():
    """ Continues to the next image. """
    global _wallpaper_path
    global _images

    img = random.choice(os.listdir(_wallpaper_path))
    _images.appendleft(img)
    bash("feh --bg-max " + _wallpaper_path + img)

    return

def rotate_n_wait(queue):
    """ Rotates wallpaper until a command from the client is recieved.
        Returns the string sent from the client. """
    global _wallpaper_path
    global _prev_rotate
    global _timeout

    result = None

    while not result:
        try:
            if time.time() - _prev_rotate > _timeout:
                next_img()
                print("Changing wallpaper")
                _prev_rotate = time.time()
            result = queue.get(True, _timeout)
        except KeyboardInterrupt as e: # Catch Ctrl-c and properly stop code
            print("Caught exception in rotate_n_wait")
            return e
        except: # Catch empty result error
            print("next")

    return result

if __name__ == "__main__":
    main()
