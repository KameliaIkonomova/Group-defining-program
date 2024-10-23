import socket, threading
from time import sleep


#initiates the client's username
nickname = input("Choose your nickname: ")


#initiates the client's group number, will not pass until a correct number is given
while True:
    try:
        group = int(input('Choose a group number (1-254): '))
        if group > 255 or group < 0:
            group = int(input('Choose a group number (1-254): '))
        else:
            break
    except:
        print('enter a number')

#socket initialization
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#connecting client to server
client.connect(('127.0.0.1', 7976))                             

#declaring a function that listens to messages sent to the client from the server
def receive():
    while True:                                                 
        try:
            #confirming there's a connection and reading the confirmation message
            message = client.recv(1024).decode('ascii')
            if message == 'NICKNAME':
                #combining the client's username and group to send to the server
                client.send('{}|{}'.format(group, nickname).encode('ascii'))                    
                verf = client.recv(1024).decode('ascii')
                #waiting for the verification message from the server, to check if the username is taken
                if verf == 'TAKEN':
                    print('nickname in use')
                    break
            else:
                #prints out any other message sent to the client from the server
                print(message)
        except:
            #incase there is an error, the user recieves a more readable error and closes connection
            print("An error occured!")
            client.close()
            break

#declaring a function that sends the user's message to the server
def write():
    while True:                                                 
        try:
            #allows the user to input a message, if the message is 'QUIT' the program shut's down
            messi = input('')
            if messi == 'QUIT':
                client.close()
                exit()
            #sends the message with the username and group number
            message = '{}|{}: {}'.format(group, nickname, messi)
            client.send(message.encode('ascii'))
        #if the user types in 'ctrl+c' at any point then the program closes.
        except EOFError:
            client.close()
            exit()

#receieve multiple messages using the threading module
receive_thread = threading.Thread(target=receive)               
receive_thread.start()
#send messages using threading to make those messages work for the other clients and the server
write_thread = threading.Thread(target=write)                    
write_thread.start()
