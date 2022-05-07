from socket import *
from time import sleep
HOST = "10.16.127.6" #local host
PORT = 8080 #open port 7000 for connection
s = socket(AF_INET, SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1) #how many connections can it receive at one time
conn, addr = s.accept() #accept the connection
print("Connected by: " , addr) #print the address of the person connected
while True:
    try:
        data = conn.recv(1024) #how many bytes of data will the server receive
        test_string = repr(data)
        print("Received: ", test_string[7:])
        sleep(3)
    except KeyboardInterrupt:
        conn.close()
        print("Connection with " , addr, " is now over.")

    #misc leftovers from example    
    #reply = raw_input("Reply: ") #server's reply to the client
    #conn.sendall(reply)