from multiprocessing.connection import Client
import configparser

# Global settings
_config_path = '/home/raelon/.config/bg/settings.conf'
_authkey = None
_port = None

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

    options = {
        'help': print_menu,
    }

    load_config()

    address = ('localhost', _port)
    with Client(address, authkey=_authkey) as conn:
        print_menu()
        while True:
            msg = input('bg$ ')
            if msg:
                conn.send(msg)

    return 0

def print_menu():
    print("{0:10} | {1:10}".format('help', 'prints this menu'))
    print("{0:10} | {1:10}".format('help', 'prints this menu'))
    print("{0:10} | {1:10}".format('help', 'prints this menu'))
    print("{0:10} | {1:10}".format('help', 'prints this menu'))
    print("{0:10} | {1:10}".format('help', 'prints this menu'))
    return

if __name__ == "__main__":
    main()
