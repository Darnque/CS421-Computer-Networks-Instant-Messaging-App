import socket
import sys

input = sys.argv[1]

serverURL = input[:input.find(':')]
serverPort = int(input[input.find(':')+1:])

userListAppend = open("userlist.txt", "a")
userListRead = open("userlist.txt", "r")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((serverURL, serverPort))
s.listen(10)

clientPort = s.getsockname()

while True:
    clientSocket, address = s.accept()
    data = clientSocket.recv(2048)
    userListAppend = open("userlist.txt", "a")
    userListRead = open("userlist.txt", "r")

    if data:
        result = data.decode().split("\r\n")
        body = result[result.index('')+1]
        print(result)

        if "POST" in result[0] and "REGISTER" in body:
            username = body[body.find('REGISTER')+9:body.find('@')]

            found = False
            for line in userListRead.read().split():
                if line[:line.find('@')] == username:
                    found = True
                    break

            if found:
                lines = [
                    'HTTP/1.1 406 Not Acceptable'
                ]
            elif any(char in ":@ " for char in username):
                lines = [
                    'HTTP/1.1 400 Bad Request'
                ]
            else:
                userListAppend.write(body[body.find('REGISTER')+9:] + '\n')
                lines = [
                    'HTTP/1.1 200 OK'
                ]
            response = '\r\n'.join(lines)+'\r\n\r\n'
            clientSocket.send(response.encode())
        elif "GET" in result[0] and "userlist.txt" in result[0]:
            users = ""
            for line in userListRead:
                if line != '':
                    users += line.strip() + ','
                else:
                    break
            if users == '':
                listResponse = [
                    'HTTP/1.1 400 Bad Request'
                ]
            else:
                listResponse = [
                    'HTTP/1.1 200 OK',
                    '',
                    '%s' % users
                ]
            listResponse = '\r\n'.join(listResponse)+'\r\n\r\n'
            clientSocket.send(listResponse.encode())
    userListAppend.close()
    userListRead.close()
    clientSocket.close()

s.close()

userListAppend.close()
userListRead.close()