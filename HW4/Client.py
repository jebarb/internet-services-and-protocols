import socket
import re
import fileinput


conn = ""


class smtp:  # define regex
    mail_from = re.compile("^From: <[^\s<>()[\]\.,;:@\"]+" +
                           "@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*>\n$")
    rcpt_to = re.compile("^To: <[^\s<>()[\]\.,;:@\"]+" +
                         "@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*>\n$")
    message_end = re.compile("^\.\n$")
    path = re.compile("<[^\s<>()[\]\.,;:@\"]+" +
                      "@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*>\n$")


class states:      # define states
    start = 0      # initial state, accept from:
    rcpt = 1       # accept to:
    data = 2       # accept to: or data
    msg = 3        # accept data
    finish = 4     # finish email
    error = -1     # error state


def commandcheck(line):  # validate command, return state that accepts it
    if smtp.mail_from.match(line):
        return states.start
    elif smtp.rcpt_to.match(line):
        return states.rcpt
    return states.data


def statecheck(line, command, state):  # ensure state sligns with command
    if state is states.data and command is states.start:
        state = responsecheck("", sendcmd("", states.data, states.data))
        if state is states.error:
            return state
        return responsecheck("", sendcmd("", states.start, states.msg))
    return responsecheck(line, sendcmd(line, command, state))


def sendcmd(line, command, state):  # write command to stdout
    if state is states.msg:
        if command is states.start:
            conn.send(".\n".encode())
            return states.finish
        else:
            conn.send(line.encode())
        return state
    elif command is states.start and state is states.start:
        conn.send(("MAIL FROM: " + line[line.index('<'):]).encode())
    elif command is states.rcpt and state in [states.rcpt, states.data]:
        conn.send(("RCPT TO: " + line[line.index('<'):]).encode())
    elif command is states.data and state is states.data:
        conn.send(("DATA" + "\n").encode())
    else:
        return states.error
    return command


def responsecheck(line, command):  # check response against state
    if command is states.msg:
        return command
    response = conn.recv(1024).decode()
    print(response.rstrip('\n'))
    if command is states.data:
        if response.startswith("354"):
            sendcmd(line, states.msg, states.msg)
            return states.msg
    elif response.startswith("250"):
        return states.start if command is states.finish else command + 1
    return states.error


def process_email():  # process input and output
    state = states.start
    line = ""
    userin = []
    hostname = socket.gethostname()
    server_port = 14615
    global input
    try:
        input = raw_input
    except NameError:
        pass
    userin[0] = input("From: ")
    while not smtp.path.match(userin[0]):
        print("Invalid email address")
        userin[0] = input("From: ")
    userin[1] = input("To: ")
    while not smtp.path.match(userin[1]):
        print("Invalid email address")
        userin[1] = input("To: ")
    userin[2] = input("Subject: ")
    userin[3] = input("Message: ")
    while not smtp.message_end.match(userin[-1]):
        userin.append(input())
    global conn
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((hostname, server_port))
    response = conn.recv(1024).decode()
    print(response)
    if response.startswith("220"):
        conn.send("HELO " + hostname)
    else:
        return
    for line in fileinput.input():
        print(line.rstrip('\n'))
        state = statecheck(line, commandcheck(line), state)
        if state is states.start:
            state = statecheck(line, commandcheck(line), state)
        if state is states.error:
            break
    if state is states.data:
        statecheck("", states.start, states.data)
    elif state is states.msg:
        responsecheck(line, sendcmd(line, states.start, state))
    conn.send("QUIT".encode())
    conn.close()

process_email()
