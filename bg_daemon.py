from multiprocessing.connection import Listener
from multiprocessing import Process, Queue
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
_freeze = False
_images = [] # index 0 is current img

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
                        # message from client
                        msg = conn.recv()
                        q.put(msg)
                        # confirmation from daemon
                        confirm = q.get(msg)
                        conn.send(confirm)
            # Catch errors when connection is unexectedly closed
            except Exception as e:
                print("Caught exception at listener")

def delete_img():
    return False

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

    return

def main():
    load_config()

    queue = Queue()
    p = Process(target=client_conn, args=(queue,))

    options = {
        'next': next_img,
        'previous': prev_img,
        'toggle_freeze': set_freeze,
        'set_image': set_img,
        'set_timeout': set_timeout,
        'delete': delete_img
    }

    try:
        p.start()
        while True:
            msg = rotate_n_wait(queue)
            msg = msg.split(' ', maxsplit=1)
            try:
                if len(msg) == 1:
                    confirm = options[msg[0]]()
                else:
                    confirm = options[msg[0]](msg[1])
                queue.put(confirm)
            except:
                print("Unknown command: " + msg)
                queue.put(False)
    except Exception as e:
        # Safely terminate side process
        p.join()

    return 0

def next_img():
    """ Continues to the next image. """
    global _wallpaper_path
    global _history_size
    global _prev_rotate
    global _images

    print("next img")

    # Grab next image
    img = random.choice(os.listdir(_wallpaper_path))
    _images.insert(0, img)
    bash("feh --bg-max " + _wallpaper_path + img)

    # Trim images list
    if len(_images) > _history_size:
        _images.pop(_history_size)

    # reset timer
    _prev_rotate = time.time()


    return True

def prev_img():
    """ Goes to previous image. """
    global _wallpaper_path
    global _prev_rotate
    global _images

    print("prev img")

    try:
        # Grab previous image
        _images.pop(0)
        bash("feh --bg-max " + _wallpaper_path + _images[0])

        # reset timer
        _prev_rotate = time.time()

        return True
    except:
        print("No previous images")
        return False

def set_freeze():
    global _freeze
    _freeze = not _freeze

    return True

def set_img():
    return False

def set_timeout(time):
    global _timeout
    _timeout = int(time)
    print("Set timeout to %d" % int(time))

    return True

def rotate_n_wait(queue):
    """ Rotates wallpaper until a command from the client is recieved.
        Returns the string sent from the client. """
    global _wallpaper_path
    global _prev_rotate
    global _timeout
    global _freeze

    result = None

    while not result:
        try:
            if _freeze == False and time.time() - _prev_rotate > _timeout:
                next_img()
                _prev_rotate = time.time()
            result = queue.get(True, _timeout)
        except KeyboardInterrupt as e: # Catch Ctrl-c and properly stop code
            return e
        except: # Catch empty result error
            pass

    return result

if __name__ == "__main__":
    main()
