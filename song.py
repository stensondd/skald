import socket
import sys

HOST = '127.0.0.1'
PORT = 8000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(sys.argv[1].encode("utf-8"))
    data = s.recv(1024)
    print(f"Received: {data.decode()}")



#import requests


#url = 'http://localhost:8000'
#port = 8000
#payload = {'key' : 'value'}

#response = requests.post(url, data=payload)