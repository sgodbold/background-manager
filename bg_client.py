from multiprocessing.connection import Client
import configparser
import sys

# Global settings
_config_path = '/home/raelon/.config/bg/settings.conf'
_authkey = None
_port = None
_conn = None

def exit(msg=''):
    """ Closes connection with daemon and exits program. """
    global _conn

    _conn.close()
    sys.exit()

def load_config():
    global _authkey
    global _port

    config = configparser.ConfigParser()
    config.read(_config_path)

    _authkey = config['daemon']['authkey'].encode('utf-8')
    _port = int(config['daemon']['port'])

    return

def main():
    global _authkey
    global _port
    global _conn

    load_config()

    options = {
        'help': print_menu,
        'next': send,
        'previous': send,
        'toggle_freeze': send,
        'set_image': send,
        'set_timeout': send,
        'delete': send,
        'exit': exit
    }

    address = ('localhost', _port)
    with Client(address, authkey=_authkey) as _conn:
        print_menu('')
        while True:
            msg = input('bg$ ')
            if msg:
                try:
                    options[msg.split(' ')[0]](msg)
                except Exception:
                    print("ERROR: Unknown command " + msg)

    return 0

def print_menu(msg=''):
    print("help".ljust(30) + "|\t\t" + "Prints this menu")
    print("next".ljust(30) + "|\t\t" + "Skips to the next image")
    print("previous".ljust(30) + "|\t\t" + "Goes back to previous image")
    print("toggle_freeze".ljust(30) + "|\t\t" + "Turns image rotation on / off")
    print("set_image [/path/to/image]".ljust(30) + "|\t\t" + "Set a specific image")
    print("set_timeout [seconds]".ljust(30) + "|\t\t" + "Sets the rotation timeout to [seconds]")
    print("delete".ljust(30) + "|\t\t" + "Deletes current image. Requires rotation to be frozen")
    print("exit".ljust(30))
    return

def send(msg):
    """ Sends a command and waits for a confirmation. """
    global _conn

    _conn.send(msg)
    confirm = _conn.recv()

    if confirm:
        print("Command completed")
    else:
        print("Error from daemon!")

    return

if __name__ == "__main__":
    main()
