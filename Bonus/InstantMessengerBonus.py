import socket
import sys

def updateUsers():
    # Updates the online users list -----
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((serverURL, serverPort))
    a = []
    listReq = [
        'GET %s HTTP/1.1' % ('/' + 'userlist.txt'),
        'Host: %s' % serverURL
    ]
    listPost = '\r\n'.join(listReq)+'\r\n\r\n'
    s.send(listPost.encode())
    listData = s.recv(2048)
    listResult = listData.decode().split("\r\n")
    if '200' in listResult[0]:
        listBody = listResult[listResult.index('')+1]
        usersSplitted = listBody.split(',')
        for user in usersSplitted:
            if user != '':
                a.append(user)
            else:
                break
            
    elif '400' in listResult[0]:
        print("There is no online users!")
    s.close()
    return a

def sendMessageP2P(userAddressPort, message, username):
    message = username + ": " + message
    sendAddressPort = userAddressPort[userAddressPort.find('@')+1:]
    sendAddress = sendAddressPort[:sendAddressPort.find(':')]
    sendPort = sendAddressPort[sendAddressPort.find(':')+1:]

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(message.encode(), (sendAddress, int(sendPort)))
    s.close()
    print("message is sent to", userAddressPort[:userAddressPort.find('@')])

username = sys.argv[1]
addrPort = sys.argv[2]
mode = sys.argv[3]

if any(char in ":@ " for char in username):
    print("Invalid username!")
    exit()

serverURL = addrPort[:addrPort.find(':')]
serverPort = int(addrPort[addrPort.find(':')+1:])


availableUsers = []

if mode == "listen": # Listen mode
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((serverURL, serverPort))
    clientIP = s.getsockname()[0]
    clientPort = s.getsockname()[1]

    # Prepares HTTP POST request
    register = 'REGISTER %s' % (username + '@' + clientIP + ':' + str(clientPort))
    lines = [
        'POST %s HTTP/1.1' % ('/' + 'userlist.txt'),
        'Host: %s' % serverURL,
        'Content-Type: %s' % 'text/*',
        'Content-Length: %s' % len(register),
        '',
        '%s' % register
    ]
    post = '\r\n'.join(lines)+'\r\n\r\n'
    s.send(post.encode()) # Sends HTTP POST
    data = s.recv(2048)
    result = data.decode().split("\r\n")

    if "200" in result[0]: # 200 OK response
        s.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((clientIP, clientPort))
        count = 0

        while True:
            if (count % 5) == 0 and count != 0:
                logOut = input("Do you want to log out?[y/n]")
                if logOut.upper() == "Y":
                    s.close()

                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((serverURL, serverPort))

                    logoutline = 'LOGOUT %s' % (username + '@' + clientIP + ':' + str(clientPort))
                    lines = [
                        'POST %s HTTP/1.1' % ('/' + 'userlist.txt'),
                        'Host: %s' % serverURL,
                        'Content-Type: %s' % 'text/*',
                        'Content-Length: %s' % len(logoutline),
                        '',
                        '%s' % logoutline
                    ]
                    logoutpost = '\r\n'.join(lines)+'\r\n\r\n'
                    s.send(logoutpost.encode()) # Sends HTTP POST to logout
                    logoutData = s.recv(2048)
                    logoutResult = logoutData.decode().split("\r\n")
                    
                    if "200" in logoutResult[0]:
                        s.close()
                        exit()
                    else:
                        print("ERROR: You are not in the list!")
                        exit()

                elif logOut.upper() != "N":
                    print("Invalid input!")
                    continue
            message = s.recv(2048).decode()
            print(message)
            count += 1
    elif "400" in result[0]: # 400 Bad Request response
        print("Invalid username character!")
        s.close()
        exit()
    elif "406" in result[0]: # 406 Not Acceptable response
        print("This user already exists!")
        s.close()
        exit()

elif mode == "send": # Send mode
    while True:
        sendCommand = input("")

        if "list" in sendCommand: # 'list' command in "send" mode
            # Updates the online users list -----
            availableUsers = []
            availableUsers = updateUsers()

            print("The online users are:")
            for user in availableUsers:
                print(user[:user.find('@')])

        elif "unicast" in sendCommand: # 'unicast <username> "message"' command in "send" mode
            msg = sendCommand.split()
            sendUser = msg[1]
            sendMessage = sendCommand[sendCommand.find('"')+1:sendCommand.rfind('"')]

            # Updates the online users list -----
            availableUsers = []
            availableUsers = updateUsers()

            # Searches for the user in the online users list
            sendAddressPort = ""
            for users in availableUsers:
                if users[:users.find('@')]  == sendUser:
                    sendAddressPort = users
                    break

            if sendAddressPort != "": # If the user is found
                sendMessageP2P(sendAddressPort, sendMessage, username)
            else:
                print("user", sendUser, "is not found")

        elif "broadcast" in sendCommand: # 'broadcast "message"' command in "send" mode
            sendMessage = sendCommand[sendCommand.find('"')+1:sendCommand.rfind('"')]

            # Updates the online users list -----
            availableUsers = []
            availableUsers = updateUsers()

            if availableUsers: #If there are some online user(s)
                for user in availableUsers:
                    sendMessageP2P(user, sendMessage, username)
            else:
                print("there is no online user")

        elif "multicast" in sendCommand: # 'multicast [user1, user2, ... userN] "message"' command in "send" mode
            userListStr = sendCommand[sendCommand.find('[')+1:sendCommand.find(']')]
            userList = [s.strip() for s in userListStr.split(',')] # Creates a list from user input
            sendMessage = sendCommand[sendCommand.find('"')+1:sendCommand.rfind('"')]

            # Updates the online users list -----
            availableUsers = []
            availableUsers = updateUsers()

            if userList:
                for sendUser in userList: # Searches for the user input list
                    flag = False
                    for avaUser in availableUsers: # Searches for the online users
                        if sendUser == avaUser[:avaUser.find('@')]:
                            flag = True
                            sendMessageP2P(avaUser, sendMessage, username)

                    if not flag:
                        print("user", sendUser, "is not found")
            else:
                print("please enter a user in []")
  
        elif "exit" in sendCommand:
            exit()
        else:
            print("Invalid command!")
        
else:
    print("Invalid mode!")
s.close()