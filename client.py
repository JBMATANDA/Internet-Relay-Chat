import socket
import threading


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = '10.10.20.116'
PORT = 12344

s.connect((HOST, PORT))

def get_input():
    while True:
        tmp = input()
        if tmp == "":  # Enter will be sent as NOOP
            tmp = "NOOP :NOOP"
        s.send(tmp.encode())
        # Stop thread if a QUIT command was successfully sent
        if tmp.split(' :')[0] == "QUIT":
            break


t = threading.Thread(
   target=get_input)
t.start()

while True:
    data = s.recv(1024).decode("utf-8")
    if data == "TERMINATE_CONNECTION":
        print("Connection was successfully terminated.")
        break
    print(data)

s.close()
