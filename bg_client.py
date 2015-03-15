from multiprocessing.connection import Client

address = ('localhost', 60000)
with Client(address, authkey=b'LcomEnEPOe') as conn:
    conn.send('ping')
    conn.send('close')
    conn.close()
