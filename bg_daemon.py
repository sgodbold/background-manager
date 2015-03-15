from multiprocessing.connection import Listener
from multiprocessing import Process, Queue
from collections import deque
import configparser
import subprocess
import random
import select
import time
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

    with Listener(address, authkey=_authkey) as listener:
        with listener.accept() as conn:
            msg = conn.recv()
            q.put(msg)
            return

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

    while True:
        msg = rotate_n_wait()
        print("got message: " + msg)

    return 0

def next_img():
    """ Continues to the next image. """
    global _wallpaper_path
    global _images

    img = random.choice(os.listdir(_wallpaper_path))
    _images.appendleft(img)
    bash("feh --bg-max " + _wallpaper_path + img)

    return

def rotate_n_wait():
    """ Rotates wallpaper until a command from the client is recieved.
        Returns the string sent from the client. """
    global _wallpaper_path
    global _prev_rotate
    global _timeout

    result = None
    queue = Queue()
    p = Process(target=client_conn, args=(queue,))

    p.start()
    while not result:
        try:
            if time.time() - _prev_rotate > _timeout:
                next_img()
                print("Changing wallpaper")
                _prev_rotate = time.time()
            result = queue.get(True, _timeout)
        except:
            print("next")
    p.join()

    return result

if __name__ == "__main__":
    main()
