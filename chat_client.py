import socket
import select
import msvcrt
import keyboard

client_socket=socket.socket()
client_socket.connect(('127.0.0.1',23))
collected=''
while True:

    (to_read, to_write, exceptional) = select.select([client_socket], [client_socket], [])
    if to_read:
        data_read = to_read[0].recv(1024)
        # technically sys.stdout could also block (e.g. being piped or simply in a slow terminal) but for the sake of simplicity, don't bother ourselves.
        if data_read:
            if(data_read=='quit'):
                break
            elif(data_read=='NL'):
                print
            else:
                print data_read
    if to_write:
        while(keyboard.is_pressed('enter') is False):
            if(msvcrt.kbhit()):
                collected += msvcrt.getche()
        client_socket.send(collected)
        collected = ''

client_socket.close()
