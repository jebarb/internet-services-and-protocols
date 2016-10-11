import socket
import re
import sys


class smtp:  # define regex
    mail_from = re.compile("^From: <[^\s<>()[\]\.,;:@\"]+" +
                           "@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*>\n$")
    rcpt_to = re.compile("^To: <[^\s<>()[\]\.,;:@\"]+" +
                         "@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*>\n$")


class states:      # define states
    start = 0      # initial state, accept from:
    rcpt = 1       # accept to:
    data = 2       # accept to: or data
    message = 3    # accept data
    error = -1     # error state


def command_check(line):  # validate command, return state that accepts it
    if smtp.mail_from.match(line):
        return states.start
    elif smtp.rcpt_to.match(line):
        return states.rcpt
    return states.data


def state_check(line, command, state):  # ensure state sligns with command
    if state is states.message and command is states.data:
        print(line.rstrip('\n'))
        return state
    elif state is states.data and command is states.start:
        state = response_check("", send_command("", states.data, states.data))
        return state if state is states.error else\
            response_check("", send_command("", states.start, states.message))
    return response_check(line, send_command(line, command, state))


def send_command(line, command, state):  # write command to stdout
    if state is states.message:
        if command is states.start:
            print(".")
        return state
    elif command is states.start and state is states.start:
            print("MAIL FROM: " + line[line.index('<'):].rstrip('\n'))
    elif command is states.rcpt and state in [states.rcpt, states.data]:
        print("RCPT TO: " + line[line.index('<'):].rstrip('\n'))
    elif command is states.data and state is states.data:
        print("DATA")
    else:
        return states.error
    return command


def response_check(line, command):  # check response against state
    response = sys.stdin.readline()
    sys.stderr.write(response.rstrip('\n') + "\n")  # ensure one newline char
    if command is states.data:
        if response.startswith("354"):
            if not line == "":
                print(line.rstrip('\n'))
            return states.message
    elif response.startswith("250"):
        return states.start if command is states.message else command + 1
    return states.error


def process_email():  # process input and output
    state = states.start
    line = ""
    hostname = socket.gethostname()
    print(hostname)
    server_port = 14615
    print(server_port)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((hostname, server_port))
    while True:
        message = raw_input('message: ')
        client_socket.send(message.encode() + '\n')
        response = client_socket.recv(1024).decode()
        print("response: " + response)
        client_socket.close()
        '''
        state = state_check(line, command_check(line), state)
        if state is states.start:
            state = state_check(line, command_check(line), state)
        if state is states.error:
            break
    if state is states.data:
        state = response_check("", send_command("", states.data, states.data))
        if states is not states.error:
            response_check("", send_command("", states.start, states.message))
    elif state is states.message:
        response_check(line, send_command(line, states.start, state))
    print("QUIT")
'''

process_email()
