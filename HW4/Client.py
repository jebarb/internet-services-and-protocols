import socket
import re
import sys


class smtp:  # define regex
    forward_path = re.compile("^[^\s<>()[\]\.,;:@\"]+" +
                              "@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*" +
                              "(,[^\s<>()[\]\.,;:@\"]+" +
                              "@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*)*$")
    reverse_path = re.compile("^[^\s<>()[\]\.,;:@\"]+" +
                              "@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*$")
    # domain = re.compile("^[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*$")
    domain = re.compile(".*")


def process_email():  # process input and output
    if len(sys.argv) < 3:
        print("TCP port or domain absent")
        return
    if not sys.argv[2].isdigit() or not smtp.domain.match(sys.argv[1]):
        print("TCP port or domain invalid")
        return
    if int(sys.argv[2]) < 1025 or int(sys.argv[2]) > 65536:
        print("TCP port out of range")
        return
    port = int(sys.argv[2])
    domain = sys.argv[1]
    userin = []
    global input
    try:
        input = raw_input  # python 3 compatibility
    except NameError:
        pass
    userin.append(input("From: "))
    while not smtp.reverse_path.match(userin[0]):
        print("Invalid email address")
        userin[0] = input("From: ")
    userin.append(input("To: "))
    while not smtp.forward_path.match(userin[1]):
        print("Invalid email address")
        userin[1] = input("To: ")
    userin.append("From: " + userin[0] + '\n')
    userin[-1] += "To: " + userin[1] + '\n'
    userin[-1] += "Subject: " + input("Subject: ") + '\n\n'
    userin[-1] += input("Message: ") + '\n'
    while not userin[-1] == ".\n" and not userin[-1].endswith("\n.\n"):
        userin[-1] += input() + '\n'
    recipients = userin[1].split(',')
    if recipients is None:
        recipients = userin[1]
    global conn
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((domain, port))
    response = conn.recv(4096).decode()
    print(response)
    if not response.startswith("220"):
        print(response.rstrip('\n'))
        return
    conn.send(("HELO " + domain + " please to meet you\n").encode())
    response = conn.recv(4096).decode()
    print(response)
    if not response.startswith("250"):
        print(response.rstrip('\n'))
        return
    conn.send(("MAIL FROM: <" + userin[0] + ">\n").encode())
    response = conn.recv(4096).decode()
    print(response)
    if not response.startswith("250"):
        print(response.rstrip('\n'))
        return
    for addr in recipients:
        conn.send(("RCPT TO: <" + addr + ">\n").encode())
        response = conn.recv(4096).decode()
        print(response)
        if not response.startswith("250"):
            print(response.rstrip('\n'))
            return
    conn.send("DATA\n".encode())
    response = conn.recv(4096).decode()
    print(response)
    if not response.startswith("354"):
        print(response.rstrip('\n'))
        return
    conn.send(userin[2].encode())
    response = conn.recv(4096).decode()
    print(response)
    if not response.startswith("250"):
        print(response.rstrip('\n'))
        return

process_email()
conn.send("QUIT".encode())
conn.close()
