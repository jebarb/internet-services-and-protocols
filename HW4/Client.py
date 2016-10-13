import socket
import re


class smtp:  # define regex
    # path = re.compile("^[^\s<>()[\]\.,;:@\"]+" +
    #                 "@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*\n" +
    #                 ",[^\s<>()[\]\.,;:@\"]+" +
    #                 "@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*\n$")
    path = re.compile("^[a-z]+@universalac(,[a-z]+@universalac)*$")


def process_email():  # process input and output
    userin = []
    server_port = 14615
    global input
    try:
        input = raw_input  # python 3 compatibility
    except NameError:
        pass
    userin.append(input("From: "))
    while not smtp.path.match(userin[0]):
        print("Invalid email address")
        userin[0] = input("From: ")
    userin.append(input("To: "))
    while not smtp.path.match(userin[1]):
        print("Invalid email address")
        userin[1] = input("To: ")
    userin.append(input("Subject: ") + '\n')
    userin[-1] += input("Message: ") + '\n'
    while not userin[-1] == ".\n" and not userin[-1].endswith("\n.\n"):
        userin[-1] += input() + '\n'
    recipients = userin[1].split(',')
    if recipients is None:
        recipients = userin[1]
    for address in recipients:
        global conn
        domain = address[address.index('@')+1:].strip()
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((domain, server_port))
        if not conn.recv(4096).decode().startswith("220"):
            return
        conn.send(("HELO " + domain + " please to meet you\n").encode())
        if not conn.recv(4096).decode().startswith("250"):
            return
        conn.send(("MAIL FROM: <" + userin[0] + ">\n").encode())
        if not conn.recv(4096).decode().startswith("250"):
            return
        for addr in recipients:
            conn.send(("RCPT TO: <" + addr + ">\n").encode())
            if not conn.recv(4096).decode().startswith("250"):
                return
        conn.send("DATA\n".encode())
        if not conn.recv(4096).decode().startswith("354"):
            return
        conn.send(userin[2].encode())
        if not conn.recv(4096).decode().startswith("250"):
            return

process_email()
conn.send("QUIT".encode())
conn.close()
