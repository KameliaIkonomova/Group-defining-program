import socket, threading, datetime, argparse                                      
from time import sleep

#initialise the starter function for modularity, allows for two inputs the host ip and the port
def starter(host, port):
    #defined global variables to be used through out the program
    global hoster
    global poster
    global server

    #converted the two inputs into the correct value types
    hoster = str(host)
    poster = int(port)

    #socket initialization
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #binding host and port to socket
    server.bind((hoster, poster))
    #starts the server and listens to client connections
    server.listen()
    #calls the recieve function
    receive()

#defined global lists to help maintain the groups and members in the server
clients = []
nicknames = []
coordinator = []
addresses = []
groupnick = []
groupcoordinators = []

#created a function for the server to keep track of the time at which messsages are sent out and logged through the server
def gettime():
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

#created another modular function to record the messages sent through the server, stores in a new text file stored on the pc
def chatlogger(message):
    f = open('chatlog.txt','a')
    f.write(str('{} \n'.format(message)))

#broadcast function declared, takes in the message as an argument and then processes it, sending to all the required members 
def broadcast(message):
    #decodes the user's message using ascii and splits the group number 
    messi = message.decode('ascii')
    sorter = messi
    sorte = sorter.split("|")
    #stores group number as a local variable to help broadcast to the appropriate groups
    grouper = sorte[0]
    #try code to handle any irregular messages broadcasted through the server
    try:
        messier = sorte[1]
    except:
        pass
    #sleeps initated to allow the threading to catch up with the commands
    sleep(0.05)
    #for every client inside the clients list, it iterates and sends the message one by one
    for client in clients:
        index = clients.index(client)
        #compares the group number in the broadcasted message with the groupnick list, if theyre equal then they are in the same group
        if grouper == groupnick[index][0]:
            client.send('({}) {}'.format(gettime(), messier).encode('ascii'))
    try:
        #logs the messages sent through the server by parcing through the chatlogger function
        chatlogger('({})group {}: {}'.format(gettime(),grouper, messier))
    except:
        pass

#created a function to help handle all the messages sent to the server from each client 
def handle(client):                                         
    while True:
        try:
            #recieving valid messages from the client 
            message = client.recv(1024)
            broadcast(message)
        except:
            #if a client abruptly disconnects from the server this code is started, to remove the client from every list
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            addresses.remove(addresses[index])

            #code initialized to remove and replace the group coordinator in case the user is the group coordinator for the specific group
            for sublist in groupnick:
                if sublist[1] == nickname:
                    serve = sublist[0]
                    #broadcasts that the user left in the appropriate group
                    broadcast('{}|{} left!'.format(sublist[0], nickname).encode('ascii'))
                    groupnick.remove(sublist)
                    #iterates through the list of groupcoordinators to check if the user is a group coordinator
                    for sublist in groupcoordinators:
                        #if the username is found then the name is removed and the next user in the specific group list is promoted automatically to group coordinator 
                        if sublist[1] == nickname:
                            win = sublist
                            groupcoordinators.remove(sublist)
                            for sublist in groupnick:
                                if sublist[0] == serve:
                                    #if the change happens then the message is broadcasted to inform all members who left and who is the new coordinator
                                    chatlogger('({}) {} is the new coordinator for group {}'.format(gettime(), sublist[1], sublist[0]))
                                    sleep(0.05)
                                    broadcast('{}|{} is the new coordinator for group {}'.format(sublist[0], sublist[1], sublist[0]).encode('ascii'))
                                    groupcoordinators.append(sublist)
                                    break
                                else:
                                    #if there are no more group members the server logs this
                                    chatlogger('({}) group {} is empty'.format(gettime(), serve))

            #initiates the code if the user who disconencted is the main coordinator for the server and group 1    
            if nickname in coordinator:
                #if there are more than one members connected to the server then the next member in the list is promoted and the old one is removed
                if len(nicknames) >= 2:
                    coordinator.remove(nickname)
                    coordinator.append(nicknames[1])
                    broadcast('1|{} is the new main coordinator'.format(coordinator[0]).encode('ascii'))
                else:
                    #otherwise the server logs that the server is empty
                    coordinator.remove(nickname)
                    chatlogger('({}) the server is empty.'.format(gettime()))

            #removes the nickname from the server list
            nicknames.remove(nickname)
            break



#accepting multiple clients
def receive():
    #constantly looping whilst the server is on
    while True:
        # stores the client variable and stores the client's address in a new local varialbe
        client, address = server.accept()
        #stores the address in a list of addresses
        addresses.append(str(address))

        #sends the welcoming message to the client to initiate the server connection
        client.send('NICKNAME'.encode('ascii'))
        #stores the response sent from the client
        sorter = client.recv(1024).decode('ascii')
        #splits the client's message to extract the group number and username
        sorte = sorter.split("|")
        nickname = sorte[1]
        serve = sorte[0]

        #stores the new username and the specified group number in the list "groupnick" which is used to broadcast messages to the group members
        sleep(0.05)
        test = [serve,nickname]
        groupnick.append(test)

        #checks if the username is already in use, if it is then the message is sent to the client informing so
        if nickname in nicknames:
            client.send('TAKEN'.encode('ascii'))
            client.close()
            pass
        else:
            
            #checks if there are any group members in the group chosen by the user
            if not any(serve in sublist for sublist in groupcoordinators):
                #if the user is the first, then the user is the group coordinator and this is logged in the server logs
                groupcoordinators.append(test)
                chatlogger('({}) {}{} is the coordinator for group {}'.format(gettime(), nickname, address, serve))

            #checks if there is a main coordinator in the server
            if not coordinator:
                #if there is not then the user becomes the main coordinator
                coordinator.append(nickname)
                chatlogger('({}) {} is the main coordinator'.format(gettime(), coordinator[0]))

            #stores the user's nickname and client information to send future messages to
            nicknames.append(nickname)
            clients.append(client)

            #broadcasts that the user joined, with his ip and port to any active group members
            broadcast("{}|{}{} joined group {}!".format(serve, nickname, address, serve).encode('ascii'))
            
            #tells the relevent server information to the client 
            client.send('Connected to server! \n'.encode('ascii'))
            client.send('{} is the main coordinator \n'.format(coordinator[0]).encode('ascii'))           
            sleep(0.05) #initiates sleep to allow threading to catch up with the messages and stop overwriting messages
            client.send('current members (first member in any group is the group admin)'.encode('ascii'))
            sleep(0.05)
            client.send('--------------- '.encode('ascii'))
            sleep(0.05)

            #opens a new or current text file to read from and send to the client, all current clients, their groups, their ips and ports
            f = open('chatmembers.txt','a')
            for x in range(len(nicknames)):
                sleep(0.05)
                client.send('{} (group {}) {}'.format(nicknames[x],groupnick[x][0], addresses[x]).encode('ascii'))
                print('')
            sleep(0.05)

            #stores the new member inside a log of connected group members, with the group number, their ip and port
            f.write('{} {} \n'.format(nickname, address))
            f.close()
            sleep(0.05)
            client.send('--------------- \n'.encode('ascii'))

            #calls the threading variable to allow for multiple messages
            thread = threading.Thread(target=handle, args=(client,))
            #more sleep arguements to allow threads to catch up
            sleep(0.1)
            thread.start()
            sleep(0.1)

#starts the server by calling the "starter" function
starter('127.0.0.1', 7976)
